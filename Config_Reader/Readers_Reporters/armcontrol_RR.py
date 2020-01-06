from .config_reader import Reader, Reporter

import os
import warnings

class Armcontrol_Reader(Reader):
    def end_effector_reader(self):
        pass


    def pick_model_reader(self):
        pass

    def bin_model_reader(self):
        pass

    def camera_setting_reader(self):
        pass

    def dof_reader(self):
        limits = {}
        limits["lower"] = self.config["dof_limits_lower_deg"]
        limits["upper"] = self.config["dof_limits_upper_deg"]
        return limits