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
        self.creds = self.get_creds()
        self.service = self.set_service()
        self.booked = self.get_freebusy()

    def run(self):
        self.display_events()
        if self.ask_to_book():
            self.book_event()

    def make_display(self):
        return FreebusyDisplay(self.robot_id)

    def make_booking(self):
        return FreebusyBooking(self.robot_id, self.booked, self.service)

    def book_event(self):
        new_booking = self.make_booking()
        new_booking.construct_and_book_event()

    def display_events(self):
        new_display = self.make_display()
        new_display.get_free_events(self.booked, self.start_year, self.start_month, self.start_day)
        new_display.display_free_events()
        #new_display.display_freebusy(self.booked)

    def ask_to_book(self):
        while True:
            user_inp = input("Would you like to book the robot? (y/n) ")
            if user_inp.lower() == 'y':
                return True
            elif user_inp.lower() == 'n':
                return False
            else:
                print("Invalid option (please type y or n) ")

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

    def set_service(self):
        return build('calendar', 'v3', credentials=self.creds)

    def get_freebusy(self):
        time_min = tz.localize(datetime(self.start_year, self.start_month, self.start_day))
        '''include 2nd day in time_max hence adding 17 hours'''
        time_max = tz.localize(datetime(self.end_year, self.end_month, self.end_day) + timedelta(hours=17))
        body = {
            "timeMin": time_min.isoformat(),
            "timeMax": time_max.isoformat(),
            "timeZone": 'US/Pacific',
            "items": [
                {
                    "id": robots[self.robot_id]
                }
            ]
        }

        events_result = self.service.freebusy().query(body=body).execute()
        calendar = events_result[u'calendars']
        booked = calendar[robots[self.robot_id]]['busy']
        return booked