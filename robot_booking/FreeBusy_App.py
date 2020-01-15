"""This class connects to the Google calendar API service. It combines creation, display, and booking."""
#from __future__ import print_function
from __future__ import print_function
import re
#import argparse
from datetime import datetime, timedelta
import pytz
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import FreeBusy_Booking as fb_booking
import FreeBusy_Display as fb_display
import FreeBusyEvent_Builder as fb_builder


SCOPES = ['https://www.googleapis.com/auth/calendar']
tz = pytz.timezone('US/Pacific')


class FreebusyApp:
    '''Combines display and booking'''
    def __init__(self, robot_id, robots, start_date, end_date):
        self.robot_id = robot_id
        self.robots = robots
        self.start_month = start_date[0]
        self.start_day = start_date[1]
        self.start_year = start_date[2]
        self.end_month = end_date[0]
        self.end_day = end_date[1]
        self.end_year = end_date[2]
        self.creds = None
        self.service = None
        self.booked = None
        self.display = None
        self.booking = None
        self.free_event_builder = None

    def run(self):
        try:
            self.initialize()
            self.make_free_events()
            self.display_events()
            if self.ask_to_book():
                self.book_event()
            print("Script ran successfully")
        except:
            print("Script failed!")

    def initialize(self):
        self.creds = self.get_creds()
        self.set_service()
        self.booked = self.get_freebusy()
        self.display = fb_display.FreebusyDisplay(self.robot_id)
        self.booking = fb_booking.FreebusyBooking(self.robot_id, self.robots, self.service)
        self.free_event_builder = fb_builder.FreeBusyEventBuilder(self.robot_id)

    def set_service(self):
        self.service = build('calendar', 'v3', credentials=self.creds)

    def get_creds(self):
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

    def get_freebusy(self):
        time_min = tz.localize(datetime(self.start_year, self.start_month, self.start_day, hour=9))
        time_max = tz.localize(datetime(self.end_year, self.end_month, self.end_day, hour=17))
        body = {
            "timeMin": time_min.isoformat(),
            "timeMax": time_max.isoformat(),
            "timeZone": 'US/Pacific',
            "items": [
                {
                    "id": self.robots[self.robot_id]
                }
            ]
        }

        events_result = self.service.freebusy().query(body=body).execute()
        calendar = events_result[u'calendars']
        booked = calendar[self.robots[self.robot_id]]['busy']
        return booked

    def book_event(self):
        self.booking.construct_events_dict(self.free_event_builder.free_events)
        choice = self.ask_for_choice()
        self.booking.book_event(choice)

    def make_free_events(self):
        self.free_event_builder.initialize_free_events(self.booked, self.start_year, self.start_month, self.start_day, self.end_year, self.end_month, self.end_day)

    def display_events(self):
        self.display.display_free_events(self.free_event_builder.free_events)

    def ask_for_choice(self):
        while True:
            user_inp = input("Please input a number between 1 and the number of free events: ")
            if user_inp:
                assert isinstance(int(user_inp), int), "Invalid option"
                assert 1 <= int(user_inp) <= len(self.booking.free_events), "Index out of range"
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