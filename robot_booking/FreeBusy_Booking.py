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
class FreebusyBooking:
    '''Where booking takes place. Currently books the next available timeslot in given time range'''
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