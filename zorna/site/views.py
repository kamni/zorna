from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from zorna.site.models import SiteAlert, SiteOptions, SiteRegistration
from zorna.site.forms import SiteAlertAdminAddForm, ZornaCalendarCategoryForm, SiteRegistrationForm
from zorna.calendars.models import ZornaCalendarCategory
from zorna.site.signals import site_options_called
from zorna.account.models import UserGroup
from zorna import defines


def admin_list_options(request):
    if request.user.is_superuser:
        site_options_called.send(None)
        ob_list = SiteOptions.objects.all()
        extra_context = {}
        extra_context['opt_list'] = ob_list
        context = RequestContext(request)
        return render_to_response('site/list_options.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()


def admin_site_version(request):
    if request.user.is_superuser:
        from zorna import get_version
        import django
        import sys
        from django.views import debug
        extra_context = {}
        extra_context['zorna_version'] = get_version()
        extra_context['django_version'] = django.get_version()
        extra_context['python_version'] = sys.version
        extra_context['settings'] = debug.get_safe_settings()
        context = RequestContext(request)
        return render_to_response('site/version.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()


def admin_site_registration(request):
    if request.user.is_superuser:
        try:
            instance = SiteRegistration.objects.get(
                site=Site.objects.get_current())
        except SiteRegistration.DoesNotExist:
            instance = None
        if request.method == 'POST':
            form = SiteRegistrationForm(request.POST, instance=instance)
            if form.is_valid():
                reg = form.save(commit=False)
                reg.owner = request.user
                reg.modifier = request.user
                reg.save()
                reg.groups.clear()
                selected_groups = request.POST.getlist('_selected_action')
                reg.groups = selected_groups
                return HttpResponseRedirect(reverse('admin_list_alerts'))
            else:
                form = SiteRegistrationForm(request.POST, instance=instance)
        else:
            form = SiteRegistrationForm(instance=instance)

        group_lists = UserGroup.objects.filter(
            id__gt=defines.ZORNA_GROUP_REGISTERED).order_by('lft')
        context = RequestContext(request)
        if instance:
            reg_groups = instance.groups.all()
        else:
            reg_groups = UserGroup.objects.none()
        extra_context = {'form':
                         form, 'groups_list': group_lists, 'reg_groups': reg_groups}
        return render_to_response('site/site_registration.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()


def admin_list_alerts(request):
    if request.user.is_superuser:
        ob_list = SiteAlert.objects.all()
        extra_context = {}
        extra_context['alert_list'] = ob_list
        context = RequestContext(request)
        return render_to_response('site/list_alerts.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()


def admin_add_alert(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = SiteAlertAdminAddForm(request.POST)
            if form.is_valid():
                alert = form.save(commit=False)
                alert.owner = request.user
                alert.modifier = request.user
                form.save()
                return HttpResponseRedirect(reverse('admin_list_alerts'))
            else:
                form = SiteAlertAdminAddForm(request.POST)
        else:
            form = SiteAlertAdminAddForm()

        context = RequestContext(request)
        extra_context = {'form': form, 'curalert': None}
        return render_to_response('site/edit_alert.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()


def admin_edit_alert(request, alert):
    if request.user.is_superuser:
        alert = SiteAlert.objects.get(pk=alert)
        if request.method == 'POST':
            if 'bdelete' in request.POST:
                alert.delete()
                return HttpResponseRedirect(reverse('admin_list_alerts'))
            form = SiteAlertAdminAddForm(request.POST, instance=alert)
            if form.is_valid():
                alert = form.save(commit=False)
                alert.modifier = request.user
                alert.save()
                return HttpResponseRedirect(reverse('admin_list_alerts'))
            else:
                form = SiteAlertAdminAddForm(request.POST, instance=alert)
        else:
            form = SiteAlertAdminAddForm(instance=alert)

        context = RequestContext(request)
        extra_context = {'form': form, 'curalert': alert}
        return render_to_response('site/edit_alert.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()


def admin_list_calendar_categories(request):
    if request.user.is_superuser:
        ob_list = ZornaCalendarCategory.objects.all()
        extra_context = {}
        extra_context['categories'] = ob_list
        context = RequestContext(request)
        return render_to_response('site/list_calendar_categories.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()


def admin_add_calendar_category(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            form = ZornaCalendarCategoryForm(request.POST)
            if form.is_valid():
                category = form.save(commit=False)
                category.owner = request.user
                category.modifier = request.user
                form.save()
                return HttpResponseRedirect(reverse('admin_list_calendar_categories'))
            else:
                form = ZornaCalendarCategoryForm(request.POST)
        else:
            form = ZornaCalendarCategoryForm()

        context = RequestContext(request)
        extra_context = {'form': form, 'curcategory': None}
        return render_to_response('site/edit_calendar_category.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()


def admin_edit_calendar_category(request, category):
    if request.user.is_superuser:
        category = ZornaCalendarCategory.objects.get(pk=category)
        if request.method == 'POST':
            if 'bdelete' in request.POST:
                category.delete()
                return HttpResponseRedirect(reverse('admin_list_calendar_categories'))
            form = ZornaCalendarCategoryForm(request.POST, instance=category)
            if form.is_valid():
                category = form.save(commit=False)
                category.modifier = request.user
                category.save()
                return HttpResponseRedirect(reverse('admin_list_calendar_categories'))
            else:
                form = ZornaCalendarCategoryForm(
                    request.POST, instance=category)
        else:
            form = ZornaCalendarCategoryForm(instance=category)

        context = RequestContext(request)
        extra_context = {'form': form, 'curcategory': category}
        return render_to_response('site/edit_calendar_category.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()
