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
        pass
        """define method to read end effector setting"""

    @abc.abstractmethod
    def pick_model_reader(self):
        pass
        """define method to read pick model setting"""

    @abc.abstractmethod
    def bin_model_reader(self):
        pass
        """define method to read bin model setting"""

    @abc.abstractmethod
    def camera_setting_reader(self):
        pass
        """define method to read camera setting"""

    @abc.abstractmethod
    def dof_reader(self):
        pass
        """reader the hand over dofs from configs"""

# create a reader class to decide how to show reports. The reader class is also instantiated here
class Reporter(abc.ABC):
    def __init__(self, paths):
        """

        :param paths:
        A list of path because we may need multiple readers to compile a report.
        """
        self.paths = paths
        self.readers = {}
        self.decorators = {}
        self.create_reader()
        self.create_decorator()
        self.world = None



    @abc.abstractmethod
    def create_reader(self):
        pass
        """create the reader for this reporter"""

    @abc.abstractmethod
    def create_decorator(self):
        pass
        """create decorator reporters"""

    @abc.abstractmethod
    def show_report(self):
        pass
        """call the reports you want to show"""

    @abc.abstractmethod
    def show_end_effector(self):
        pass
        """implement end effector reporter here"""

    @abc.abstractmethod
    def show_pick_models(self):
        pass
        """implement pick models reporter here"""

    @abc.abstractmethod
    def show_bin_models(self):
        pass
        """implement bin models reporter here"""

    @abc.abstractmethod
    def show_camera_setting(self):
        pass
        """implement camera reporter here"""




