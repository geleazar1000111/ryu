from .config_reader import Reader, Reporter
from .datacollection_RR import Datacollcetion_Reader
from .world_RR import  World_Reader
from .hardware_RR import Hardware_Reader
import json

import os

import yaml

class Task_Reader(Reader):
    def end_effector_reader(self):
        return self.config["End_Effectors"]


    def pick_model_reader(self):
        return self.config["Pick_Model"]


    def bin_model_reader(self):
        return self.config["Bin_Model"]


    def camera_setting_reader(self):
        return self.config["Cameras"]


    def dof_reader(self):
        pass
        """reader the hand over dofs from configs"""

    def bin_mesh_reader(self):
        return self.config["Bin_Meshes"]

# create a reader class to decide how to show reports. The reader class is also instantiated here
class Task_Reporter(Reporter):

    def create_reader(self):
        for path in self.paths:
            if path.find("DC") != -1:
                print ("Creating data collection task reader from: ", path)
                self.readers["task"] = Task_Reader(path)
            elif path.find("datacollection/config.yaml") != -1:
                print ("Creating datacollection reader from: ", path)
                self.readers["datacollection"] = Datacollcetion_Reader(path)
            elif path.find("world.yaml") != -1:
                print("Creating world reader from", path)
                self.readers["world"] = World_Reader(path)
            elif path.find("mesh") != -1:
                os.environ["ODIN_MESH_FOLDER"] = path
            elif path.find("hardware.yaml") != -1:
                print("Creating hardware reader from", path)
                self.readers["hardware"] = Hardware_Reader(path)

        print()
        print("-------------------------------------------------------------------------------------------")


    def create_decorator(self):
        pass
        """create decorator reporters"""


    def show_report(self):
        print("Analyzing DC Task .......")
        """call the reports you want to show"""
        self.show_end_effector()
        self.show_pick_models()
        self.show_bin_models()
        self.show_camera_setting()
        self.show_bin_meshes()
        self.show_camera_setting()

        print("IF YOU SEE NO WARNINGS ABOVE, YOU CAN START CHECKING OTHER CONFIGS\n")
        print("-------------------------------------------------------------------------------------------")


    def show_end_effector(self):
        config_ees = self.readers["datacollection"].end_effector_reader()
        for ee in self.readers["task"].end_effector_reader():
            if not any(ee == config_ee["name"] for config_ee in config_ees):
                print("WARNING: End effector {} is not included in data collection config! Please add it in the config file!\n".format(ee))

    def show_pick_models(self):
        config_pick_models = self.readers["datacollection"].pick_model_reader()
        model = self.readers["task"].pick_model_reader()
        if model not in config_pick_models.keys():
            print("WARNING: Specified pick model {} is not included in data collection config! Please install and include it in config file!\n".format(model))

    def show_bin_models(self):
        config_bin_models = self.readers["datacollection"].bin_model_reader()
        model = self.readers["task"].bin_model_reader()
        if model not in config_bin_models.keys():
            print("WARNING: Specified bin model {} is not included in data collection config! Please install and include it in config file!\n".format(model))

    def show_camera_setting(self):
        hardware_cam = self.readers["hardware"].camera_setting_reader()
        datacollection_cam = self.readers["datacollection"].calibration_reader()
        print()
        for cam in self.readers["task"].camera_setting_reader():
            if not any([key.find(cam) != -1 for key in hardware_cam.keys()]):
                print("WARNING: Specified camera {} is not enabled in Hardware config! Please add it!\n".format(cam))
            if not any([trans.find(cam) != -1 for trans in datacollection_cam]):
                print("WARNING: The transformation matrices for camera {} are not included in data collection config!\n".format(cam))


    def show_bin_meshes(self):
        config_bin_meshes = self.readers["world"].bin_mesh_reader()
        for bin in self.readers["task"].bin_mesh_reader():
            if not any([config_bin_meshes[bin_name].find(bin) != -1 for bin_name in config_bin_meshes]):
                print("WARNING: bin mesh {} is not included in world config! Please create and add it!\n".format(bin))

