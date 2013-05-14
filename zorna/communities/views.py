# Create your views here.
#import importlib
import sys
import urllib2
import os,mimetypes
from django.utils import simplejson
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from django.template import RequestContext, loader, TemplateDoesNotExist
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.http import HttpResponse
from django.views.generic.list_detail import object_list
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import mail
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.template.loader import render_to_string

from zorna import defines
from zorna.acl.models import ACLPermission, get_acl_users_by_object
from zorna.site.email import ZornaEmail

from zorna.communities.models import EventCommunity, PollCommunity, PollCommunityChoice, UrlCommunity
from zorna.communities.forms import CommunityAdminAddForm, MessageCommunityForm, EventCommunityForm, InviteCommunityForm, PollCommunityForm,PollCommunityChoiceForm, UrlCommunityForm, EMBEDLY_RE
from zorna.utilit import get_upload_communities
from zorna.forms.forms import comforms_community, FormsForm
from zorna.communities.api import * 
from zorna.forms.api import forms_get_entries

NB_MESSAGES_BY_PAGE=10
NB_COMMUNITIES_BY_PAGE=15

def CommunityPopupHttpResponseError(request, error):
    context = RequestContext(request)
    return render_to_response('communities/popup_error.html', {'title': _(u'Error'), 'error':error}, context_instance=context)


def get_community_addons_instance(request, community_id=0, all=True):
    return CommunityAddons(request, community_id, all)

class zornapoll_community(ZornaCommunityAddons):
    
    def get_title(self, id):
        return _(u'Poll')

    def get_content_type(self, id):
        ct = ContentType.objects.get_for_model(PollCommunity)
        return ct
    
    def get_content_types(self):
        ct = ContentType.objects.get_for_model(PollCommunity)
        return [ct]

    def get_content_type_id(self, id):
        ct = ContentType.objects.get_by_natural_key('communities', 'pollcommunity')
        return ct.pk

    def get_css_file(self, id):
        #return '/skins/%s/css/event.css' % settings.ZORNA_SKIN
        return None

    def get_message(self, id):
        return None

    def get_tabs(self, request, community_id=0):
        ao = get_allowed_objects(request.user, Community, 'manage')
        if len(ao):
            return [ 'poll' ]
        else:
            return []

    def get_communities(self, request, id):
        return get_allowed_objects(request.user, Community, 'manage')
    
    def get_users(self, request, id):
        return []

    def get_menus(self, request, community_id=0):
        id = 'zornapoll_poll_menu'
        return [ {'title': _(u'Polls'), 'url': reverse('communities_home_plugin', args=(id,)), 'id': id, 'css_icon': 'polls'} ]

    def get_page_title(self, request, id):
        return _(u'Polls')

    def render_form_by_id(self, request, id, post=False):
        if id == 'poll':
            form = self.get_form(request, id, post)
            return self.render_form(request, form)
        else:
            return ''

    def render_form(self, request, form):
        try:
            if not form.instance.pk:
                t = loader.get_template("communities/poll_form.html")
            else:
                t = loader.get_template("communities/poll_edit_form.html")
                
            c = RequestContext(request, {'form_extra': form})
            return t.render(c)
        except:
            return ''
        
    def get_form(self, request, id, post=False, instance_id=None):
        if instance_id:
            try:
                instance = PollCommunity.objects.get(pk=instance_id)
            except PollCommunity.DoesNotExist:
                instance = None
        else:
            instance = None
            
        if post:
            choice_form_set = modelformset_factory(PollCommunityChoice, form=PollCommunityChoiceForm, extra=2)
            if instance:
                #don't let user update poll questions
                poll_form_set = choice_form_set(queryset=instance.pollcommunitychoice_set.all())
            else:
                poll_form_set = choice_form_set(request.POST)
            k = poll_form_set.total_form_count()
            if k == 0:
                #call again choice_form_set without otherwise the form displayed without add link
                poll_form_set = choice_form_set(queryset=PollCommunityChoice.objects.none())
            form_poll = PollCommunityForm(poll_form_set, request.POST, instance=instance)
        else:
            if instance:
                choice_form_set = modelformset_factory(PollCommunityChoice, form=PollCommunityChoiceForm, extra=2)
                poll_form_set = choice_form_set(queryset=PollCommunityChoice.objects.none())
                form_poll = PollCommunityForm(poll_form_set, instance=instance)
            else:
                choice_form_set = modelformset_factory(PollCommunityChoice, form=PollCommunityChoiceForm, extra=2)
                poll_form_set = choice_form_set(queryset=PollCommunityChoice.objects.none())
                form_poll= PollCommunityForm(poll_form_set)
        return form_poll
    
    def save(self, request, id, form_poll, message=None):
        poll = form_poll.save()
        for i in range(0, form_poll.poll_form_set.total_form_count()):
            form = form_poll.poll_form_set.forms[i]
            try:
                value = form.cleaned_data['choice']
                if value:
                    choice = PollCommunityChoice(choice = form.cleaned_data['choice'])
                    choice.question = poll
                    choice.save()
            except:
                pass
        return poll
    
    def render_message(self, request, poll):
        t = loader.get_template('communities/poll_view.html')
        c = RequestContext(request, {'url_frame': reverse('communities_poll_vote', args=(poll.pk,)), 'poll': poll})
        return t.render(c)
    
    def render_widget(self, request, id, community_id=0):
        return '',''

    def render_page(self, request, id, context={}):
        ct = ContentType.objects.get_for_model(PollCommunity)
        #m = MessageCommunityExtra.objects.select_related().filter(content_type = ct).order_by('-message_time_updated')
        community_id = context.get('community_id', 0)
        messages = get_messages_extra_by_content_type(request, ct, community_id)
        extra = {}
        for m in messages:
            extra[m.object_id] = m
        q = context.get('search_string', None)
        if q:    
            polls = PollCommunity.objects.filter(Q(question__icontains=q) | Q(pollcommunitychoice__choice__icontains=q), pk__in=extra.keys(), ).distinct()
        else:
            polls = PollCommunity.objects.filter(pk__in=extra.keys())
        q = []
        for p in polls:
            p.message = extra[p.pk].message
            q.append({'html': self.render_message(request, p), 'message': extra[p.pk].message, 'id': p.pk})
        return q
        
def communities_poll_vote(request, poll):
    try:
        poll = PollCommunity.objects.get(pk=poll)
    except PollCommunity.DoesNotExist:
        return HttpResponse('')

    if request.method == 'POST':
        answer = request.POST.get("answer", 0)
        if answer:
            choice = poll.pollcommunitychoice_set.get(pk=int(answer))
            choice.user.add(request.user)

    extra_context = {'poll': poll}
    if poll.pollcommunitychoice_set.filter(user=request.user).count() == 0:
        template = 'communities/poll_vote.html'
    else:
        extra_context['query'] = poll.pollcommunitychoice_set.values("choice").annotate(count=Count("user__pk"))
        extra_context['total_votes'] = 0
        for q in extra_context['query']:
            extra_context['total_votes'] += q['count']
        template = 'communities/poll_results.html'
    
    context = RequestContext(request)
    return render_to_response(template, extra_context, context_instance=context)    

