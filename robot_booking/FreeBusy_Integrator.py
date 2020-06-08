"""This class combines building, displaying, and booking free events"""
import robot_booking.FreeBusy_Booking as fb_booking
import robot_booking.FreeBusy_Display as fb_display
import robot_booking.FreeBusyEvent_Builder as fb_builder

class FreeBusyIntegrator:
    def __init__(self, robot_id, robot_resource_name, service):
        self.robot_id = robot_id
        self.builder = fb_builder.FreeBusyEventBuilder(self.robot_id)
        self.booking = fb_booking.FreebusyBooking(service)
        self.display = fb_display.FreeBusyDisplay(robot_id)