from config_reader import Reader, Reporter
from world_RR import World_Reader
from hardware_RR import  Hardware_Reader
import os
import warnings

os.environ.setdefault("ODIN_MESH_FOLDER", "/local/meshes")

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

class Datacollection_Reporter(Reporter):

    def show_report(self):
        self.show_end_effector()
        self.show_pick_models()
        self.show_bin_models()
        self.show_cached_calibration()
        self.show_camera_setting()

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

        print()

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
        camera_hardware = self.readers["hardware"].camera_setting_reader()

        print(calibrations)

        for cali in calibrations:
            if cali not in camera_hardware:
                warnings.warn("FATAL ERROR, camera not enabled in hardware.yaml! Please delete {} in DC config or Hardware config!".format(cali), Warning)

        print()

    def show_camera_setting(self):
        print("Show cameras enbaled for each bin")
        camera_dict = self.readers["datacollection"].camera_setting_reader()
        camera_hardware = self.readers["hardware"].camera_setting_reader()

        for bin in camera_dict.keys():
            print("For motion ", bin, ", the cameras enabled are: ", camera_dict[bin])
            for cam in camera_dict[bin]:
                if cam not in camera_hardware:
                    warnings.warn("FATAL ERROR, camera not enabled in hardware.yaml! Please delete {} in DC config or Hardware config!".format(cam), Warning)

        print()



