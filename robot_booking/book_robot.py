from __future__ import print_function
import re
import argparse
from datetime import datetime, timedelta
import pytz
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

'''One hour padding in WORK_START and WORK_END. We still want the ability to book until 5pm and after 9am'''
UTC_OFFSET_TIMEDELTA = datetime.utcnow() - datetime.now()
WORK_START = datetime.strptime("10:00:00", "%H:%M:%S").time()
WORK_END = datetime.strptime("16:00:00", "%H:%M:%S").time()
SCOPES = ['https://www.googleapis.com/auth/calendar']
valid_date = re.compile("[\d]{1,2}/[\d]{1,2}/[\d]{4}")
tz = pytz.timezone('US/Pacific')
robots = {
    'VS': 'osaro.com_3138373730323034343235@resource.calendar.google.com',
    'LR-MATE': 'osaro.com_3438343531333034393639@resource.calendar.google.com',
    'M-20': 'osaro.com_32373736333937323031@resource.calendar.google.com',
    'IIWA': 'osaro.com_32323831353732373733@resource.calendar.google.com',
    'KR10': 'osaro.com_3137363632333931383736@resource.calendar.google.com',
    'UR10': 'osaro.com_383639353138393738@resource.calendar.google.com',
    'YASK': 'osaro.com_1887m7gjkdtjkiaoj5c7kc6rrtcg06gb6or3ie1i6gqj8d1p6s@resource.calendar.google.com',
    'KWSK': 'osaro.com_3637383431393334343032@resource.calendar.google.com',
    'IRB': 'osaro.com_3234333336343235363734@resource.calendar.google.com'
}


class FreebusyDisplay:
    '''Where displaying free events takes place'''
    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.is_available = 0
        self.free_events = []

    def fill_free_events(self, start_range, end_range):
        pass

    def get_free_events(self):
        return self.free_events

    def get_availability(self):
        return self.is_available

    def calculate_gap(self, prev_event, next_event):
        diff = next_event - prev_event
        diff_hours = diff.total_seconds() // 3600
        return diff_hours

    def make_free_event(self, start, end):
        if self.calculate_gap(start, end) >= 0.5:
            self.free_events.append({'start': start, 'end': end, 'duration': self.calculate_gap(start, end)})
            #self.free_events[start] = {'start': start, 'end': end, 'duration': self.calculate_gap(start, end)}

    def check_if_free(self, booked):
        if self.free_events:
            self.is_available = 1
        elif booked and not self.free_events:
            self.is_available = -1
        #else:
         #   self.is_available = 2

    def build_free_events(self, booked, min_year, min_month, min_day, max_year, max_month, max_day):
        curstart = datetime(min_year, min_month, min_day, hour=9)
        if booked:
            curstart = datetime(min_year, min_month, min_day, hour=9)
            curdate = curstart
            for event in booked:
                curdate = convert_google_datetime(event['start'])
                if curdate.date() == curstart.date():
                    curend = convert_google_datetime(event['start'])
                    self.make_free_event(curstart, curend)
                    curstart = convert_google_datetime(event['end'])
                else:
                    curstart = datetime(curdate.year, curdate.month, curdate.day, hour=9)
                    curend = convert_google_datetime(event['start'])
                    self.make_free_event(curstart, curend)
                    curstart = convert_google_datetime(event['end'])
            curend = datetime(curdate.year, curdate.month, curdate.day, hour=17)
            self.make_free_event(curstart, curend)
        else:
            curend = datetime(max_year, max_month, max_day, hour=17)
            delta = curend - curstart
            for i in range(delta.days + 1):
                date = curstart + timedelta(days=i)
                date_start = date.replace(hour=9)
                date_end = date.replace(hour=17)
                print(date_start, date_end)
                self.make_free_event(date_start, date_end)
        self.check_if_free(booked)

    def format_event_display(self, event):
        print("{} is free from {} to {}".format(self.robot_id, event['start'], event['end']))

    def display_free_events(self):
        if self.is_available < 0:
            print("{} is not free in this time range".format(self.robot_id))
        elif self.is_available == 1:
            for event in self.free_events:
                self.format_event_display(event)
        elif self.is_available == 2:
            print("{} is completely free in this time range".format(self.robot_id))

    def display_freebusy(self, booked):
        if booked:
            for event in booked:
                print("{} is booked {} until {}".format(self.robot_id, event['start'], event['end']))
        else:
            print("{} is free in this time range".format(self.robot_id))


