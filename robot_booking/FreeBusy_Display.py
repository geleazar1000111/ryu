class FreebusyDisplay:
    '''Where displaying events takes place'''
    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.free_events = {}

    def calculate_gap(self, prev_event, next_event):
        diff = next_event - prev_event
        diff_hours = diff.total_seconds() // 3600
        return diff_hours

    def make_free_event(self, num, start, end):
        if self.calculate_gap(start, end) >= 0.5:
            self.free_events[num] = {'start': start, 'end': end, 'duration': self.calculate_gap(start, end)}

    def get_free_events(self, booked, min_year, min_month, min_day):
        if booked:
            curstart = datetime(min_year, min_month, min_day, hour=9)
            for num, event in enumerate(booked):
                curdate = convert_google_datetime(event['start'])
                if curdate.date() == curstart.date():
                    curend = convert_google_datetime(event['start'])
                    self.make_free_event(num, curstart, curend)
                    curstart = convert_google_datetime(event['end'])
                else:
                    curstart = datetime(curdate.year, curdate.month, curdate.day, hour=9)
                    curend = convert_google_datetime(event['start'])
                    self.make_free_event(num, curstart, curend)
                    curstart = convert_google_datetime(event['end'])
            curend = datetime(curdate.year, curdate.month, curdate.day, hour=17)
            self.make_free_event(num, curstart, curend)

    def format_event_display(self, event):
        print("{} is free from {} to {}".format(self.robot_id, event['start'], event['end']))

    def display_free_events(self):
        for event in self.free_events:
            self.format_event_display(self.free_events[event])

    def display_freebusy(self, booked):
        if booked:
            for event in booked:
                print("{} is booked {} until {}".format(self.robot_id, event['start'], event['end']))
        else:
            print("{} is free in this time range".format(self.robot_id))