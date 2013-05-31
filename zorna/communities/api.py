import os
import urllib
from django.db.models import Count
from django.utils import simplejson
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from zorna.calendars.models import ZornaCalendar
from zorna.acl.models import get_allowed_objects
from zorna.communities.models import Community, MessageCommunity, MessageCommunityExtra
from zorna.acl.models import get_acl_by_object, get_acl_for_model
from zorna.account.models import UserAvatar
from zorna.utilit import get_upload_communities


class ZornaCommunityAddons(object):

    def get_title(self, id):
        return ''

    def get_content_type(self, id):
        return None

    def get_content_types(self):
        return []

    def get_content_type_id(self, id):
        return None

    def get_css_file(self, id):
        return None

    def get_js_file(self, id):
        return None

    def get_message(self, id):
        return None

    def save(self, request, id, form, message):
        return form.save(request=request, message=message)

    def get_tabs(self, request, community_id=0):
        return []

    def get_communities(self, request, id):
        return []

    def get_users(self, request, id):
        return []

    def get_menus(self, request, community_id=0):
        return []

    def get_page_title(self, request, id):
        return ''

    def render_form_by_id(self, request, id, post=False):
        return ''

    def render_form(self, request, form, ec={}):
        return ''

    def get_form(self, request, id, post=False):
        return None

    def render_message(self, request, assignment):
        return ''

    def render_page(self, request, id, context={}):
        return ''

    def render_widget(self, request, id, community_id):
        return None, None


def initialize_context(request):
    ret = {}
    ret['all_msg'] = request.REQUEST.get("all_msg", 'all')
    ret['community_id'] = request.REQUEST.get("community_id", 0)
    ret['search_string'] = request.REQUEST.get("search_string", '')
    ret['search_string'] = ret['search_string'].encode('utf8')
    ret['member_id'] = request.REQUEST.get("member_id", 0)
    ret['message_id'] = request.REQUEST.get("message_id", 0)
    ret['contenttype_id'] = request.REQUEST.get("contenttype_id", 0)
    ret['current_query_string'] = urllib.urlencode(ret)
    # Next lines must be after previous line
    ret['com_page'] = request.REQUEST.get("com_page", 0)
    ret['from_id'] = request.REQUEST.get("from_id", 0)
    if ret['from_id'] == '':
        ret['from_id'] = 0
    else:
        ret['from_id'] = int(ret['from_id'])

    ao = set([])

    ao_member = get_allowed_objects(request.user, Community, 'member')
    ao = ao.union(set(ao_member))
    ao_manage = get_allowed_objects(request.user, Community, 'manage')
    ao = ao.union(set(ao_manage))
    ret['communities'] = Community.objects.filter(id__in=ao).order_by('name')
    ret['user_manager'] = True if len(ao_manage) else False
    ccom = int(ret['community_id'])
    ret['current_community'] = None
    for com in ret['communities']:
        com.manager = True if com.pk in ao_manage else False
        com.member = True if com.pk in ao_member else False
        if ccom != 0 and ccom == com.pk:
            ret['current_community'] = com

    if int(ret['community_id']) != 0 and ret['current_community'] and ret['current_community'] in ret['communities']:
        communities = [ret['current_community']]
    else:
        communities = ret['communities']
        ret['community_id'] = 0

    data = []
    ret['members'] = set([])
    for com in communities:
        ret['members'] = ret['members'].union(
            set(get_acl_by_object(com, 'member')))
        ret['members'] = ret['members'].union(
            set(get_acl_by_object(com, 'manage')))
        data.append([com.name, "g-%s" % str(com.id)])

    data.extend([("%s %s" % (x.last_name, x.first_name), ("u-%s" % str(x.id)))
                for x in ret['members']])
    ret['members_count'] = len(ret['members'])

    if int(ret['community_id']):
        contributors = MessageCommunity.objects.values('owner').filter(
            Q(communities=int(ret['community_id'])) |
            Q(reply__communities=int(ret['community_id']))
        ).annotate(total=Count('owner')
                   )
    else:
        contributors = MessageCommunity.objects.values(
            'owner').annotate(total=Count('owner'))
    contributors = contributors.order_by('-total')[0:10]

    ret['users_avatars'] = {}
    for avatar in UserAvatar.objects.select_related().filter(user__pk__in=[u.pk for u in ret['members']] + [c['owner'] for c in contributors]):
        ret['users_avatars'][avatar.user_id] = avatar

    for m in ret['members']:
        if ret['users_avatars'].has_key(m.pk):
            m.avatar = ret['users_avatars'][m.pk]
        else:
            m.avatar = None
    for c in contributors:
        if ret['users_avatars'].has_key(c['owner']):
            c['avatar'] = ret['users_avatars'][c['owner']]
            c['user'] = ret['users_avatars'][c['owner']].user
        else:
            c['avatar'] = None
            c['user'] = User.objects.get(pk=c['owner'])

    ret['contributors'] = contributors
    ret['members_data'] = simplejson.dumps(data)

    if ret['current_community']:
        ret['community_title'] = ret['current_community'].name
    elif ret['all_msg'] == 'followed':
        ret['community_title'] = _(u"Followed posts")
    elif ret['all_msg'] == 'last':
        ret['community_title'] = _(u"Recent messages")
    elif ret['all_msg'] == 'tome':
        ret['community_title'] = _(u"Direct to me")
    elif ret['all_msg'] == 'contributor':
        member = User.objects.get(pk=ret['member_id'])
        ret['community_title'] = member.get_full_name()
    elif ret['all_msg'] == 'contenttype':
        ret['community_title'] = _(u"Content type")
    elif ret['all_msg'] == 'message':
        ret['community_title'] = _(u"Message")
    else:
        ret['community_title'] = _(u"All")

    if int(ret['from_id']) != 0:
        ret['msg_sender'] = User.objects.get(pk=int(ret['from_id']))
    return ret


