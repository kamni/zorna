from django.contrib.auth.models import User
from zorna.acl.models import get_allowed_objects
from zorna.calendars.models import ZornaCalendar

from zorna.calendars.models import EventDetails
from zorna.communities.models import Community
from zorna.site.models import SiteOptions


def get_user_calendars(user, permissions=['viewer']):
    allowed_objects = set([])
    for perm in permissions:
        objects = get_allowed_objects(user, ZornaCalendar, perm)
        allowed_objects = allowed_objects.union(set(objects))
    b_personal_calendar = SiteOptions.objects.is_access_valid(
        user, 'zorna_personal_calendar')
    if b_personal_calendar:
        pcal = get_personal_calendar(User.objects.get(pk=user.pk))
        allowed_objects.update([pcal.pk])
    allowed_objects = ZornaCalendar.objects.filter(pk__in=allowed_objects)
    exclude = []
    for obj in allowed_objects:
        if isinstance(obj.content_object, Community) and obj.content_object.enable_calendar is False:
            exclude.append(obj)
    return allowed_objects.exclude(pk__in=[obj.pk for obj in exclude])


def get_personal_calendar(user):
    user = User.objects.get(pk=user.pk)
    return ZornaCalendar.objects.get_or_create_calendar_for_object(user, user, distinction='owner', name=user.get_full_name())


def get_resource_calendar(resource):
    return ZornaCalendar.objects.get_or_create_calendar_for_object(None, resource, distinction='owner', name=resource.name)


def delete_event(event):
    instance_event_details = EventDetails.objects.get_eventdetails_for_object(
        event)
    instance_event_details.delete()
    event.delete()
    return True
