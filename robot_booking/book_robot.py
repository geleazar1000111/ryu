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


def get_start(event):
    return event['start'].get('dateTime', event['start'].get('date'))


def get_end(event):
    return event['end'].get('dateTime', event['end'].get('date'))


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


def get_day_of_week(event_date):
    '''Uses this formula from https://cs.uwaterloo.ca/~alopez-o/math-faq/node73.html to determine day of week from date'''
    '''Monday = 1, Tuesday = 2, etc.'''
    day = event_date.day
    month = event_date.month
    year = event_date.year
    t = [0, 3, 2, 5, 0, 3,
         5, 1, 4, 6, 2, 4]
    year -= month < 3
    return ((year + int(year / 4) - int(year / 100)
             + int(year / 400) + t[month - 1] + day) % 7)


def ask_to_book():
    while True:
        user_inp = input("Would you like to book the robot? (y/n) ")
        if user_inp.lower() == 'y':
            return True
        elif user_inp.lower() == 'n':
            return False
        else:
            print("Invalid option (please type y or n) ")


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
    if booked:
        for event in booked:
            print("{} is booked {} until {}".format(robot_id, event['start'], event['end']))
        start_next_event = get_next_available(booked)
    else:
        print("{} is free in this time range".format(robot_id))
        start_next_event = time_min + timedelta(hours=9)
    if ask_to_book():
        construct_and_book_event(service, robot_id, start_next_event, add_hour_to_datetime(start_next_event))


def add_hour_to_datetime(curtime):
    return curtime + timedelta(hours=1)


def add_day_to_datetime(curtime):
    return curtime + timedelta(days=1)


def get_next_available(booked_events):
    '''This will get the next available 1 hr time slot'''
    if len(booked_events) == 1:
        event1_end = convert_google_datetime(booked_events[0]['end'])
        if event1_end.time() <= WORK_END:
            return event1_end
    for i in range(len(booked_events) - 1):
        event1_end = convert_google_datetime(booked_events[i]['end'])
        event2_start = convert_google_datetime(booked_events[i + 1]['start'])
        diff = event2_start - event1_end
        diff_hours = diff.total_seconds() // 3600
        if diff_hours >= 1:
            if event1_end.time() <= WORK_END:
                return event1_end


def construct_and_book_event(service, robot_id, start_event, end_event):
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
        'attendees': [{'email': robots[robot_id]}]
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('{} now booked for data collection from {} to {}'.format(robot_id, start_event, end_event))
    print('Link to event: {}'.format(event.get('htmlLink')))


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
    assert valid_date.match(args['start date']), "Invalid date format"
    assert valid_date.match(args['end date']), "Invalid date format"
    start_date = parse_date_from_args(args['start date'])
    end_date = parse_date_from_args(args['end date'])
    get_freebusy(robot_id, start_date[0], start_date[1], start_date[2], end_date[0], end_date[1], end_date[2])


if __name__ == '__main__':
    main()