class zornaevent_community(ZornaCommunityAddons):
    
    def get_title(self, id):
        return _(u'Event')

    def get_content_type(self, id):
        ct = ContentType.objects.get_for_model(EventCommunity)
        return ct
    
    def get_content_types(self):
        ct = ContentType.objects.get_for_model(EventCommunity)
        return [ct]

    def get_content_type_id(self, id):
        ct = ContentType.objects.get_by_natural_key('communities', 'eventcommunity')
        return ct.pk

    def get_css_file(self, id):
        #return '/skins/%s/css/event.css' % settings.ZORNA_SKIN
        return None

    def get_message(self, id):
        return None

    def get_communities(self, request, id):
        return get_allowed_objects(request.user, Community, 'manage')
    
    def get_users(self, request, id):
        return []

    def get_tabs(self, request, community_id=0):
        ao = get_allowed_objects(request.user, Community, 'manage')
        if len(ao):
            return [ 'event' ]
        else:
            return []        

    def get_menus(self, request, community_id=0):
        id = 'zornaevent_event_menu'
        return [ {'title': _(u'Events'), 'url': reverse('communities_home_plugin', args=(id,)), 'id': id, 'css_icon': 'events'} ]

    def get_page_title(self, request, id):
        return _(u'Events')


    def render_form_by_id(self, request, id, post=False):
        if id == 'event':
            form = self.get_form(request, id, post)
            return self.render_form(request, form)
        else:
            return ''

    def render_form(self, request, form):
        try:
            t = loader.get_template("communities/event_form.html")
            c = RequestContext(request, {'form_extra': form})
            return t.render(c)
        except:
            return ''
        
    def get_form(self, request, id, post=False, instance_id=None):
        if instance_id:
            try:
                instance = EventCommunity.objects.get(pk=instance_id)
            except EventCommunity.DoesNotExist:
                instance = None
        else:
            instance = None
            
        if post:
            form = EventCommunityForm(request.POST, instance=instance)
        else:
            if instance:
                id = {'title': instance.event.title, 'start': instance.event.start, 'end': instance.event.end}
                form = EventCommunityForm(instance = instance, initial=id)
            else:
                form = EventCommunityForm(instance = instance)
                
        return form
    
    def save(self, request, id, form, message=None):
        return form.save(request=request, message=message)
    
    def render_message(self, request, assignment):
        t = loader.get_template('communities/event_view.html')
        c = RequestContext(request, {'msg':assignment})
        return t.render(c)
    
    def render_widget(self, request, id, community_id=0):
        ct = ContentType.objects.get_for_model(EventCommunity)
        #m = MessageCommunityExtra.objects.select_related().filter(content_type = ct).order_by('-message_time_updated')
        messages = get_messages_extra_by_content_type(request, ct, community_id)
        messages = messages.order_by('-message__time_updated')
        extra = {}
        for m in messages:
            extra[m.object_id] = m
                    
        m = EventCommunity.objects.filter(pk__in=extra.keys()).order_by('event__start')[0:10]
        for c in m:
            c.message = extra[c.pk].message
        
        if len(m):
            t = loader.get_template('communities/event_widget.html')
            c = RequestContext(request, {'assignements':m})
            return _(u'Events'), t.render(c)
        else:
            return '',''

    def render_page(self, request, id, context={}):
        ct = ContentType.objects.get_for_model(EventCommunity)
        #m = MessageCommunityExtra.objects.select_related().filter(content_type = ct).order_by('-message_time_updated')
        community_id = context.get('community_id', 0)
        messages = get_messages_extra_by_content_type(request, ct, community_id)
        extra = {}
        for m in messages:
            extra[m.object_id] = m
        q = context.get('search_string', None)
        if q:    
            messages = EventCommunity.objects.filter(Q(event__title__icontains=q) | Q(event__description__icontains=q), pk__in=extra.keys(), )
        else:
            messages = EventCommunity.objects.filter(pk__in=extra.keys())
        messages = messages.order_by('event__start')
        t = loader.get_template('communities/event_view.html')
        q = []
        for m in messages:
            m.message = extra[m.pk].message
            c = RequestContext(request, {'msg':m})
            q.append({'html': t.render(c), 'message': extra[m.pk].message, 'id': m.pk})
        return q


class zornaurl_community(ZornaCommunityAddons):
    
    def get_title(self, id):
        return _(u'Link')

    def get_content_type(self, id):
        ct = ContentType.objects.get_for_model(UrlCommunity)
        return ct
    
    def get_content_types(self):
        ct = ContentType.objects.get_for_model(UrlCommunity)
        return [ct]

    def get_content_type_id(self, id):
        ct = ContentType.objects.get_by_natural_key('communities', 'urlcommunity')
        return ct.pk

    def get_css_file(self, id):
        #return '/skins/%s/css/event.css' % settings.ZORNA_SKIN
        return None

    def get_message(self, id):
        return None

    def get_communities(self, request, id):
        return get_allowed_objects(request.user, Community, 'manage')
    
    def get_users(self, request, id):
        return []

    def get_tabs(self, request, community_id=0):
        ao = get_allowed_objects(request.user, Community, 'manage')
        if len(ao):
            return [ 'link' ]
        else:
            return []        

    def get_menus(self, request, community_id=0):
        id = 'zornaurl_url_menu'
        return [ {'title': _(u'Links'), 'url': reverse('communities_home_plugin', args=(id,)), 'id': id, 'css_icon': 'links'} ]

    def get_page_title(self, request, id):
        return _(u'Links')


    def render_form_by_id(self, request, id, post=False):
        if id == 'url':
            form = self.get_form(request, id, post)
            return self.render_form(request, form)
        else:
            return ''

    def render_form(self, request, form):
        try:
            t = loader.get_template("communities/url_form.html")
            c = RequestContext(request, {'form_extra': form})
            return t.render(c)
        except:
            return ''
        
    def get_form(self, request, id, post=False, instance_id=None):
        if instance_id:
            try:
                instance = UrlCommunity.objects.get(pk=instance_id)
            except EventCommunity.DoesNotExist:
                instance = None
        else:
            instance = None
            
        if post:
            form = UrlCommunityForm(request.POST, instance=instance)
        else:
            if instance:
                form = UrlCommunityForm(instance = instance)
            else:
                form = UrlCommunityForm(instance = instance)
                
        return form
    
    def save(self, request, id, form, message=None):
        return form.save(request=request, message=message)
    
    def render_message(self, request, extra):
        t = loader.get_template('communities/url_view.html')
        context = {}
        context['title'] = extra.title
        context['description'] = extra.excerpt
        context['url'] = extra.url
        if settings.EMBEDLY_KEY and EMBEDLY_RE.search(extra.url):
            api_url = 'http://api.embed.ly/1/oembed?'
            #max_width = settings.EMBEDLY_MAX_WIDTH if settings.EMBEDLY_MAX_WIDTH else 500
            params = {'url': extra.url , 'key': settings.EMBEDLY_KEY, 'maxwidth': 500 }
            oembed_call = "%s%s" % (api_url, urllib.urlencode(params))
            try:
                embedly_info = simplejson.loads(urllib2.urlopen(oembed_call).read())
                context['description'] = embedly_info['description']
                context['title'] = embedly_info['title']
            except Exception as e:
                embedly_info = False
        else:
            embedly_info = False
        c = RequestContext(request, {'msg':context, 'embedly_info':embedly_info})        
        return t.render(c)
    
    def render_widget(self, request, id, community_id=0):
        return '',''

    def render_page(self, request, id, context={}):
        ct = ContentType.objects.get_for_model(UrlCommunity)
        #m = MessageCommunityExtra.objects.select_related().filter(content_type = ct).order_by('-message_time_updated')
        community_id = context.get('community_id', 0)
        messages = get_messages_extra_by_content_type(request, ct, community_id)
        extra = {}
        for m in messages:
            extra[m.object_id] = m
        q = context.get('search_string', None)
        if q:    
            messages = UrlCommunity.objects.filter(Q(title__icontains=q) | Q(excerpt__icontains=q), pk__in=extra.keys(), )
        else:
            messages = UrlCommunity.objects.filter(pk__in=extra.keys())
        messages = messages.order_by('-time_created')
        t = loader.get_template('communities/url_view.html')
        q = []
        for m in messages:
            m.message = extra[m.pk].message
            q.append({'html': self.render_message(request, m), 'message': extra[m.pk].message, 'id': m.pk})
        return q

