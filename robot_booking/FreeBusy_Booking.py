"""This purpose of this class is to book a given free timeslot. It takes in the robot id, robots dict, and the
Google Service. An object of this class needs to connect to the user's Google calendar to book an event."""


class FreebusyBooking:
    def __init__(self, robot_id, robots, service):
        self.robot_id = robot_id
        self.robots = robots
        self.service = service
        self.free_events = {}

    def construct_events_dict(self, free):
        for num, event in enumerate(free, 1):
            self.free_events[num] = event

    def book_event(self, choice):
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
            'attendees': [{'email': self.robots[self.robot_id]}]
        }
        #event = self.construct_event(choice)
        event = self.service.events().insert(calendarId='primary', body=event).execute()
        print('{} now booked for data collection from {} to {}'.format(self.robot_id, start_event, end_event))
        print('Link to event: {}'.format(event.get('htmlLink')))