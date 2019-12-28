from config_reader import Reader, Reporter
import os

class World_Reader(Reader):

    def end_effector_reader(self):
        robot = None
        for rob in self.robots:
            if rob in self.config.keys():
                robot = self.config[rob]
        return robot["mesh"]["path"]

    def pick_model_reader(self):
        pass

    def bin_model_reader(self):
        pass

    def bin_mesh_reader(self):
        return [self.config["a_bin"], self.config["b_bin"]]

    def camera_setting_reader(self):
        pass
