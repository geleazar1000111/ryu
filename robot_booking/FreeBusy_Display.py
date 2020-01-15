"""A simple class that displays free time slots organized in a list. It takes in the robot id."""


class FreebusyDisplay:
    def __init__(self, robot_id):
        self.robot_id = robot_id

    def format_date(self, event_date):
        return "{}/{}/{}".format(event_date.month, event_date.day, event_date.year)

    def format_time(self, event_time):
        if event_time.hour < 12:
            return "{}:{:02d}AM".format(event_time.hour, event_time.minute)
        elif event_time.hour >= 12:
            pm_hour = event_time.hour
            if event_time.hour != 12:
                pm_hour -= 12
            return "{}:{:02d}PM".format(pm_hour, event_time.minute)

    def format_event_display(self, event, num):
        print("{}. {} is free on {} from {} to {}".format(num, self.robot_id, self.format_date(event['start'].date()), self.format_time(event['start'].time()), self.format_time(event['end'].time())))

    def display_free_events(self, free_events):
        if free_events:
            for num, event in enumerate(free_events, 1):
                self.format_event_display(event, num)
        else:
            print("{} is not available in this time range".format(self.robot_id))

    def display_freebusy(self, booked):
        if booked:
            for event in booked:
                print("{} is booked {} until {}".format(self.robot_id, event['start'], event['end']))
        else:
            print("{} is free in this time range".format(self.robot_id))
