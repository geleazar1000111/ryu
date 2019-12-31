from config_reader import Reader, Reporter
from world_RR import World_Reader, World_Reporter
from hardware_RR import  Hardware_Reader
from armcontrol_RR import Armcontrol_Reader
import os
import warnings
import numpy as np

os.environ.setdefault("ODIN_MESH_FOLDER", "/local/meshes/")

class Datacollcetion_Reader(Reader):

    def calibration_reader(self):
        return self.config["cached_calibrations"]

    def end_effector_reader(self):
        return self.config["tooltips"]["end_effectors"]

    def pick_model_reader(self):
        return self.config["models"]["pick_models"]

    def bin_model_reader(self):
        return self.config["models"]["bin_models"]

    def camera_setting_reader(self):
        """

        :return:
        A dict that the key is the bin setting name and the values are the name of cameras exist
        """
        camera_dict = {}
        camera_list = ["overcam_transform_name", "sidecam_transform_name", "wristcam_transform_name"]
        for bin in self.config["bins"]:
            cameras = [self.config["bins"][bin].get(camera, None) for camera in camera_list if self.config["bins"][bin].get(camera, None)]
            camera_dict[bin] = cameras

        return camera_dict

    def dof_reader(self):
        dofs = {}
        for bin in self.config["bins"]:
            dof = {}
            dof["handover_start_dofs_deg"] = self.config["bins"][bin]["handover_start_dofs_deg"]
            dof["handover_end_dofs_deg"] = self.config["bins"][bin]["handover_end_dofs_deg"]
            dofs[bin] = dof

        return dofs


class Datacollection_Reporter(Reporter):

    def show_report(self):
        print("Analyzing Data Collection config ......")
        print()
        self.show_end_effector()
        self.show_pick_models()
        self.show_bin_models()
        self.show_cached_calibration()
        self.show_camera_setting()
        self.show_dof()

    def create_reader(self):
        for path in self.paths:
            if path.find("datacollection/config.yaml") != -1:
                print ("Creating datacollection reader from: ", path)
                self.readers["datacollection"] = Datacollcetion_Reader(path)
            elif path.find("world.yaml") != -1:
                print("Creating world reader from", path)
                self.readers["world"] = World_Reader(path)
            elif path.find("hardware.yaml") != -1:
                print("Creating hardware reader from", path)
                self.readers["hardware"] = Hardware_Reader(path)
            elif path.find("armcontrol.yaml") != -1:
                print("Creating armcontrol reader from", path)
                self.readers["armcontrol"] = Armcontrol_Reader(path)
            elif path.find("mesh") != -1:
                os.environ["ODIN_MESH_FOLDER"] = path

        print()

    def create_decorator(self):
        for path in self.paths:
            if path.find("world.yaml") != -1:
                print("Creating affiliated world config reporter from ", path)
                self.decorators["world"] = World_Reporter(self.paths)

    def show_end_effector(self):
        end_effectors = self.readers["datacollection"].end_effector_reader()
        print("The end effectors listed are:")
        for end_effector in end_effectors:
            print(end_effector["name"])

        print()


    def show_pick_models(self):
        pick_models = self.readers["datacollection"].pick_model_reader()
        end_effectors = self.readers["datacollection"].end_effector_reader()
        print("The pick models listed are:")
        for pick_model in pick_models.keys():
            print(pick_model)
            #check if model directory exist
            model_path = pick_models[pick_model]["config"][0]["saved_model"]["saved_model_dir"]
            if not os.path.exists(model_path):
                warnings.warn("{} does not exist, please install the model!".format(model_path), Warning)
                print()

            #check if end effector in the enabled end effector list
            end_effector = pick_models[pick_model]["config"][0]["end_effector"]
            if end_effector not in [ee["name"] for ee in end_effectors]:
                warnings.warn("{} not listed in config, model : {} is not able to run!".format(end_effector, pick_model), Warning)
                print()

        print()

    def show_bin_models(self):
        bin_models = self.readers["datacollection"].bin_model_reader()
        print("The bin models listed are:")
        for bin_model in bin_models:
            print(bin_model)
            model_path = bin_models[bin_model]["config"]["saved_model_dir"]
            if not os.path.exists(model_path):
                warnings.warn("{} does not exist, please install the model!".format(model_path), Warning)
                print()

        print()

    def show_cached_calibration(self):
        print("These cameras have their calibration matrices enabled: ")
        calibrations = self.readers["datacollection"].calibration_reader()
        print(calibrations)
        if self.readers.get("hardware", None):
            camera_hardware = self.readers["hardware"].camera_setting_reader()
            for cali in calibrations:
                if cali not in camera_hardware:
                    warnings.warn("FATAL ERROR, camera not enabled in hardware.yaml! Please delete {} in DC config or Hardware config!".format(cali), Warning)

        print()

    def show_camera_setting(self):
        camera_dict = self.readers["datacollection"].camera_setting_reader()
        print("Show cameras enbaled for each bin")
        for bin in camera_dict.keys():
            print("For motion ", bin, ", the cameras enabled are: ", camera_dict[bin])
        if self.readers.get("hardware", None):
            camera_hardware = self.readers["hardware"].camera_setting_reader()
            for bin in camera_dict.keys():
                for cam in camera_dict[bin]:
                    if cam not in camera_hardware:
                        warnings.warn("FATAL ERROR, camera not enabled in hardware.yaml! Please delete {} in DC config or Hardware config!".format(cam), Warning)

        print()

    def show_dof(self):
        dofs = self.readers["datacollection"].dof_reader()
        break_flag = False
        for bin in dofs:
            start = dofs[bin]["handover_start_dofs_deg"]
            end = dofs[bin]["handover_end_dofs_deg"]
            if not all(np.equal(start, end)):
                warnings.warn("Please set start and end dofs for bin: {} as the same value, they are now different: {} {} ".format(bin, start, end))
                break_flag = True

        if self.readers.get("armcontrol", None) and not break_flag:
            limits = self.readers["armcontrol"].dof_reader()
            upper = limits["upper"]
            lower = limits["lower"]
            for bin in dofs:
                dof = dofs[bin]["handover_start_dofs_deg"]
                if not all([a < b for a, b in zip(dof, upper)]):
                    warnings.warn("Please modify the dof: {}, so it is below the upper limit: {}".format(dof, upper))
                    break_flag = True
                if not all([a > b for a, b in zip(dof, lower)]):
                    warnings.warn("Please modify the dof: {}, so it is above the lower limit: {}".format(dof, upper))
                    break_flag = True

        if self.decorators.get("world", None) and not break_flag:
            self.decorators["world"].create_world(os.environ["ODIN_MESH_FOLDER"])
            for bin in dofs:
                print("Checking dof for bin :", bin)
                self.decorators["world"].check_collision(dofs[bin]["handover_start_dofs_deg"])