def get_community_calendar(community):
    return ZornaCalendar.objects.get_or_create_calendar_for_object(community.owner, community, distinction='owner', name=community.name)


def get_community(id):
    try:
        return Community.objects.get(pk=id)
    except:
        return None


def get_communities_ids(user):
    return get_allowed_objects(user, Community, ['member', 'manage'])


def get_communities(user=None):
    if user:
        return Community.objects.filter(pk__in=get_communities_ids(user))
    else:
        return Community.objects.all()


def user_has_access_to_communities(user):
    allowed_objects = get_communities_ids(user)
    return len(allowed_objects) != 0


def get_member_communities_ids(user):
    return get_allowed_objects(user, Community, 'member')


def get_member_communities(user):
    return Community.objects.filter(pk__in=get_member_communities_ids(user))


def is_user_community_manager(user, community_id=0):
    allowed_objects = get_allowed_objects(user, Community, 'manage')
    if community_id == 0:
        return len(allowed_objects) != 0
    elif community_id in allowed_objects:
        return True
    else:
        return False


def get_managed_communities_ids(user):
    return get_allowed_objects(user, Community, 'manage')


def get_managed_communities(user):
    return Community.objects.filter(pk__in=get_managed_communities_ids(user))


def get_community_managers(user, community):
    if not isinstance(community, Community):
        community = Community.objects.get(pk=community)
    check = get_acl_for_model(community)
    if check.manage_community(community, user):
        return get_acl_by_object(community, 'manage')
    else:
        return Community.objects.none()


def is_member_by_message(user, message):
    baccess = False
    allowed_objects = get_allowed_objects(user, Community, 'member')
    c = Community.objects.filter(
        messagecommunity__pk=message, pk__in=allowed_objects)
    if c:
        baccess = True
    elif user.is_authenticated():
        # is this message is sent to current user?
        # u =
        # User.objects.filter(Q(message_users__messagecommunity__pk=message,
        # pk=user.pk))
        l = MessageCommunity.objects.filter(users=user, pk=message)
        if l:
            baccess = True
        else:
            try:
                MessageCommunity.objects.get(pk=message, owner=user)
                baccess = True
            except MessageCommunity.DoesNotExist:
                pass
    return baccess


def is_manager_by_message(user, message):
    baccess = False
    allowed_objects = get_allowed_objects(user, Community, 'manage')
    c = Community.objects.filter(
        messagecommunity__pk=message, pk__in=allowed_objects)
    if c:
        baccess = True
    elif user.is_authenticated():
        # is this message owned by current user?
        try:
            MessageCommunity.objects.get(pk=message, owner=user)
            baccess = True
        except MessageCommunity.DoesNotExist:
            baccess = False
    return baccess


def get_all_messages(request, community_id=0, from_date=None):
    allowed_objects = get_allowed_objects(
        request.user, Community, ['member', 'manage'])
    messages = MessageCommunity.objects.none()
    if request.user.is_authenticated():
        if community_id and int(community_id) in allowed_objects:
            messages = MessageCommunity.objects.select_related().filter(
                Q(communities=community_id), reply__isnull=True)
        elif int(community_id) == 0:
            messages = MessageCommunity.objects.select_related().filter(Q(communities__in=allowed_objects) | Q(
                users=request.user) | Q(owner=request.user), reply__isnull=True)
    else:
        if community_id and int(community_id) in allowed_objects:
            messages = MessageCommunity.objects.select_related().filter(
                Q(communities=community_id), reply__isnull=True)
        elif int(community_id) == 0:
            messages = MessageCommunity.objects.select_related().filter(
                Q(communities__in=allowed_objects), reply__isnull=True)

    if from_date:
        messages = messages.filter(Q(time_updated__gt=from_date) | Q(
            reply__time_updated__gt=from_date))
    return messages


