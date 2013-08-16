import datetime
import time
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.simplejson import JSONDecoder


from schedule.models.events import EventRelation
from schedule.periods import Period
from schedule.utils import encode_occurrence, decode_occurrence
from schedule.views import get_occurrence
from schedule.models.rules import Rule

from zorna.calendars.forms import EditEventForm, EditEventDetailsForm, ResourceCalendarForm, ZornaCalendarSettingsForm
from zorna.calendars.models import EventDetails, ZornaResourceCalendar
from zorna.acl.models import get_acl_for_model

from zorna.calendars.api import *


def jsondump_occurences(occurrences, user):
    occ_list = []
    for occ in occurrences:
        ed = {}
        ed['id'] = encode_occurrence(occ)
        ed['calendar_id'] = occ.calendar_id
        ed['calendar_name'] = occ.calendar_name
        if occ.start.time().__str__() == '00:00:00' and occ.end.time().__str__() == '00:00:00':
            ed['allday'] = True
        else:
            ed['allday'] = False

        ed['title'] = occ.title
        ed['start'] = occ.start.__str__()
        ed['end'] = occ.end.__str__()
        ed['description'] = "<br />".join(occ.description.split("\n"))
        if occ.manager or occ.event.creator == user:
            ed['editable'] = True
            ed['url'] = reverse(
                "edit_calendar_event") + "?id=" + encode_occurrence(occ)
        else:
            ed['url'] = ''
            ed['editable'] = False
        ed['author'] = User.objects.get(
            pk=occ.event.creator_id).get_full_name()
        ed['location'] = occ.details.location
        if occ.details.bgcolor:
            ed['backgroundColor'] = occ.details.bgcolor
        elif occ.details.category:
            ed['backgroundColor'] = occ.details.category.bgcolor
            ed['category'] = occ.details.category.name
        else:
            ed['backgroundColor'] = False
            ed['category'] = ''

        occ_list.append(ed)
    rnd = loader.get_template('calendars/occurrences_json.html')
    resp = rnd.render(Context({'occurrences': occ_list}))
    return resp


def jsondump_occurences_old(occurrences, user):
    occ_list = []
    for occ in occurrences:
        original_id = occ.id
        occ.id = encode_occurrence(occ)
        if occ.start.time().__str__() == '00:00:00' and occ.end.time().__str__() == '00:00:00':
            occ.allday = True
        else:
            occ.allday = False
        occ.start = occ.start.__str__()
        occ.end = occ.end.__str__()
        occ.recurring = bool(occ.event.rule)
        occ.persisted = bool(original_id)
        occ.description = occ.description.replace(
            '\n', '\\n')  # this can be multiline
        if occ.manager:
            occ.url = reverse("edit_calendar_event") + "?id=" + occ.id
        else:
            occ.url = ''
        occ.author = User.objects.get(pk=occ.event.creator_id).get_full_name()
        occ_list.append(occ)
    rnd = loader.get_template('calendars/occurrences_json.html')
    resp = rnd.render(Context({'occurrences': occ_list}))
    return resp


def json_events(request):
    ret = ''
    if request.user.is_authenticated():
        pcal = get_personal_calendar(request.user)
        start = request.GET['start']
        end = request.GET['end']
        allowed_objects = set([])
        perms = ['viewer', 'manager', 'creator']
        ao = {}
        for p in perms:
            ao[p] = get_user_calendars(request.user, [p])
            allowed_objects = allowed_objects.union(set(ao[p]))
        for obj in allowed_objects:
            evt = EventRelation.objects.get_events_for_object(
                obj.content_object)
            if obj.pk == pcal.pk or obj in ao['manager']:
                manager = True
            else:
                manager = False
            if obj.pk == pcal.pk or obj in ao['creator']:
                creator = True
            else:
                creator = False
            period = Period(events=evt, start=datetime.datetime.fromtimestamp(
                float(start)), end=datetime.datetime.fromtimestamp(float(end)))
            occurrences = []
            for o in period.occurrences:
                if period.classify_occurrence(o):
                    o.calendar_id = obj.pk
                    o.calendar_name = obj.calendar.name
                    if o.event.calendar_id == obj.calendar.pk:
                        o.manager = manager
                        o.creator = creator
                    else:
                        o.manager = False
                        o.creator = False
                    if o.id:
                        o.details = EventDetails.objects.get_eventdetails_for_object(
                            o)
                    else:
                        o.details = EventDetails.objects.get_eventdetails_for_object(
                            o.event)

                    if o.details.privacy == 2 and request.user != obj.owner:  # Private event
                        continue
                    else:
                        occurrences.append(o)
            if len(occurrences):
                ret += '"' + obj.calendar.slug + '": ' + \
                    jsondump_occurences(occurrences, request.user) + ','
    ret = ret[:-1]
    ret = '{' + ret + '}'
    # json_data = simplejson.dumps(ret)
    return HttpResponse(ret)


