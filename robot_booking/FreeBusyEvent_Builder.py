from datetime import datetime, timedelta
import re


class FreeBusyEventBuilder:
    '''Where creating free event time slots takes place.'''

    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.is_available = 0
        self.days_in_range = {}
        self.free_events = []

    def construct_free_events(self):
        for day in self.days_in_range:
            curstart = self.days_in_range[day]['range']['start']
            if self.days_in_range[day]['booked']:
                for event in self.days_in_range[day]['booked']:
                    curend = event['start']
                    self.make_free_event(curstart, curend)
                    curstart = event['end']
                curend = self.days_in_range[day]['range']['end']
                self.make_free_event(curstart, curend)
            else:
                self.make_free_event(self.days_in_range[day]['range']['start'], self.days_in_range[day]['range']['end'])

    def initialize_free_events(self, booked, min_year, min_month, min_day, max_year, max_month, max_day):
        curstart = datetime(min_year, min_month, min_day, hour=9)
        curend = datetime(max_year, max_month, max_day, hour=17)
        self.fill_days(curstart, curend)
        for event in booked:
            event_start = convert_google_datetime(event['start'])
            event_end = convert_google_datetime(event['end'])
            self.days_in_range[event_start.date()]['booked'].append({'start': event_start, 'end': event_end})
        self.construct_free_events()

    def fill_days(self, start_range, end_range):
        delta = end_range - start_range
        for i in range(delta.days + 1):
            date = start_range + timedelta(days=i)
            date_start = date.replace(hour=9)
            date_end = date.replace(hour=17)
            self.days_in_range[date.date()] = {'range': {'start': date_start, 'end': date_end, 'duration': 8},
                                               'booked': []}

    def calculate_gap(self, prev_event, next_event):
        diff = next_event - prev_event
        diff_hours = diff.total_seconds() // 3600
        return diff_hours

    def make_free_event(self, start, end):
        if self.calculate_gap(start, end) >= 0.5:
            self.free_events.append({'start': start, 'end': end, 'duration': self.calculate_gap(start, end)})
            # self.free_events[start] = {'start': start, 'end': end, 'duration': self.calculate_gap(start, end)}

    def check_if_free(self, booked):
        if self.free_events:
            self.is_available = 1
        elif booked and not self.free_events:
            self.is_available = -1
        # else:
        #   self.is_available = 2


"""Helper Functions"""


def is_single_day_event(datetime_str):
    regex_obj = re.compile('.*-.*-.*T.*:.*:.*')
    if regex_obj.match(datetime_str):
        return True
    return False


def convert_google_datetime(datetime_str):
    if not is_single_day_event(datetime_str[:datetime_str.rfind("-")]):
        return datetime.strptime(datetime_str, '%Y-%m-%d')
    else:
        return datetime.strptime(datetime_str[:datetime_str.rfind("-")], '%Y-%m-%dT%H:%M:%S%f')