def get_message_by_id(request, message_id):
    allowed_objects = get_allowed_objects(
        request.user, Community, ['member', 'manage'])
    if request.user.is_authenticated():
        messages = MessageCommunity.objects.select_related().filter(Q(communities__in=allowed_objects) | Q(
            users=request.user) | Q(owner=request.user), reply__isnull=True, pk=message_id)
    else:
        messages = MessageCommunity.objects.select_related().filter(Q(
            communities__in=allowed_objects), reply__isnull=True, pk=message_id)
    return messages


def get_followed_messages(request):
    if request.user.is_authenticated():
        messages = MessageCommunity.objects.select_related().filter(
            followers=request.user)
    else:
        return MessageCommunity.objects.none()
    return messages


def get_last_messages(request):
    if request.user.is_authenticated():
        messages = get_all_messages(
            request, 0, request.user.get_profile().last_activity)
    else:
        return MessageCommunity.objects.none()
    return messages


def get_member_messages(request, member):
    allowed_objects = get_allowed_objects(
        request.user, Community, ['member', 'manage'])
    messages = MessageCommunity.objects.select_related().filter(Q(users=member) | (Q(communities__in=allowed_objects) & (
        Q(owner=member) | Q(messagecommunity__owner=member) | Q(messagecommunity__users=member) | Q(users=member))))
    return messages


def get_contributor_messages(request, member):
    allowed_objects = get_allowed_objects(
        request.user, Community, ['member', 'manage'])
    # messages =
    # MessageCommunity.objects.select_related().filter(Q(communities__in=allowed_objects)
    # & (Q(owner=member)|Q(messagecommunity__owner=member)))
    messages = MessageCommunity.objects.select_related().filter(Q(communities__in=allowed_objects) & (
        Q(owner=member, reply__isnull=True) | Q(messagecommunity__owner=member)))
    return messages


def get_messages_extra_by_content_type(request, ct, community_id=0):
    allowed_objects = get_allowed_objects(
        request.user, Community, ['member', 'manage'])
    if request.user.is_authenticated():
        if community_id and int(community_id) in allowed_objects:
            messages = MessageCommunityExtra.objects.select_related().filter(Q(
                message__communities=community_id), message__reply__isnull=True, content_type=ct)
        else:
            messages = MessageCommunityExtra.objects.select_related().filter(Q(message__communities__in=allowed_objects) | Q(
                message__users=request.user) | Q(message__owner=request.user), message__reply__isnull=True, content_type=ct)
    else:
        if community_id and int(community_id) in allowed_objects:
            messages = MessageCommunityExtra.objects.select_related().filter(Q(
                message__communities=community_id), message__reply__isnull=True, content_type=ct)
        else:
            messages = MessageCommunityExtra.objects.select_related().filter(Q(
                message__communities__in=allowed_objects), message__reply__isnull=True, content_type=ct)

    return messages.distinct()


def get_messages_by_content_type(request, ct, community_id=0):
    allowed_objects = get_allowed_objects(
        request.user, Community, ['member', 'manage'])
    if request.user.is_authenticated():
        if community_id and int(community_id) in allowed_objects:
            messages = MessageCommunity.objects.select_related().filter(Q(communities=community_id) | Q(
                users=request.user) | Q(owner=request.user), messagecommunityextra__content_type=ct)
        else:
            messages = MessageCommunity.objects.select_related().filter(Q(communities__in=allowed_objects) | Q(
                users=request.user) | Q(owner=request.user), messagecommunityextra__content_type=ct)
    else:
        if community_id and int(community_id) in allowed_objects:
            messages = MessageCommunity.objects.select_related().filter(Q(
                communities=community_id), messagecommunityextra__content_type=ct)
        else:
            messages = MessageCommunity.objects.select_related().filter(Q(
                communities__in=allowed_objects), messagecommunityextra__content_type=ct)

    return messages.distinct()


def get_message_by_object(obj):
    return MessageCommunity.objects.get(messagecommunityextra__object_id=obj.pk, messagecommunityextra__content_type=ContentType.objects.get_for_model(obj))


def get_tome_messages(request):
    if request.user.is_authenticated():
        messages = MessageCommunity.objects.select_related().filter(
            users=request.user)
    else:
        return MessageCommunity.objects.none()
    return messages


def detete_message_community_extra(object, ct):
    MessageCommunityExtra.objects.filter(
        content_type=ct, object_id=object.pk).delete()


def add_community(name, description):
    try:
        com = Community.objects.get(name=name)
        return com
    except Community.DoesNotExist:
        try:
            com = Community(
                name=name, description=description, bgcolor='FF7400')
            com.save()
            get_community_calendar(com)
            return com
        except:
            return None
    return None


def get_message_attachments(message_id):
    ret = []
    try:
        path = os.path.join(get_upload_communities(), "%s" % message_id)
        files = os.listdir(path)
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isfile(fullpath):
                ret.append(f)
    except Exception:
        pass
    return ret