def calendar_update_event_dates(request):
    id = request.POST.get('id', None)
    start = request.POST.get('start', None)
    end = request.POST.get('end', None)
    id = request.REQUEST.get('id', None)
    try:
        all_day = JSONDecoder().decode(request.POST.get('allDay', 'null'))
    except ValueError:
        all_day = None

    start = datetime.datetime.fromtimestamp(float(start) / 1000)
    end = datetime.datetime.fromtimestamp(float(end) / 1000)

    if id:
        kwargs = decode_occurrence(id)
        event_id = kwargs.pop('event_id')
        instance_event, occurrence = get_occurrence(event_id, **kwargs)
        calendars = get_user_calendars(request.user, ['manager', 'creator'])
        if instance_event.calendar.pk not in [c.calendar_id for c in calendars]:
            return HttpResponse("error", mimetype="text/javascript", status=403)

        if all_day:
            ostart = start.strftime('%Y-%m-%d 00:00:00')
            oend = end.strftime('%Y-%m-%d 23:59:59')
        else:
            ostart = start.strftime('%Y-%m-%d %H:%M:%S')
            oend = end.strftime('%Y-%m-%d %H:%M:%S')

        if occurrence.pk:
            occurrence.start = ostart
            occurrence.end = oend
            occurrence.save()
        else:
            occurrence.title = instance_event.title
            occurrence.description = instance_event.description
            occurrence.start = ostart
            occurrence.end = oend
            occurrence.save()
            ied = EventDetails.objects.get_eventdetails_for_object(
                instance_event)
            EventDetails.objects.create_details(
                occurrence,
                location=ied.location,
                free_busy=ied.free_busy,
                privacy=ied.privacy,
                bgcolor=ied.bgcolor,
                category=ied.category,
            )
        return HttpResponse("success", mimetype="text/javascript")
    else:
        return HttpResponse("error", mimetype="text/javascript", status=400)


