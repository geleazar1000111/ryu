from config_reader import Reader, Reporter
from hardware_RR import  Hardware_Reader
from datacollection_RR import Datacollcetion_Reader
from projectTooltip_RR import ProjectTooltip_Reader
import os
import numpy as np

class Calibrate_Reader(Reader):

    def end_effector_reader(self):
        pass

    def pick_model_reader(self):
        pass

    def bin_model_reader(self):
        pass

    def camera_setting_reader(self):
        camera = {}
        for policy in self.config["policy"]["kwargs"]["subpolicies"]:
            name = policy["~placeholder"]["name"]
            cam = policy["~placeholder"]["options"][0]["value"]["kwargs"]["camera"]["name"]
            trans = policy["~placeholder"]["options"][0]["value"]["kwargs"]["camera_transform_name"]
            camera[name] = {cam: trans}

        return camera

    def dof_reader(self):
        pass

# create a reader class to decide how to show reports. The reader class is also instantiated here
class Calibrate_Reporter(Reporter):



    def create_reader(self):
        for path in self.paths:
            if path.find("calibrate.yaml") != -1:
                print("Creating calibration reader from", path)
                self.readers["calibrate"] = Calibrate_Reader(path)
            elif path.find("hardware.yaml") != -1:
                print("Creating hardware reader from", path)
                self.readers["hardware"] = Hardware_Reader(path)
            elif path.find("datacollection/config.yaml") != -1:
                print ("Creating datacollection reader from: ", path)
                self.readers["datacollection"] = Datacollcetion_Reader(path)
            elif path.find("project_to_tooltip.yaml") != -1:
                print("Creating project_to_tooltip reader from", path)
                self.readers["projectTooltip"] = ProjectTooltip_Reader(path)

        print()

    def create_decorator(self):
        pass

    def show_report(self):
        print("Analyzing calibration config ......")
        print()
        self.show_camera_setting()
        self.check_cached_calibration()


    def show_end_effector(self):
        pass
        """implement end effector reporter here"""


    def show_pick_models(self):
        pass
        """implement pick models reporter here"""


    def show_bin_models(self):
        pass
        """implement bin models reporter here"""


    def show_camera_setting(self):
        cams = self.readers["calibrate"].camera_setting_reader()
        camera_hardware = None
        if self.readers.get("hardware", None):
            camera_hardware = self.readers["hardware"].camera_setting_reader()
        for cam_name in cams:
            cam = list(cams[cam_name])[0]
            transform = cams[cam_name][cam]
            print("In placeholder: {}, the camera name is : {}".format(cam_name, cam))
            if cam != transform:
                print("WARNING: In placeholder: {}, the camera name is {}, but the transform: {} is not matching with the camera selection!".format(cam, transform))
            if camera_hardware:
                if cam not in camera_hardware:
                    print("FATAL ERROR: camera not enabled in hardware.yaml! Please delete {} in DC config or Hardware config!".format(cam))

        print("Please check whether the placeholders are matching with the camera selections \n")

    def check_cached_calibration(self):
        cams = self.readers["calibrate"].camera_setting_reader()
        transformations = []
        for cam_name in cams:
            cam = list(cams[cam_name])[0]
            transform = cams[cam_name][cam]
            transformations.append(transform)

        if self.readers.get("datacollection", None):
            print("Checking enabled calibration in data collection config ......")
            calibrations = self.readers["datacollection"].calibration_reader()
            for cali in calibrations:
                if cali not in transformations:
                    print("WARNING: {} is enbaled in data collection config but not exists in calibration!".format(cali))

        if self.readers.get("projectTooltip", None):
            print("Checking enbaled calibration in project_to_tooltip.yaml ......")
            calibrations = self.readers["projectTooltip"].calibration_reader()
            for cali in calibrations:
                if cali not in transformations:
                    print("WARNING: {} is enbaled in project_to_tooltip.yaml but not exists in calibration!".format(cali))




