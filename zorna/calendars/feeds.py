import vobject

from django.http import HttpResponse

from schedule.models import Calendar
from zorna.calendars.models import ZornaCalendar

DAYS_NUMS = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']

EVENT_ITEMS = (
    ('uid', 'uid'),
    ('dtstart', 'start'),
    ('dtend', 'end'),
    ('summary', 'summary'),
    ('description', 'description'),
    ('location', 'location'),
    ('last_modified', 'last_modified'),
    ('created', 'created'),
    ('recurrence-id', 'recurrence_id'),
    ('rrule', 'rrule'),
)

class ZornaICalendarFeed(object):

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
        self.cal = vobject.iCalendar()

        for item in self.items():
            item.occ = None
            self.add_event(item)
            if item.rule:
                persisted_occurrences = item.occurrence_set.filter(cancelled=0)
                for po in persisted_occurrences:
                    item.occ = po
                    self.add_event(item)
            
        response = HttpResponse(self.cal.serialize(), mimetype='text/calendar')
        response['Filename'] = 'calendar.ics'  # IE needs this
        response['Content-Disposition'] = 'attachment; filename=calendar.ics'
        return response

    def add_event(self, item):
        event = self.cal.add('vevent')
        for vkey, key in EVENT_ITEMS:
            value = getattr(self, 'item_' + key)(item)
            if value:
                event.add(vkey).value = value
        

    def items(self):
        return []

    def item_uid(self, item):
        pass


    def item_start(self, item):
        pass

    def item_end(self, item):
        pass

    def item_summary(self, item):
        return str(item)

    def item_description(self, item):
        pass

    def item_location(self, item):
        pass

    def item_last_modified(self, item):
        pass

    def item_created(self, item):
        pass
    
    def item_rrule(self, item):
        pass

    def item_recurrence_id(self, item):
        pass
    
class ZornaCalendarICalendar(ZornaICalendarFeed):
    def items(self):
        cal_id = self.args[1]
        slug = self.args[1]
        key = self.args[2]
        try:
            zcal = ZornaCalendar.objects.get(calendar__slug=slug, secret_key=key)
            cal = zcal.calendar
        except:
            return Calendar.objects.none()
        return cal.events.all()

    def item_uid(self, item):
        return str(item.id)

    def item_start(self, item):
        if item.occ:
            return item.occ.start
        else:
            return item.start

    def item_end(self, item):
        if item.occ:
            return item.occ.end
        else:
            return item.end

    def item_summary(self, item):
        if item.occ:
            return item.occ.title
        else:
            return item.title
        
    def item_description(self, item):
        if item.occ:
            return item.occ.description
        else:
            return item.description

    def item_created(self, item):
        return item.created_on
    
    def item_rrule(self, item):
        rrule = ''
        if item.occ is None and item.rule:
            rrule = 'FREQ='+item.rule.frequency
            p = item.rule.params.split(';')
            for e in p:
                e = e.split(':')
                if e[0] == 'byweekday':
                    e[0] = 'BYDAY'
                rrule = rrule + ';'+e[0]+'='
                el= e[1].split(',')
                days = []
                for d in el:
                    days.append(DAYS_NUMS[int(d)])
                rrule = rrule + ','.join(days) 
            if item.end_recurring_period:
                rrule = rrule + ';UNTIL=' + item.end_recurring_period.strftime('%Y%m%dT%H%M%SZ')
            
        return rrule.upper()

    def item_recurrence_id(self, item):
        if item.occ:
            return item.occ.start
        return ''