def view_calendar(request, calendar_id = None):
    if request.user.is_authenticated():
        allowed_objects = get_user_calendars(
            request.user, ['viewer', 'manager', 'creator'])
        if not allowed_objects:
            return HttpResponseForbidden()
        cal = get_personal_calendar(request.user)
        if cal in allowed_objects:
            cal.bshare = True
        else:
            cal.bshare = False
        extra_context = {}
        write_calendars = get_user_calendars(
            request.user, ['manager', 'creator'])
        if write_calendars:
            extra_context['bcreate'] = True
        else:
            extra_context['bcreate'] = False
        extra_context['week_start_on'] = cal.week_start_on
        extra_context['custom_view'] = cal.custom_view

        extra_context['start_date'] = int(time.mktime(
            datetime.date.today().timetuple()))
        extra_context['end_date'] = extra_context['start_date']
        extra_context['calendar'] = cal
        my_calendars = request.session.get('my_calendars', [])
        if calendar_id and int(calendar_id) in [c.pk for c in allowed_objects]:
            my_calendars = [int(calendar_id)]
        if not len(my_calendars):
            if cal in allowed_objects:
                my_calendars = [cal.pk]
            else:
                my_calendars = [allowed_objects[0].pk]
        request.session['my_calendars'] = my_calendars
        extra_context['my_calendars'] = ZornaCalendar.objects.filter(pk__in=list(set(
            my_calendars) & set([ao.pk for ao in allowed_objects]))).order_by('calendar__name')
        for cal in extra_context['my_calendars']:
            try:
                cal.description = cal.content_object.description
            except AttributeError:
                cal.description = ''
        extra_context['calendars_viewer'] = ZornaCalendar.objects.filter(
            pk__in=allowed_objects).exclude(pk__in=my_calendars).order_by('calendar__name')
        for cal in extra_context['calendars_viewer']:
            try:
                cal.description = cal.content_object.description
            except AttributeError:
                cal.description = ''
        context = RequestContext(request)
        return render_to_response('calendars/calendar.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()


def add_to_view_calendar(request, calendar):
    my_calendars = request.session.get('my_calendars', [])
    if not int(calendar) in my_calendars:
        my_calendars.append(int(calendar))
    request.session['my_calendars'] = my_calendars
    return view_calendar(request)


def remove_from_view_calendar(request, calendar):
    my_calendars = request.session.get('my_calendars', [])
    if int(calendar) in my_calendars and len(my_calendars) > 1:
        my_calendars.remove(int(calendar))
    request.session['my_calendars'] = my_calendars
    return view_calendar(request)


def create_calendar_event(request):
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    title = request.GET.get('title', None)

    initial_data = {}
    if title:
        initial_data['title'] = title

    if start:
        try:
            start = datetime.datetime.fromtimestamp(float(start))
            initial_data['start'] = start
            if end:
                initial_data[
                    'end'] = datetime.datetime.fromtimestamp(float(end))
            else:
                initial_data['end'] = start + datetime.timedelta(minutes=30)
        except TypeError:
            raise Http404
        except ValueError:
            raise Http404

    calendars = get_user_calendars(request.user, ['manager', 'creator'])
    if not calendars:
        return HttpResponseRedirect(reverse('view_calendar', args=[]))

    if request.method == 'POST':
        form = EditEventForm(data=request.POST)
        form_details = EditEventDetailsForm(data=request.POST)
        calendar_id = request.POST.get('calendar_id', None)
        if calendar_id and form.is_valid():
            calendar = get_object_or_404(ZornaCalendar, pk=calendar_id)
            if not calendar.pk in [c.pk for c in calendars]:
                # TODO Display warning message
                return HttpResponseRedirect(reverse('view_calendar', args=[]))
            event = form.save(commit=False)
            event.creator = request.user
            event.calendar = calendar.calendar
            if 'end_recurring_period' in form.cleaned_data and form.cleaned_data['end_recurring_period']:
                event.end_recurring_period = event.end_recurring_period + \
                    datetime.timedelta(days=1, seconds= -1)

            if request.POST['rule'] != '':
                params = "interval:" + request.POST['interval']
                if request.POST['rule'] == 'WEEKLY':
                    weekdays = request.POST.getlist('weekdays')
                    if not weekdays:
                        weekdays = [str((int(
                            event.start.strftime('%w')) + 6) % 7)]
                    params += ";byweekday:" + ",".join(weekdays)
                rule = Rule(name=request.POST['rule'],
                            frequency=request.POST['rule'],
                            params=params
                            )
                rule.save()
                event.rule = rule

            event.save()
            evtd = form_details.save(commit=False)
            evtd.ct = ContentType.objects.get_for_model(type(event))
            evtd.object_id = event.pk
            evtd.content_object = event
            evtd.save()
            return HttpResponseRedirect(reverse('view_calendar', args=[]))
        else:
            form = EditEventForm(data=request.POST)
            form_details = EditEventDetailsForm(data=request.POST)
    else:
        form = EditEventForm(initial=initial_data)
        form_details = EditEventDetailsForm()

    extra_context = {
        'form': form,
        'boccurrence': False,
        'event': None,
        'form_details': form_details,
        'calendars': calendars,
        'calendar': get_personal_calendar(request.user),
    }

    context = RequestContext(request)
    return render_to_response('calendars/calendar_edit.html', extra_context, context_instance=context)


def edit_calendar_simple_event(request, event_id, event, occurrence):
    instance_event_details = EventDetails.objects.get_eventdetails_for_object(
        event)
    calendars = get_user_calendars(request.user, ['manager', 'creator'])
    if event.calendar.pk not in [c.calendar_id for c in calendars]:
        return HttpResponseRedirect(reverse('view_calendar', args=[]))

    if request.method == 'POST':
        action = request.POST.get('action', None)
        if action and action == 'deleteevent':
            event.delete()
            instance_event_details.delete()
            return HttpResponseRedirect(reverse('view_calendar', args=[]))

        form = EditEventForm(data=request.POST, instance=event)
        form_details = EditEventDetailsForm(
            data=request.POST, instance=instance_event_details)
        if form.is_valid():
            calendar = get_object_or_404(
                ZornaCalendar, pk=request.POST['calendar_id'])
            event = form.save(commit=False)
            event.calendar = calendar.calendar
            if 'end_recurring_period' in form.cleaned_data and form.cleaned_data['end_recurring_period']:
                event.end_recurring_period = event.end_recurring_period + \
                    datetime.timedelta(days=1, seconds= -1)
            if request.POST['rule'] != '':
                params = "interval:" + request.POST['interval']
                if request.POST['rule'] == 'WEEKLY':
                    wl = request.POST.getlist('weekdays')
                    if not wl:
                        wl = [str((int(event.start.strftime('%w')) + 6) % 7)]
                    if wl:
                        params += ";byweekday:" + ",".join(wl)
                rule = Rule(
                    name=request.POST['rule'],
                    frequency=request.POST['rule'],
                    params=params
                )
                rule.save()
                event.rule = rule
            event.save()
            form_details.save()
            return HttpResponseRedirect(reverse('view_calendar', args=[]))
        else:
            form = EditEventForm(data=request.POST)
            form_details = EditEventDetailsForm(data=request.POST)
    else:
        form = EditEventForm(instance=event)
        form_details = EditEventDetailsForm(instance=instance_event_details)

    extra_context = {
        'form': form,
        'boccurrence': False,
        'event': event,
        'form_details': form_details,
        'calendars': calendars,
        'calendar': ZornaCalendar.objects.get(calendar=event.calendar)
    }

    context = RequestContext(request)
    return render_to_response('calendars/calendar_edit.html', extra_context, context_instance=context)


def edit_calendar_reccurrent_event(request, event_id, event, occurrence):
    instance_event_details = EventDetails.objects.get_eventdetails_for_object(
        event)
    calendars = get_user_calendars(request.user, ['manager', 'creator'])
    if event.calendar.pk not in [c.calendar_id for c in calendars]:
        return HttpResponseRedirect(reverse('view_calendar', args=[]))
    original_start = event.start
    params = event.rule.get_params()
    initial_data = {}
    initial_data['rule'] = event.rule.frequency
    if 'interval' in params:
        initial_data['interval'] = params['interval']
    if 'byweekday' in params:
        initial_data['weekdays'] = params['byweekday'] if type(params[
                                                               'byweekday']) == type(list()) else [params['byweekday']]
    initial_data['start'] = occurrence.start
    initial_data['end'] = occurrence.end
    initial_data['title'] = occurrence.title
    initial_data['description'] = occurrence.description

    if request.method == 'POST':
        form = EditEventForm(data=request.POST, instance=event)
        form_details = EditEventDetailsForm(
            data=request.POST, instance=instance_event_details)

        action = request.POST.get('action', None)
        if action and action == 'deleteone':
            occurrence.cancel()
            return HttpResponseRedirect(reverse('view_calendar', args=[]))

        if action and action == 'deleteall':
            persisted_occurrences = event.occurrence_set.all()
            for occ in persisted_occurrences:
                try:
                    EventDetails.objects.get_eventdetails_for_object(
                        occ).delete()
                except:
                    pass
            event.rule.delete()
            event.delete()
            instance_event_details.delete()
            return HttpResponseRedirect(reverse('view_calendar', args=[]))

        if action and action == 'updateevent' and form.is_valid():  # update only this occurrence
            occurrence.title = form.cleaned_data['title']
            occurrence.description = form.cleaned_data['description']
            occurrence.start = form.cleaned_data[
                'start'].strftime('%Y-%m-%d %H:%M:%S')
            occurrence.end = form.cleaned_data[
                'end'].strftime('%Y-%m-%d %H:%M:%S')
            occurrence.save()
            EventDetails.objects.create_details(
                occurrence,
                request.POST.get('location', ''),
                request.POST.get('free_busy', 0),
                request.POST.get('privacy', 0),
            )
            return HttpResponseRedirect(reverse('view_calendar', args=[]))

        if form.is_valid():
            calendar = get_object_or_404(
                ZornaCalendar, pk=request.POST['calendar_id'])
            evt = form.save(commit=False)
            evt.calendar = calendar.calendar
            if 'end_recurring_period' in form.cleaned_data and form.cleaned_data['end_recurring_period']:
                evt.end_recurring_period = evt.end_recurring_period + \
                    datetime.timedelta(days=1, seconds= -1)
            rule = event.rule
            if rule and request.POST['rule'] == '':
                persisted_occurrences = event.occurrence_set.all()
                for occ in persisted_occurrences:
                    try:
                        EventDetails.objects.get_eventdetails_for_object(
                            occ).delete()
                    except:
                        pass
                event.rule = None
                rule.delete()

            if request.POST['rule'] != '':
                params = "interval:" + request.POST['interval']
                if request.POST['rule'] == 'WEEKLY':
                    wl = request.POST.getlist('weekdays')
                    if not wl:
                        wl = [str((int(evt.start.strftime('%w')) + 6) % 7)]
                    if wl:
                        params += ";byweekday:" + ",".join(wl)
                if evt.rule:
                    evt.rule.name = request.POST['rule']
                    evt.rule.frequency = request.POST['rule']
                    evt.rule.params = params
                    evt.rule.save()
                else:
                    rule = Rule(name=request.POST['rule'],
                                frequency=request.POST['rule'],
                                params=params
                                )
                    rule.save()
                    evt.rule = rule
            if occurrence.start.date() == evt.start.date():
                td = evt.end.date() - evt.start.date()
                evt.start = datetime.datetime.combine(
                    original_start.date(), evt.start.time())
                evt.end = datetime.datetime.combine(
                    original_start.date() + td, evt.end.time())
            evt.save()
            form_details.save()
            return HttpResponseRedirect(reverse('view_calendar', args=[]))
        else:
            form = EditEventForm(data=request.POST)
            form_details = EditEventDetailsForm(data=request.POST)
    else:
        form = EditEventForm(instance=event, initial=initial_data)
        form_details = EditEventDetailsForm(instance=instance_event_details)

    extra_context = {
        'form': form,
        'boccurrence': False,
        'event': event,
        'form_details': form_details,
        'calendars': calendars,
        'calendar': ZornaCalendar.objects.get(calendar=event.calendar)
    }

    context = RequestContext(request)
    return render_to_response('calendars/calendar_edit.html', extra_context, context_instance=context)


def edit_calendar_occurrence(request, event_id, event, occurrence):
    instance_event_details = EventDetails.objects.get_eventdetails_for_object(
        occurrence)
    calendars = get_user_calendars(request.user, ['manager', 'creator'])
    if event.calendar.pk not in [c.calendar_id for c in calendars]:
        return HttpResponseRedirect(reverse('view_calendar', args=[]))
    initial_data = {}
    initial_data['start'] = occurrence.start
    initial_data['end'] = occurrence.end
    initial_data['title'] = occurrence.title
    initial_data['description'] = occurrence.description

    if request.method == 'POST':
        form = EditEventForm(data=request.POST, instance=event)
        form_details = EditEventDetailsForm(
            data=request.POST, instance=instance_event_details)

        action = request.POST.get('action', None)
        if action and action == 'deleteevent':
            occurrence.cancel()
            return HttpResponseRedirect(reverse('view_calendar', args=[]))

        if form.is_valid():
            occurrence.title = form.cleaned_data['title']
            occurrence.description = form.cleaned_data['description']
            occurrence.start = form.cleaned_data[
                'start'].strftime('%Y-%m-%d %H:%M:%S')
            occurrence.end = form.cleaned_data[
                'end'].strftime('%Y-%m-%d %H:%M:%S')
            occurrence.save()
            form_details.save()
            return HttpResponseRedirect(reverse('view_calendar', args=[]))
        else:
            form = EditEventForm(data=request.POST)
            form_details = EditEventDetailsForm(data=request.POST)
    else:
        form = EditEventForm(instance=event, initial=initial_data)
        form_details = EditEventDetailsForm(instance=instance_event_details)

    extra_context = {
        'form': form,
        'boccurrence': True,
        'event': event,
        'form_details': form_details,
        'calendars': calendars,
        'calendar': ZornaCalendar.objects.get(calendar=event.calendar)
    }

    context = RequestContext(request)
    return render_to_response('calendars/calendar_edit.html', extra_context, context_instance=context)


def edit_calendar_event(request):

    id = request.REQUEST.get('id', None)
    if id:
        kwargs = decode_occurrence(id)
        event_id = kwargs.pop('event_id')
        instance_event, occurrence = get_occurrence(event_id, **kwargs)
    else:
        return HttpResponseRedirect('/')

    if occurrence.pk:
        return edit_calendar_occurrence(request, event_id, instance_event, occurrence)
    else:
        if instance_event.rule is None:
            return edit_calendar_simple_event(request, event_id, instance_event, occurrence)
        else:
            return edit_calendar_reccurrent_event(request, event_id, instance_event, occurrence)


@login_required()
def calendar_share(request):
    if request.user.is_authenticated():
        cal = get_personal_calendar(request.user)
        check = get_acl_for_model(cal)
        extra_context = check.get_acl_users_forms(
            request, cal.pk, template=None)
        context = RequestContext(request)
        return render_to_response('calendars/calendar_share.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()


@login_required()
def calendar_user_settings(request):
    if request.user.is_authenticated():
        cal = get_personal_calendar(request.user)
        if request.method == 'POST':
            form = ZornaCalendarSettingsForm(request.POST, instance=cal)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('view_calendar'))
            else:
                form = ZornaCalendarSettingsForm(request.POST, instance=cal)
        else:
            form = ZornaCalendarSettingsForm(instance=cal)

        context = RequestContext(request)
        extra_context = {'form': form, 'calendar': cal}
        return render_to_response('calendars/calendar_settings.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')


@login_required()
def calendar_settings_shared_url(request):
    if request.user.is_authenticated():
        allowed_objects = get_user_calendars(request.user, ['manager'])
        extra_context = {}
        extra_context['calendars'] = ZornaCalendar.objects.select_related(
            depth=1).filter(pk__in=allowed_objects)
        for cal in extra_context['calendars']:
            cal.zorna_url = request.build_absolute_uri(reverse(
                'calendar_ical', args=[cal.calendar.slug, cal.secret_key]))
        context = RequestContext(request)
        return render_to_response('calendars/calendar_settings_url.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()


@login_required()
def calendar_reset_secret_key(request, calendar):
    if request.user.is_authenticated():
        try:
            calendar = ZornaCalendar.objects.get(pk=calendar)
        except:
            return HttpResponseForbidden()
        calendars = get_user_calendars(request.user, ['manager'])
        if not calendar in calendars:
            return HttpResponseForbidden()
        calendar.reset_secret_key()
        calendar.save()
        return HttpResponseRedirect(reverse('calendar_settings_shared_url'))
    else:
        return HttpResponseForbidden()


@login_required()
def admin_list_calendars(request):
    if request.user.is_superuser:
        ob_list = ZornaResourceCalendar.objects.all()
        extra_context = {}
        extra_context['calendars_list'] = ob_list
        context = RequestContext(request)
        return render_to_response('calendars/list_calendars.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')


@login_required()
def admin_acl_calendar(request, resource_calendar):
    if request.user.is_superuser:
        c = ZornaResourceCalendar.objects.get(pk=resource_calendar)
        calendar = get_resource_calendar(c)
        ct = ContentType.objects.get_for_model(type(calendar))
        return HttpResponseRedirect(reverse('acl_groups_object',
                                            args=[ct.pk, calendar.pk]) + '?next=%s' % reverse('admin_list_calendars'))
    else:
        return HttpResponseRedirect('/')


@login_required()
def admin_add_calendar(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = ResourceCalendarForm(request.POST)
            if form.is_valid():
                rcalendar = form.save(commit=False)
                rcalendar.owner = rcalendar.modifier = request.user
                rcalendar.save()
                get_resource_calendar(rcalendar)
                return HttpResponseRedirect(reverse('admin_list_calendars'))
            else:
                form = ResourceCalendarForm(request.POST)
        else:
            form = ResourceCalendarForm()

        context = RequestContext(request)
        extra_context = {'form': form, 'resource_calendar': None}
        return render_to_response('calendars/edit_calendar.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')


@login_required()
def admin_edit_calendar(request, resource_calendar):
    if request.user.is_superuser:
        c = ZornaResourceCalendar.objects.get(pk=resource_calendar)
        c.calendar = get_resource_calendar(c)
        if request.method == 'POST':
            form = ResourceCalendarForm(request.POST, instance=c)
            if form.is_valid():
                rcalendar = form.save(commit=False)
                rcalendar.modifier = request.user
                rcalendar.save()
                c.calendar.rename(form.cleaned_data['name'])
                return HttpResponseRedirect(reverse('admin_list_calendars'))
        else:
            form = ResourceCalendarForm(
                instance=c, initial={'slug': c.calendar.calendar.slug})

        context = RequestContext(request)
        extra_context = {'form': form, 'resource_calendar': c}
        return render_to_response('calendars/edit_calendar.html', extra_context, context_instance=context)
    else:
        return HttpResponseRedirect('/')
