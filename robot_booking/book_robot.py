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
import FreeBusy_App as fb_app

'''One hour padding in WORK_START and WORK_END. We still want the ability to book until 5pm and after 9am'''
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


def get_freebusy(robot_id, start_month, start_day, start_year, end_month, end_day, end_year):
    creds = get_creds()
    service = build('calendar', 'v3', credentials=creds)
    time_min = tz.localize(datetime(start_year, start_month, start_day, hour=9))
    time_max = tz.localize(datetime(end_year, end_month, end_day, hour=17))
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
    start_month = start_date[0]
    start_day = start_date[1]
    start_year = start_date[2]
    end_month = end_date[0]
    end_day = end_date[1]
    end_year = end_date[2]
    service = build('calendar', 'v3', credentials=get_creds())
    booked = get_freebusy(robot_id, start_month, start_day, start_year, end_month, end_day, end_year)
    freebusy_app = fb_app.FreebusyApp(robot_id, start_date, end_date, service, booked)
    """creds = get_creds()
    service  = build('calendar', 'v3', credentials=creds)
    curstart = datetime(2019, 12, 18, hour=9)
    curend = datetime(2019, 12, 20, hour=17)
    delta = curend - curstart
    free_events = []
    booked_events = []
    for i in range(delta.days + 1):
        date = curstart + timedelta(days=i)
        date_start = date.replace(hour=9)
        date_end = date.replace(hour=17)
        #print(date_start, date_start.year)
        booked = get_freebusy(service, robot_id, date.month, date.day, date.year) # date_end.month, date_end.day, date_end.year)
        if booked:
            #print(booked)
            booked_events += booked
        else:
            free_events.append((date_start, "free"))
    for event in free_events:
        print(event)"""


    freebusy_app.run()
    #freebusy_app.run()


if __name__ == '__main__':
    main()
