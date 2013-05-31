import random
import hashlib
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from schedule.models.events import Calendar
from zorna.models import ZornaEntity

PRIVACY_TYPES = (
    (0, ugettext_noop(u'Default')),
    (1, ugettext_noop(u'Public')),
    (2, ugettext_noop(u'Private')),
)


class ZornaCalendarCategory(ZornaEntity):
    name = models.CharField(max_length=255)
    bgcolor = models.CharField(_('background color'), max_length=6)

    class Meta:
        verbose_name = _('calendar category')
        verbose_name_plural = _('calendar categories')
        db_table = settings.TABLE_PREFIX + "calendar_categories"

    def __unicode__(self):
        return self.name


class EventDetailsManager(models.Manager):

    def create_details(self, content_object, location='', free_busy=0, privacy=0, bgcolor='', category=None):
        ct = ContentType.objects.get_for_model(type(content_object))
        object_id = content_object.id
        evtd = EventDetails(
            content_type=ct,
            object_id=object_id,
            location=location,
            free_busy=free_busy,
            content_object=content_object,
            privacy=privacy,
            bgcolor=bgcolor,
            category=category
        )
        evtd.save()
        return evtd

    def get_eventdetails_for_object(self, obj):
        ct = ContentType.objects.get_for_model(type(obj))
        return self.get(object_id=obj.id, content_type=ct)


class EventDetails(models.Model):
    content_type = models.ForeignKey(ContentType, editable=False)
    object_id = models.IntegerField(editable=False)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    category = models.ForeignKey(ZornaCalendarCategory, null=True, blank=True)
    bgcolor = models.CharField(_('background color'), max_length=6, default='', blank=True, help_text=_(
        "If used, calendar category is ignored."))
    location = models.CharField(_('location'), max_length=100, blank=True)
    free_busy = models.BooleanField(_('Busy'), editable=True)
    privacy = models.IntegerField(_(
        'privacy'), max_length=1, choices=PRIVACY_TYPES, default=0)

    objects = EventDetailsManager()

    class Meta:
        verbose_name = _('Event details')
        verbose_name_plural = _("Event details")
        db_table = settings.TABLE_PREFIX + "eventdetails"


class ZornaCalendarManager(models.Manager):

    def get_calendar_for_object(self, obj, distinction=None):
        calendar = Calendar.objects.get_calendar_for_object(obj, distinction)
        return ZornaCalendar.objects.get(object_id=obj.pk, calendar=calendar)

    def get_or_create_calendar_for_object(self, user, content_object, distinction=None, name=None):
        calendar = Calendar.objects.get_or_create_calendar_for_object(
            content_object, distinction, name)
        try:
            return ZornaCalendar.objects.get(object_id=content_object.pk, calendar=calendar)
        except ZornaCalendar.DoesNotExist:
            zcalendar = ZornaCalendar(
                content_object=content_object, owner=user)
            zcalendar.calendar = calendar
            zcalendar.reset_secret_key()
            zcalendar.save()
            return zcalendar

    def get_calendars_for_object(self, obj, distinction=None):
        calendars = Calendar.objects.get_calendars_for_object(obj, distinction)
        return ZornaCalendar.objects.filter(object_id=obj.pk, calendar__in=calendars)


CALENDAR_WEEK_START_ON_CHOICES = (
    (0, _(u'Sunday')),
    (1, _(u'Monday')),
    (6, _(u'Saturday')),
)

CALENDAR_CUSTOM_VIEW_CHOICES = (
    ('agendaDay', _(u'Day')),
    ('agendaWeek', _(u'Week')),
    ('month', _(u'Month')),
)


class ZornaCalendar(ZornaEntity):
    calendar = models.ForeignKey(Calendar, editable=False)
    secret_key = models.CharField(_(
        'secret key'), max_length=40, editable=False, default='')
    ct_type = models.ForeignKey(ContentType, editable=False)
    object_id = models.IntegerField(editable=False)
    content_object = generic.GenericForeignKey('ct_type', 'object_id')
    custom_view = models.CharField(_(
        "custom view"), max_length=10, choices=CALENDAR_CUSTOM_VIEW_CHOICES, default='month')
    week_start_on = models.IntegerField(_(
        "week start on"), max_length=1, choices=CALENDAR_WEEK_START_ON_CHOICES, default='0')
    default_meeting_length = models.IntegerField(
        _("default meeting length"), max_length=2,
        choices=[(i, i)
                 for i in [10, 15, 20, 30, 45, 60, 120]],
        default='60', help_text=_("Default meeting length in minutes"))
    time_scale = models.IntegerField(_("default time scale"), max_length=2,
                                     choices=[(i, i) for i in [
                                              5, 10, 15, 30, 60]],
                                     default='60', help_text=_("Default time scale"))

    objects = ZornaCalendarManager()

    class Meta:
        verbose_name = _('zorna calendar')
        verbose_name_plural = _('zorna calendars')
        db_table = settings.TABLE_PREFIX + "calendars"

    def __unicode__(self):
        return unicode(self.content_object)

    def reset_secret_key(self):
        h = hashlib.sha1()
        h.update(str(random.random()))
        salt = h.hexdigest()[:5]
        h.update(salt + self.calendar.slug)
        self.secret_key = h.hexdigest()

    def get_acl_permissions():
        return {
            'viewer': ugettext_noop(u'Can view event details'),
            'manager': ugettext_noop(u'Can make change to events'),
            'creator': ugettext_noop(u'Can add new event'),
        }
    get_acl_permissions = staticmethod(get_acl_permissions)


class ZornaResourceCalendar(ZornaEntity):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        verbose_name = _('zorna resource calendar')
        verbose_name_plural = _('zorna resource calendars')
        db_table = settings.TABLE_PREFIX + "resource_calendars"

    def __unicode__(self):
        return unicode(self.name)
