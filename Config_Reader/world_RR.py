from config_reader import Reader, Reporter
import os
import odin
import openravepy

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

    def dof_reader(self):
        pass

class World_Reporter(Reporter):

    def create_reader(self):
        for path in self.paths:
            if path.find("world.yaml") != -1:
                print("Creating world reader from", path)
                self.readers["world"] = World_Reader(path)

        print()

    def create_decorator(self):
        pass

    def show_report(self):
        print("Analyzing World config ......")

    def show_end_effector(self):
        pass

    def show_pick_models(self):
        pass

    def show_bin_models(self):
        pass

    def show_camera_setting(self):
        pass