class FreebusyBooking:
    '''Where booking takes place. Currently books the next available 1hr timeslot in given time range'''
    def __init__(self, robot_id, service):
        self.robot_id = robot_id
        self.service = service
        self.free_events = {}

    def construct_events_dict(self, free):
        for num, event in enumerate(free, 1):
            self.free_events[num] = event

    def construct_and_book_event_(self, choice):
        start_event = self.free_events[choice]['start']
        end_event = self.free_events[choice]['end']
        event = {
            'summary': 'Data Collection',
            'start': {
                'dateTime': start_event.isoformat(),
                'timeZone': 'US/Pacific',
            },
            'end': {
                'dateTime': end_event.isoformat(),
                'timeZone': 'US/Pacific',
            },
            'attendees': [{'email': robots[self.robot_id]}]
        }
        event = self.service.events().insert(calendarId='primary', body=event).execute()
        print('{} now booked for data collection from {} to {}'.format(self.robot_id, start_event, end_event))
        print('Link to event: {}'.format(event.get('htmlLink')))


class FreebusyApp:
    '''Combines display and booking'''
    def __init__(self, robot_id, start_date, end_date):
        self.robot_id = robot_id
        self.start_month = start_date[0]
        self.start_day = start_date[1]
        self.start_year = start_date[2]
        self.end_month = end_date[0]
        self.end_day = end_date[1]
        self.end_year = end_date[2]
        #self.creds = self.get_creds()
        #self.service = self.set_service()
        #self.booked = self.get_freebusy()
        self.display = FreebusyDisplay(self.robot_id)
        #self.booking = FreebusyBooking(self.robot_id, )

    def run(self):
        self.display_events()
        if self.ask_to_book():
            self.book_event()

    def book_event(self):
        self.booking.construct_events_dict(self.display.free_events)
        if self.display.get_availability() == 1:
            choice = self.ask_for_choice()
            self.booking.construct_and_book_event_(choice)
        elif self.display.get_availability() == 2:
            self.booking.construct_and_book_event_(1)

    def display_events(self, booked):
        self.display.build_free_events(booked, self.start_year, self.start_month, self.start_day, self.end_year, self.end_month, self.end_day)
        self.display.display_free_events()

    def ask_for_choice(self):
        while True:
            user_inp = input("Please input a number between 1 and the number of free events: ")
            if user_inp:
                assert isinstance(int(user_inp), int), "Invalid option"
                assert 1 <= int(user_inp) <= len(self.display.free_events), "Index out of range"
                return int(user_inp)
            else:
                return 1

    def ask_to_book(self):
        while True:
            user_inp = input("Would you like to book the robot? (y/n) ")
            if user_inp.lower() == 'y':
                return True
            elif user_inp.lower() == 'n':
                return False
            else:
                print("Invalid option (please type y or n) ")

def get_creds():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def get_freebusy(robot_id, start_month, start_day, start_year, end_month, end_day, end_year):
    creds = get_creds()
    service = build('calendar', 'v3', credentials=creds)
    time_min = tz.localize(datetime(start_year, start_month, start_day))
    time_max = tz.localize(datetime(end_year, end_month, end_day))
    body = {
        "timeMin": time_min.isoformat(),
        "timeMax": time_max.isoformat(),
        "timeZone": 'US/Pacific',
        "items": [
            {
                "id": robots[robot_id]
            }
        ]
    }

    events_result = service.freebusy().query(body=body).execute()
    calendar = events_result[u'calendars']
    booked = calendar[robots[robot_id]]['busy']
    return booked


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


def add_hour_to_datetime(curtime):
    return curtime + timedelta(hours=1)


def add_day_to_datetime(curtime):
    return curtime + timedelta(days=1)


def get_args():
    parser = argparse.ArgumentParser(description='Check availability in time range and/or book robot calendar based '
                                                 'on that availability', epilog='Robot keys: VS, M-20, LR-MATE, IIWA, '
                                                                                'KR10, UR10, YASK, KWSK, IRB')
    parser.add_argument('robot name', type=str, help='name of robot i.e. VS, M-20, etc.')
    parser.add_argument('start date', type=str, help='start of range MM/DD/YYYY')
    parser.add_argument('end date', type=str, help='end of range MM/DD/YYYY')
    return vars(parser.parse_args())


def parse_date_from_args(datestr):
    return [int(x) for x in datestr.split("/")]


def main():
    '''Input: start date, end date, robot'''
    args = get_args()
    robot_id = args['robot name']
    assert valid_date.match(args['start date']), "Invalid date format" '''TODO: use strftime. This will only check the format'''
    assert valid_date.match(args['end date']), "Invalid date format"
    start_date = parse_date_from_args(args['start date'])
    end_date = parse_date_from_args(args['end date'])
    freebusy_app = FreebusyApp(robot_id, start_date, end_date)
    booked = get_freebusy(robot_id, 1, 2, 2020, 1, 3, 2020)
    freebusy_app.display_events(booked)
    #freebusy_app.run()


if __name__ == '__main__':
    main()
