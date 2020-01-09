class FreebusyBooking:
    '''Where booking takes place. Currently books the next available 1hr timeslot in given time range'''
    def __init__(self, robot_id, booked, service):
        self.robot_id = robot_id
        self.service = service
        self.booked = booked

    def get_next_available(self):
        '''This will get the next available 1 hr time slot'''
        '''TODO: bug fixes
            -need to check for edge cases'''
        if len(self.booked) == 1:
            event1_end = convert_google_datetime(self.booked[0]['end'])
            if event1_end.time() <= WORK_END:
                return event1_end
        for i in range(len(self.booked) - 1):
            event1_end = convert_google_datetime(self.booked[i]['end'])
            event2_start = convert_google_datetime(self.booked[i + 1]['start'])
            diff = event2_start - event1_end
            print(event1_end)
            diff_hours = diff.total_seconds() // 3600
            print(diff_hours)
            if diff_hours >= 1:
                if event1_end.time() <= WORK_END:
                    return event1_end

    def construct_and_book_event(self):
        start_event = self.get_next_available()
        end_event = add_hour_to_datetime(start_event)
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