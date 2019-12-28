import json
import os

import yaml

import abc

# create a reader class to read essential information from configs and have interface to pass them.
# We need the config path to initialize a reader
class Reader(abc.ABC):
    def __init__(self, path):
        self.path = path
        with open(path) as f:
            contents = f.read()
            self.config = yaml.load(contents)

        #list all the robots name if the office, for read end effector path in world.yaml
        self.robots = ["lrmate200id_7l", "gp7", "kr10_r1100", "m-20ia", "ur10", "vs050"]

    @abc.abstractmethod
    def end_effector_reader(self):
        """define method to read end effector setting"""

    @abc.abstractmethod
    def pick_model_reader(self):
        """define method to read pick model setting"""

    @abc.abstractmethod
    def bin_model_reader(self):
        """define method to read bin model setting"""

    @abc.abstractmethod
    def camera_setting_reader(self):
        """define method to read camera setting"""

# create a reader class to decide how to show reports. The reader class is also instantiated here
class Reporter(abc.ABC):
    def __init__(self, paths):
        """

        :param paths:
        A list of path because we may need multiple readers to compile a report.
        """
        self.paths = paths
        self.readers = {}
        self.create_reader()
        self.camera_conversion = {}


    @abc.abstractmethod
    def create_reader(self):
        """create the reader for this reporter"""

    @abc.abstractmethod
    def show_report(self):
        """call the reports you want to show"""

    @abc.abstractmethod
    def show_end_effector(self):
        """implement end effector reporter here"""

    @abc.abstractmethod
    def show_pick_models(self):
        """implement pick models reporter here"""

    @abc.abstractmethod
    def show_bin_models(self):
        """implement bin models reporter here"""

    @abc.abstractmethod
    def show_camera_setting(self):
        """implement camera reporter here"""