class CommunityAddons(object):
    plugins = {}
    content_types = {}
    _populated = False
    
    def __init__(self, request, community_id=0, all=False):
        self.id_by_content_type = {}
        self.request = request
        self.community_id = community_id
        if all and not CommunityAddons._populated :
            self.register_addon(zornaurl_community())
            self.register_addon(zornaevent_community())
            self.register_addon(zornapoll_community())
            try:
                if settings.ZORNA_COMMUNITY_FORMS:
                    self.register_addon(comforms_community(request))
            except:
                pass
            self.get_instances()
        self.tabs = {}
        self.plugins_menus = []
        self.plugins_tabs = []
        for p in CommunityAddons.plugins.values():
            tabs = p.get_tabs(request, community_id);
            for t in tabs:
                tab = self.format_tab(p, t)
                self.plugins_tabs.append(tab)
                self.tabs[tab['id']] = p
            self.plugins_menus.extend(p.get_menus(request, community_id))

    def register_addon(self, instance):
        app = instance.__class__.__name__.split('_')[0]
        CommunityAddons.plugins[app] = instance
        cts = instance.get_content_types()
        for ct in cts:
            CommunityAddons.content_types[ct.pk] = instance

    def get_tab_id(self, instance, tab):
        app = instance.__class__.__name__.split('_')[0]
        ct = instance.get_content_type(tab)
        return '%s_%s_%s_%s_tab' % (app, ct.app_label, ct.model, tab)

    def format_tab(self, instance, tab):
        ct = instance.get_content_type(tab)
        id = self.get_tab_id(instance, tab)
        self.id_by_content_type[ct.pk] = id
        return {'id': id, 'title':instance.get_title(tab), 'css_file': instance.get_css_file(tab)}
            
    def load_app(self, app):
        try:
            __import__('zorna_plugins.%s.zorna_community' % app )
            b = sys.modules['zorna_plugins.%s.zorna_community' % app]
            obj = getattr(b, '%s_community' % app)
            self.register_addon(obj())
        except:
            pass

    def get_instances(self):
        if CommunityAddons._populated == True:
            return CommunityAddons.plugins.values()
        else:
            CommunityAddons._populated = True
            plugins_path = os.path.join(settings.PROJECT_PATH, 'zorna_plugins')
            for app in os.listdir(plugins_path):
                app_path = os.path.join(plugins_path,app)
                if os.path.isdir(app_path) and not CommunityAddons.plugins.has_key(app):
                    self.load_app(app)
            return CommunityAddons.plugins.values()
        
    def get_instance_by_name(self, name):
        try:
            return CommunityAddons.plugins[name]
        except KeyError:
            try:
                plugins_path = os.path.join(settings.PROJECT_PATH, 'zorna_plugins')
                for app in os.listdir(plugins_path):
                    if app == name:
                        app_path = os.path.join(plugins_path,app)
                        if os.path.isdir(app_path):
                            if not CommunityAddons.plugins.has_key(app):
                                self.load_app(app)
                                return CommunityAddons.plugins[app]
            except Exception as e:
                pass        

    def get_instance_by_content_type(self, ct):
        try:
            return CommunityAddons.content_types[ct]
        except KeyError:
            return None

    def get_id_by_content_type(self, ct):
        return self.id_by_content_type[ct]


