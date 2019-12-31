from config_reader import Reader, Reporter
import os

class Hardware_Reader(Reader):

    def end_effector_reader(self):
        pass

    def pick_model_reader(self):
        pass

    def bin_model_reader(self):
        pass

    def camera_setting_reader(self):
        cameras = {}
        for key in self.config.keys():
            if key.find("_rs") != -1:
                cameras[key] = self.config[key]

        return cameras

    def dof_reader(self):
        pass
