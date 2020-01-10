class FreebusyDisplay:
    '''Where displaying free events takes place.'''
    def __init__(self, robot_id):
        self.robot_id = robot_id

    def format_event_display(self, event):
        print("{} is free from {} to {}".format(self.robot_id, event['start'], event['end']))

    def display_free_events(self, free_events):
        if free_events:
            for event in free_events:
                self.format_event_display(event)
        else:
            print("{} is not available in this time range".format(self.robot_id))

    def display_freebusy(self, booked):
        if booked:
            for event in booked:
                print("{} is booked {} until {}".format(self.robot_id, event['start'], event['end']))
        else:
            print("{} is free in this time range".format(self.robot_id))