@login_required()
def admin_list_communities(request):
    if request.user.is_superuser:
        object_id = request.GET.get('object_id', None)
        if object_id:
            com = Community.objects.get(pk=object_id)
            cal = get_community_calendar(com)
            ACLPermission.objects.copy_permissions(com, 'member', cal, 'viewer')
            ACLPermission.objects.copy_permissions(com, 'manage', cal, 'manager')
        ob_list = Community.objects.all()
        extra_context ={}
        extra_context['communities_list'] = ob_list
        context = RequestContext(request)
        return render_to_response('communities/admin_list_communities.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()

@login_required()
def admin_add_community(request):
    if request.user.is_superuser:
        if request.method == 'POST':    
            form = CommunityAdminAddForm(request.POST)
            if form.is_valid():
                com = form.save(commit=False)
                com.owner=com.modifier = request.user
                com.save()
                get_community_calendar(com)
                return HttpResponseRedirect(reverse('admin_list_communities'))
            else:
                form = CommunityAdminAddForm(request.POST)
        else:
            form = CommunityAdminAddForm()
            
        context = RequestContext(request)
        extra_context = {'form': form, 'curcommunity': False}
        return render_to_response('communities/edit_community.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()

@login_required()
def admin_edit_community(request, community):
    if request.user.is_superuser:
        community = Community.objects.get(pk=community)
        if request.method == 'POST':    
            form = CommunityAdminAddForm(request.POST, instance=community)
            if form.is_valid():
                com = form.save(commit=False)
                com.modifier=request.user
                com.save()
                get_community_calendar(com)
                return HttpResponseRedirect(reverse('admin_list_communities'))
            else:
                form = CommunityAdminAddForm(request.POST, instance=community)
        else:
            form = CommunityAdminAddForm(instance=community)
            
        context = RequestContext(request)
        extra_context = {'form': form, 'curcommunity': community}
        return render_to_response('communities/edit_community.html', extra_context, context_instance=context)
    else:
        return HttpResponseForbidden()

@login_required()
def join_community(request, comname, community):
    try:
        community = Community.objects.get(pk=community)
        if community.status == 1: # Public
            check = get_acl_for_model(community)
            check.add_perm('member', community, request.user, defines.ZORNA_PERMISSIONS_ALLOW)
            return HttpResponseRedirect(reverse('communities_home_page')+'?community_id='+str(community.pk))
        else:
            return HttpResponseRedirect(reverse('list_communities'))
    except Exception as e:
        return HttpResponseRedirect(reverse('list_communities'))

@login_required()
def leave_community(request, comname, community):
    try:
        community = Community.objects.get(pk=community)
        if community.status == 1: # Public
            check = get_acl_for_model(community)
            check.add_perm('member', community, request.user, defines.ZORNA_PERMISSIONS_DENY)
            return HttpResponseRedirect(reverse('list_communities'))
        else:
            return HttpResponseRedirect(reverse('list_communities'))
    except Exception as e:
        return HttpResponseRedirect(reverse('list_communities'))


@login_required()
def list_communities_view(request, queryset, extra_context, nb_page=NB_COMMUNITIES_BY_PAGE):
    try:
        extra_context['sidebar_right_template'] = "community_sidebar_right_template.html"
        loader.get_template(extra_context['sidebar_right_template'])
    except TemplateDoesNotExist:
        extra_context['sidebar_right_template'] = "communities/community_sidebar_right_template.html"
        
    extra_context['communities_count'] = Community.objects.filter(status__in=[0,1]).count()
    extra_context['allowed_communities'] = get_communities_ids(request.user)
    return object_list(request, queryset=queryset, extra_context=extra_context, template_name='communities/list_communities.html', paginate_by=nb_page)    


@login_required()
def list_communities(request):
    extra_context ={}
    extra_context['aselected'] = 'selected'
    extra_context['allowed_communities'] = get_communities_ids(request.user)
    ob_list = Community.objects.filter(status__in=[0,1])
    for o in ob_list:
        o.members_count = len(get_acl_by_object(o, 'member'))
        o.managers_count = len(get_acl_by_object(o, 'manage'))
    return list_communities_view(request, ob_list, extra_context)

@login_required()
def user_list_communities(request):
    extra_context ={}
    extra_context['bselected'] = 'selected'
    extra_context['allowed_communities'] = get_communities_ids(request.user)
    ob_list = Community.objects.filter(pk__in=extra_context['allowed_communities'])
    for o in ob_list:
        o.members_count = len(get_acl_by_object(o, 'member'))
        o.managers_count = len(get_acl_by_object(o, 'manage'))
    return list_communities_view(request, ob_list, extra_context)    

@login_required()
def last_activity_communities(request):
    extra_context ={}
    extra_context['cselected'] = 'selected'
    
    extra_context['allowed_communities'] = get_communities_ids(request.user)
    messages = MessageCommunity.objects.select_related().filter(
                    Q(users=request.user) | 
                    Q(communities__in=extra_context['allowed_communities'], reply__isnull=True ))
    messages = messages.order_by('-time_updated')
    return list_communities_view(request, messages, extra_context, 30)    


@login_required()
def community_members(request, community):
    extra_context = {}
    extra_context['community'] = Community.objects.get(pk=community)
    check = get_acl_for_model(extra_context['community'])
    if check.manage_community(extra_context['community'], request.user):
        extra_context['users_title'] = _(u"Members")
        users_list = get_acl_by_object(extra_context['community'], 'member')
        template = "communities/community_users.html"
        extra_context['next'] = request.REQUEST.get('next', reverse('communities_home_page')+'?community_id='+community)
        return object_list(request, queryset=users_list, template_name=template, extra_context=extra_context, paginate_by=20)
    else:
        return HttpResponseForbidden()

@login_required()
def community_managers(request, community):
    extra_context = {}
    extra_context['community'] = Community.objects.get(pk=community)
    check = get_acl_for_model(extra_context['community'])
    if check.manage_community(extra_context['community'], request.user):
        extra_context['users_title'] = _(u"Managers")
        users_list = get_acl_by_object(extra_context['community'], 'manage')
        template = "communities/community_users.html"
        extra_context['next'] = request.REQUEST.get('next', reverse('communities_home_page')+'?community_id='+community)
        return object_list(request, queryset=users_list, template_name=template, extra_context=extra_context, paginate_by=20)
    else:
        return HttpResponseForbidden()


@login_required()
def manage_community_members(request, community):
    extra_context = {}
    extra_context['community'] = Community.objects.get(pk=community)
    check = get_acl_for_model(extra_context['community'])
    if check.manage_community(extra_context['community'], request.user):
        extra_context['users_title'] = _(u"Members of ")
        if request.method == 'POST':
            selected = request.POST.getlist('_selected_action')
            # delete permission
            ACLPermission.objects.delete_user_permissions('member', extra_context['community'])
            # add permission for checked users   
            ol = User.objects.filter(pk__in=selected)
            for u in ol:
                check.add_perm('member', extra_context['community'], u, defines.ZORNA_PERMISSIONS_ALLOW)
            
            u = request.POST.get("u", "")
            if u :
                u = User.objects.get(pk=u)
                check.add_perm('member', extra_context['community'], u, defines.ZORNA_PERMISSIONS_ALLOW)

        users_list = get_acl_users_by_object(extra_context['community'], 'member')
        extra_context['next'] = request.REQUEST.get('next', reverse('communities_home_page')+'?community_id='+community)
        template = "communities/manage_community_users.html"
        return object_list(request, queryset=users_list, template_name=template, extra_context=extra_context, paginate_by=20)
    else:
        return HttpResponseForbidden()

@login_required()
def manage_community_managers(request, community):
    extra_context = {}
    extra_context['community'] = Community.objects.get(pk=community)
    check = get_acl_for_model(extra_context['community'])
    if check.manage_community(extra_context['community'], request.user):
        extra_context['users_title'] = _(u"Managers of ")
        if request.method == 'POST':
            selected = request.POST.getlist('_selected_action')
            # delete permission
            ACLPermission.objects.delete_user_permissions('manage', extra_context['community'])
            # add permission for checked users   
            ol = User.objects.filter(pk__in=selected)
            for u in ol:
                check.add_perm('manage', extra_context['community'], u, defines.ZORNA_PERMISSIONS_ALLOW)
            
            u = request.POST.get("u", "")
            if u :
                u = User.objects.get(pk=u)
                check.add_perm('manage', extra_context['community'], u, defines.ZORNA_PERMISSIONS_ALLOW)

        users_list = get_acl_users_by_object(extra_context['community'], 'manage')
        extra_context['next'] = request.REQUEST.get('next', reverse('communities_home_page')+'?community_id='+community)
        template = "communities/manage_community_users.html"
        return object_list(request, queryset=users_list, template_name=template, extra_context=extra_context, paginate_by=20)
    else:
        return HttpResponseForbidden()

@login_required()
def communities_home_page(request):
    if user_has_access_to_communities(request.user) == False:
        return HttpResponseForbidden()

    #first process form submission
    msg_type = request.REQUEST.get("msg-type", 'message_tab')
    html_form = user_send_message(request, msg_type)
    
    #then get messages to display
    ret = get_messages(request)
    
    ret['html_form'] = html_form
    ret['tab'] = msg_type
    if ret['all_msg'] ==  'followed':
        ret['current_menu'] = "followed"
        ret['zorna_title_page'] = _(u"Followed posts")
    elif ret['all_msg'] ==  'tome':
        ret['current_menu'] = "tome"
        ret['zorna_title_page'] = _(u"Direct to me")
    elif ret['all_msg'] ==  'last':
        ret['current_menu'] = "last"
        ret['zorna_title_page'] = _(u"Recent messages")
    else:
        ret['current_menu'] = "messages"
        ret['zorna_title_page'] = _(u"Messages")
    return communities_home(request, ret)

@login_required()
def communities_home_files(request):
    if user_has_access_to_communities(request.user) == False:
        return HttpResponseForbidden()

    ret = initialize_context(request)
    ret['current_menu'] = "files"
    ret['zorna_title_page'] = _(u"Attachments")
    q = ret['search_string']

    messages = get_all_messages(request, int(ret['community_id']))
    if ret['from_id'] != 0:
        messages = messages.filter(owner=ret['from_id'], reply__isnull=True)
    
    messages = messages.order_by('-time_updated')
    ret['attachments'] = []
    puc = get_upload_communities()
    for msg in messages:        
        path = "%s/%s" % (puc, msg.pk)
        try:
            files = []
            for f in os.listdir(path):
                if q and not q in f:
                    continue
                files.append({'name':f, 'ext': os.path.splitext( f )[1][1:]})
            if len(files):
                if not ret['users_avatars'].has_key(msg.owner_id):
                    try:
                        ret['users_avatars'][msg.owner_id] = UserAvatar.objects.get(user__id=msg.owner_id)
                    except UserAvatar.DoesNotExist:
                        ret['users_avatars'][msg.owner_id] = None
                avatar_user = ret['users_avatars'][msg.owner_id]
                msg.avatar_user = avatar_user
                ret['attachments'].append({ 'message': msg, 'files': files})
                
        except:
            pass
        
    paginator = Paginator(ret['attachments'], NB_MESSAGES_BY_PAGE)
    page = int(request.GET.get('page', 1))
    try:
        ret['attachments'] = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        ret['attachments'] = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        ret['attachments'] = paginator.page(paginator.num_pages)
    ret['page'] = page
    ret['paginator'] = paginator            

    return communities_home(request, ret, 'communities/home_files.html')


@login_required()
def communities_home_members(request):
    if user_has_access_to_communities(request.user) == False:
        return HttpResponseForbidden()

    ret = initialize_context(request)
    ret['current_menu'] = "members"
    ret['zorna_title_page'] = _(u"Members")

    try:
        form = FormsForm.objects.get(slug=settings.ZORNA_COMMUNITY_USER_PROFILE_FORM)
        entries = form.entries.filter(account__in=ret['members'])
    except:
        entries = None

    kwargs = {}
    profiles = {}

    kwargs['q'] = ret['search_string'].decode('utf8')
    if entries:
        kwargs['entries'] = entries
        columns, rows = forms_get_entries(settings.ZORNA_COMMUNITY_USER_PROFILE_FORM, **kwargs)
        for r in rows:
            profiles[r['entity'].account_id] = r
    else:
        columns, rows = None, None
    
    t = loader.get_template("account/user_card.html")
    ret['com_members'] = []
    index = 0
    for x in ret['members']:
        if kwargs['q'] and not profiles.has_key(x.pk) and kwargs['q'].lower() not in x.get_full_name().lower() :
            continue
        if not ret['users_avatars'].has_key(x.pk):
            try:
                ret['users_avatars'][x.pk] = UserAvatar.objects.get(user__id=x.pk)
            except UserAvatar.DoesNotExist:
                ret['users_avatars'][x.pk] = None
        x.avatar_user = ret['users_avatars'][x.pk]
        if  profiles.has_key(x.pk):
            row = profiles[x.pk]
        else:
            row = None
        c = RequestContext(request, {'row': row, 'columns':columns, 'account':x, 'index':index})
        x.html = t.render(c)
        ret['com_members'].append(x)
        index += 1

    def entry_sort(entry):
        return entry.get_full_name()

    ret['com_members'].sort(key=entry_sort)
        
    paginator = Paginator(ret['com_members'], NB_MESSAGES_BY_PAGE)
    page = int(request.GET.get('page', 1))
    try:
        ret['com_members'] = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        ret['com_members'] = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        ret['com_members'] = paginator.page(paginator.num_pages)
    ret['page'] = page
    ret['paginator'] = paginator            

    return communities_home(request, ret, 'communities/home_members.html')

@login_required()
def communities_home_plugin(request, id):
    if not user_has_access_to_communities(request.user):
        return HttpResponseForbidden()

    ret = initialize_context(request)
    ret['current_menu'] = id

    cp = get_community_addons_instance(request, ret['community_id'])
    try:
        r = id.split('_')
        if len(r) == 3 and r[-1] == 'menu':
            instance = cp.get_instance_by_name(r[0])
        else:
            instance = None
    except:
        instance = None

    if instance:
        ret['plugin_list'] = instance.render_page(request,  r[-2], ret)
        ret['plugin_id'] = cp.get_tab_id(instance,r[-2])
        for entry in ret['plugin_list']:
            if not ret['users_avatars'].has_key(entry['message'].owner_id):
                try:
                    ret['users_avatars'][entry['message'].owner_id] = UserAvatar.objects.get(user__id=entry['message'].owner_id)
                except UserAvatar.DoesNotExist:
                    ret['users_avatars'][entry['message'].owner_id] = None
            entry['avatar_user'] = ret['users_avatars'][entry['message'].owner_id]
    
        
        paginator = Paginator(ret['plugin_list'], NB_MESSAGES_BY_PAGE)
        page = int(request.GET.get('page', 1))
        try:
            ret['plugin_list'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            ret['plugin_list'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            ret['plugin_list'] = paginator.page(paginator.num_pages)
        ret['page'] = page
        ret['paginator'] = paginator 
        ret['css_file'] = instance.get_css_file(ret['plugin_id'])
        
        ret['zorna_title_page'] = instance.get_page_title(request, r[-2] )        
    
    return communities_home(request, ret, 'communities/home_plugin.html')


@login_required()
def communities_edit_plugin(request, id, instance_id):
    if not user_has_access_to_communities(request.user):
        return HttpResponseForbidden()

    cp = get_community_addons_instance(request, 0, False)
    try:
        r = id.split('_')
        if len(r) == 5 and r[-1] == 'tab':
            instance = cp.get_instance_by_name(r[0])
        else:
            instance = None
    except:
        instance = None

    if instance:
        if request.method == 'POST':
            form = instance.get_form(request, r[-2], post=True, instance_id=instance_id)
            if form.is_valid():
                instance.save(request, r[-2], form, None)
                return HttpResponse('')
        else:
            form = instance.get_form(request, r[-2], instance_id=instance_id)
                
        extra_context = {}
        extra_context['form'] = form
        extra_context['form_extra'] = instance.render_form(request, form)
        extra_context['action'] = reverse('communities_edit_plugin', args=[id, instance_id])

        context = RequestContext(request)
        return render_to_response('communities/edit_plugin.html', extra_context, context_instance=context)
    else:
        return CommunityPopupHttpResponseError(request, _(u'Access Denied'))


@login_required()
def communities_home(request, ret, template='communities/home.html'):
    try:
        avatar_user = UserAvatar.objects.get(user=request.user)
    except UserAvatar.DoesNotExist:
        avatar_user = None
    ret['avatar'] = avatar_user

    cp = get_community_addons_instance(request, ret['community_id'])
    ret['tabs'] = [ {'id': 'message_tab', 'title': _(u'Message')}, ]
    ret['tabs'].extend(cp.plugins_tabs)
    ret['plugins_menus'] = cp.plugins_menus
    
    ret['plugins'] = []
    for id, instance in cp.tabs.iteritems():
        r = id.split('_')
        title, html = instance.render_widget(request, r[-2], ret['community_id'])
        if title:
            ret['plugins'].append({'title': title, 'html':html, 'contenttype_id': instance.get_content_type_id(r[-2])})
    
    ret['jsfollow'] = _(u'Follow')
    ret['jsunfollow'] = _(u'Unfollow')
    context = RequestContext(request)
    return render_to_response(template, ret, context_instance=context)

def get_tab(request, tab):
    #form.tab_title = _(u"Message")
    ret = {}
    data = []
    community_id = request.GET.get("community_id", 0)
    try:
        cp = get_community_addons_instance(request, 0, True)
        r = tab.split('_')
        if len(r) == 5 and r[-1] == 'tab':
            instance = cp.get_instance_by_name(r[0])
            ao = instance.get_communities(request, r[-2])
            if community_id and int(community_id) in ao:
                ao = [community_id] 
            communities = Community.objects.filter(id__in=ao).order_by('name')
            members = instance.get_users(request, r[-2])
            for com in communities:
                data.append([com.name, "g-%s" % str(com.id)])
            data.extend([ ("%s %s" % (x.last_name, x.first_name), ("u-%s" % str(x.id))) for x in members ])    
        else:
            instance = None
            ao = set([])
            ao_member = get_allowed_objects(request.user, Community, 'member')        
            ao = ao.union(set(ao_member))
            ao_manage = get_allowed_objects(request.user, Community, 'manage')        
            ao = ao.union(set(ao_manage))
        
            if community_id and int(community_id) in ao:
                ao = [community_id] 
            communities = Community.objects.filter(id__in=ao).order_by('name')
            
            members = set([])
            for com in communities:
                members = members.union(set(get_acl_by_object(com, 'member')))
                members = members.union(set(get_acl_by_object(com, 'manage')))
                data.append([com.name, "g-%s" % str(com.id)])
            data.extend([ ("%s %s" % (x.last_name, x.first_name), ("u-%s" % str(x.id))) for x in members ])    

        if request.method == 'POST':
            mcf = MessageCommunityForm(request.POST or None, request.FILES or None)
            
            if instance:
                form_extra = instance.get_form(request, r[-2], True)
            else:
                form_extra = None
                    
            if mcf.is_valid() and ( form_extra == None or form_extra.is_valid()):
                m = mcf.save(request)
                if m:
                    if form_extra:
                        fx = instance.save(request, r[-2], form_extra, m)
                        MessageCommunityExtra.objects.create(message=m, content_object=fx)
                
                #initialize form and display only current tab        
                mcf = MessageCommunityForm()
                if instance:
                    form_extra = instance.get_form(request, r[-2])
                else:
                    form_extra = None
            else:
                mcf.data['send_to'] = ''           
        else:
            mcf = MessageCommunityForm()
            if instance:
                form_extra = instance.get_form(request, r[-2])
            else:
                form_extra = None

        if form_extra:
            form_extra = instance.render_form(request, form_extra)
        else:
            form_extra = None
            
        mcf.message_type = tab
        
        t = loader.get_template("communities/message_form.html")
        c = RequestContext(request, {'message_form': mcf, 'form_extra': form_extra})
        ret['error'] = False
        ret['html'] = t.render(c)
        ret['sendto'] = data
    except Exception as e:
        ret['error'] = True
        ret['html'] = "Error: Can't load form (%s)" % e
        ret['sendto'] = []
    return ret


def get_json_tab(request, tab):
    ret = get_tab(request, tab)
    json_data = simplejson.dumps(ret)
    return HttpResponse(json_data)
        

def user_send_message(request, msg_type):
    ret = get_tab(request, msg_type)
    return ret['html']
            
@login_required()
def user_send_reply(request):
    message = request.GET.get("reply_message", None)
    msg_id = request.GET.get("msg_id", 0)
    ret = {}
    ret['html'] = ''        
    ret['msgid'] = 0
    if msg_id and message:
        try:
            r = MessageCommunity.objects.get(pk=msg_id)
            m = MessageCommunity(message=message)
            m.owner = m.modifier = request.user
            m.reply = r
            m.save()
            m.manager = True
            # update parent time message
            r.time_updated = m.time_updated
            r.modifier = request.user
            r.save()
            #current_community = request.POST.get("current_community", 0)
            t = loader.get_template('communities/message_reply.html')
            c = RequestContext(request, {"reply":m })
            ret['html'] = t.render(c)
            ret['msgid'] = m.pk
            #send email to followers
            followers = r.followers.all().exclude(pk=request.user.pk)

            subject = _(u'New reply from %s' % request.user.get_full_name())
            url = request.build_absolute_uri(reverse('communities_home_page', args=[]))
            email = ZornaEmail()
            for f in followers:
                ec = {"follower": f, "message": r, 'reply': m, 'url':url }
                body_text = render_to_string('communities/email_follower_text.html', ec )
                body_html = render_to_string('communities/email_follower_html.html', ec )
                email.append(subject, body_text, body_html, settings.DEFAULT_FROM_EMAIL, [f.email])
            email.send()
        except MessageCommunity.DoesNotExist:
            pass
    json_data = simplejson.dumps(ret)
    return HttpResponse(json_data)

@login_required()
def user_update_reply(request):
    ret = {}
    msg_id = request.GET.get("msgid", None)
    message = request.GET.get("value", '')
    ret['msgid'] = msg_id
    ret['message'] = message
    try:
        r = MessageCommunity.objects.get(pk=msg_id)
        ret['error'] = False
    except MessageCommunity.DoesNotExist:
        ret['error'] = True
        r = None
         
    if message and r:
        r.message = message
        r.modifier=request.user
        r.save()
        try:
            extra = MessageCommunityExtra.objects.get(message=r)
            extra.content_object.update_message(r)
        except:
            pass
    elif r:
        ret['message'] = r.message

    json_data = simplejson.dumps(ret)
    return HttpResponse(json_data)

@login_required()
def user_delete_reply(request):
    ret = {}
    msg_id = request.GET.get("msgid", None)
    ret['msgid'] = msg_id
    try:
        MessageCommunity.objects.get(pk=msg_id).delete()
        ret['error'] = False
    except MessageCommunity.DoesNotExist:
        ret['error'] = True
         
    json_data = simplejson.dumps(ret)
    return HttpResponse(json_data)

def delete_message_attachments(message_id):
    try:
        path = os.path.join(get_upload_communities(), "%s" % message_id)
        files = os.listdir(path)
        for f in files:
            fullpath=os.path.join(path, f)
            if os.path.isfile(fullpath):
                os.remove(fullpath)
        os.rmdir(path)
        return True
    except Exception:
        return False

@login_required()
def user_delete_message(request):
    ret = {}
    msg_id = request.GET.get("msgid", None)
    ret['msgid'] = msg_id
    try:
        MessageCommunity.objects.filter(reply=msg_id).delete()
        r = MessageCommunity.objects.get(pk=msg_id)
        try:
            extra = MessageCommunityExtra.objects.get(message=r)
            extra.content_object.delete()
        except:
            pass
        r.delete()
        delete_message_attachments(msg_id)
        ret['error'] = False
    except MessageCommunity.DoesNotExist:
        ret['error'] = True
        r = None
         
    json_data = simplejson.dumps(ret)
    return HttpResponse(json_data)

def get_new_messages(request, community_id, max_msg_id, search_string, all_msg, member_id, message_id, ct_id):
    allowed_objects = get_allowed_objects(request.user, Community, ['manage', 'member'])
    
    if all_msg == 'followed':
        messages = MessageCommunity.objects.select_related().filter(followers=request.user)
    elif all_msg == 'last':
        from_date = request.user.get_profile().last_activity
        messages = MessageCommunity.objects.select_related().filter(Q(time_updated__gt=from_date)|Q(reply__time_updated__gt=from_date))
    elif all_msg == 'tome':
        messages = MessageCommunity.objects.select_related().filter(users=request.user)
    elif all_msg == 'contributor':
        member = User.objects.get(pk=member_id)
        messages = MessageCommunity.objects.select_related().filter(Q(communities__in=allowed_objects) & ( Q(owner=member, reply__isnull=True )|Q(messagecommunity__owner=member)))
    elif all_msg == 'message':
        messages = MessageCommunity.objects.select_related().filter(pk=message_id)
    elif all_msg == 'contenttype':
        messages = MessageCommunity.objects.select_related().filter(contenttype=ct_id)
    elif community_id:
        if int(community_id) in allowed_objects:
            messages = MessageCommunity.objects.select_related().filter(Q(communities__exact=community_id))
    else:
        messages = MessageCommunity.objects.select_related().filter(Q(communities__in=allowed_objects)|Q(owner=request.user)|Q(users=request.user)|Q(reply__owner=request.user))
    
    try:
        messages = messages.filter((Q(pk__gt=int(max_msg_id)) & Q(reply__isnull=True)) | Q(messagecommunity__pk__gt=int(max_msg_id)))
    except NameError:
        return MessageCommunity.objects.none()
    return messages
    
def get_messages(request):
    max_msg_id = request.REQUEST.get("msg_max_id", 0)

    ret = initialize_context(request)
    messages = None
    if int(max_msg_id):
        messages = get_new_messages(request, int(ret['community_id']), max_msg_id, ret['search_string'], ret['all_msg'], ret['member_id'], ret['message_id'], ret['contenttype_id'])
    elif ret['all_msg'] ==  'all':
        messages = get_all_messages(request, int(ret['community_id']))
    elif ret['all_msg'] ==  'followed':
        messages = get_followed_messages(request)
    elif ret['all_msg'] ==  'last':
        messages = get_all_messages(request, int(ret['community_id']), request.user.get_profile().last_activity)
    elif ret['all_msg'] ==  'tome':
        messages = get_tome_messages(request)
    elif ret['all_msg'] ==  'contributor':
        messages = get_contributor_messages(request, ret['member_id'])
    elif ret['all_msg'] ==  'message':
        messages = get_message_by_id(request, ret['message_id'])
    elif ret['all_msg'] ==  'contenttype':
        messages = get_messages_by_content_type(request, ret['contenttype_id'])
    else:
        messages = MessageCommunity.objects.none()

    #if max_msg_id == 0 and ret['last_msg_id']:
    #    messages = messages.filter(pk__lt=int(ret['last_msg_id']))

    if ret['search_string'] != '':
        messages = messages.filter(message__icontains=ret['search_string'])
    
    if ret['from_id'] != 0:
        messages = messages.filter(owner=ret['from_id'], reply__isnull=True)

    messages = messages.annotate(nb_replies=Count('messagecommunity'))
    messages = messages.annotate(nb_followers=Count('followers'))
    messages = messages.order_by('-time_updated')

    if max_msg_id == 0:
        page = int(ret['com_page'])
        messages = messages[page*NB_MESSAGES_BY_PAGE:(page+1) * NB_MESSAGES_BY_PAGE]
        ret['com_page'] = page + 1
        c = messages.count()
        if c :
            ret['com_page'] = page + 1
        ret['messages_more'] = False if c < NB_MESSAGES_BY_PAGE else True
        
    t = loader.get_template('communities/message_entry.html')
    extra_context = ret.copy()
    html = []
    extra_context['msg'] = ''
    extra_context['current_query_string'] = ret['current_query_string']
    # retrieve msg followed by user
    if request.user.is_anonymous():
        msg_followed = MessageCommunity.objects.none()
    else:
        msg_followed = MessageCommunity.objects.filter(followers=request.user)
    
    upload_path = get_upload_communities()
    cp = get_community_addons_instance(request,int(ret['community_id']))
    for msg in messages:
        if msg.nb_replies:
            replies = MessageCommunity.objects.select_related().filter(reply__isnull=False, reply=msg).order_by('time_updated')
            msg.replies = replies

        if ret['users_avatars'].has_key(msg.owner_id):
            extra_context['avatar_user'] = ret['users_avatars'][msg.owner_id]
        else:
            try:
                ret['users_avatars'][msg.owner_id] = UserAvatar.objects.get(user__id=msg.owner_id)
            except UserAvatar.DoesNotExist:
                ret['users_avatars'][msg.owner_id] = None
            extra_context['avatar_user'] = ret['users_avatars'][msg.owner_id]
            
        path = "%s/%s" % (upload_path, msg.pk)
        try:
            extra_context['attachments'] = [{'file':f, 'ext': os.path.splitext( f )[1][1:] } for f in os.listdir(path)]
        except:
            extra_context['attachments'] = []        

        try:
            extra = MessageCommunityExtra.objects.get(message=msg)
            #msg.extra = extra.content_object
            instance = cp.get_instance_by_content_type(extra.content_type_id)
            if instance:
                msg.extra = instance.render_message(request, extra.content_object)
                msg.extra_id = cp.get_id_by_content_type(extra.content_type_id)
                msg.extra_object_id = extra.object_id
            else:
                msg.extra = None
        except Exception as e:
            msg.extra = None
        
        extra_context['msg'] = msg
        c = RequestContext(request, extra_context)
        #ret['last_msg_id'] = max(msg.pk, ret['last_msg_id'])
        if msg in msg_followed:
            msg.follow = True
        else:
            msg.follow = False

        msg.manager = is_manager_by_message(request.user, msg.pk)
        html.append({ 'id': msg.pk , 'msg': t.render(c) })

    ret['html_messages'] = html
    
    return ret

def check_messages_ajax(request):
    ret = get_messages(request)
    data = {}
    data['html_messages'] = ret['html_messages']
    if ret.has_key('messages_more'):
        data['com_page'] = ret['com_page']
        data['messages_more'] = ret['messages_more']
    json_data = simplejson.dumps(data)
    return HttpResponse(json_data)

@login_required()
def get_file(request, msg, filename):
    baccess = is_member_by_message(request.user, msg) or is_manager_by_message(request.user, msg)

    if baccess:
        upload_path = get_upload_communities()
        path = "%s/%s" % (upload_path, msg)
        for f in os.listdir(path):
            if f == filename:
                path = "%s/%s" % ( path, f)
                fp = open(path, 'rb')
                content_type = mimetypes.guess_type(f)[0]
                response     = HttpResponse(fp.read(),content_type=content_type)
                response['Content-Length']      = os.path.getsize(path)    
                response['Content-Disposition'] = "attachment; filename=%s"%f
                return response
    else:
        return HttpResponseForbidden()

def follow_message_ajax(request):
    ret = {}
    message = request.GET.get("message", None)
    if message and (is_member_by_message(request.user, message) or is_manager_by_message(request.user, message)) :
        msg = MessageCommunity.objects.get(pk=message)
        msg.followers.add(request.user)
        ret['msgid'] = message
        ret['follow'] = True
        ret['error'] = False
    else:
        ret['follow'] = False
        ret['error'] = True

    json_data = simplejson.dumps(ret)
    return HttpResponse(json_data)

        
def unfollow_message_ajax(request):
    ret = {}
    message = request.GET.get("message", None)
    baccess = is_member_by_message(request.user, message) or is_manager_by_message(request.user, message)
    if baccess:
        msg = MessageCommunity.objects.get(pk=message)
        msg.followers.remove(request.user)
        ret['msgid'] = message
        ret['follow'] = False
        ret['error'] = False
    else:
        ret['follow'] = True
        ret['error'] = True

    json_data = simplejson.dumps(ret)
    return HttpResponse(json_data)

def member_profile(request, member):
    #TODO permission
    extra_context ={}
    try:
        avatar_user = UserAvatar.objects.get(user__id=member)
    except UserAvatar.DoesNotExist:
        avatar_user = None
    extra_context['avatar_user'] = avatar_user
    extra_context['member_id'] = member
    context = RequestContext(request)
    return render_to_response('communities/member_profile.html', extra_context, context_instance=context)

def invite_community_member(request, community_id):
    extra_context = {}
    extra_context['community'] = Community.objects.get(pk=community_id)
    check = get_acl_for_model(extra_context['community'])
    if check.manage_community(extra_context['community'], request.user):
        form = InviteCommunityForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            users = form.cleaned_data['send_to'].split(',')
            check = get_acl_for_model(extra_context['community'])
            ol = User.objects.filter(pk__in=users)
            for u in ol:
                if form.cleaned_data['manager']:
                    check.add_perm('manage', extra_context['community'], u, defines.ZORNA_PERMISSIONS_ALLOW)
                else:
                    check.add_perm('member', extra_context['community'], u, defines.ZORNA_PERMISSIONS_ALLOW)
                    
            #TODO send an email to all recipients
            subject = _(u'%(user)s added you to %(community)s') % {'user':request.user.get_full_name(), 'community':extra_context['community'].name}
            url = request.build_absolute_uri(reverse('communities_home_page', args=[]))
            if form.cleaned_data['manager']:
                role = _("manager")
            else:
                role = _("member")

            email = ZornaEmail()
            for f in ol:
                ec = {
                        "member": f, 
                        "message": form.cleaned_data['message'], 
                        'community': extra_context['community'], 
                        'url': url, 
                        'role': role,
                        'user': request.user 
                    }
                body_text = render_to_string('communities/email_invite_text.html', ec )
                body_html = render_to_string('communities/email_invite_html.html', ec )
                email.append(subject, body_text, body_html, settings.DEFAULT_FROM_EMAIL, [f.email])
            email.send()
            return HttpResponse('')
        extra_context['form'] = form
        extra_context['action'] = reverse('invite_community_member', args=[community_id])
        context = RequestContext(request)
        return render_to_response('communities/community_invite_member.html', extra_context, context_instance=context)
    else:
        return CommunityPopupHttpResponseError(request, _(u'Access Denied'))    

def invite_list_users(request, community_id):
    users = set([])
    ret = {}
    try:
        com = Community.objects.get(pk=community_id)
        if is_user_community_manager(request.user, com.pk):
            users = users.union(set(get_acl_by_object(com, 'member')))
            users = users.union(set(get_acl_by_object(com, 'manage')))
            ret['data'] = [("%s %s" % (x.last_name, x.first_name), ("%s" % str(x.id))) for x in User.objects.all().exclude(pk__in=[u.pk for u in users]) ]
    except Community.DoesNotExist:
        pass
    data = simplejson.dumps(ret)
    return HttpResponse(data)
    