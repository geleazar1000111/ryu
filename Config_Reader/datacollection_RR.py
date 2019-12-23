from config_reader import Reader, Reporter
import os

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
        A dict that the keys are the bin pick/place process, the values are the camera tranforms exist
        """
        camera_dict = {}
        camera_list = ["overcam_transform_name", "sidecam_transform_name", "wristcam_transform_name"]
        for bin in self.config["bins"]:
            cameras = [camera for camera in camera_list if self.config["bins"][bin].get(camera, None)]
            camera_dict[bin] = cameras

        return camera_dict

class Datacollection_Reporter(Reporter):

    def show_report(self):
        self.show_end_effector()
        self.show_pick_models()

    def create_reader(self):
        for path in self.paths:
            if path.find("datacollection") != -1:
                print ("Creating datacollection reader from: ", path)
                self.readers["datacollection"] = Datacollcetion_Reader(path)

        print()

    def show_end_effector(self):
        end_effectors = self.readers["datacollection"].end_effector_reader()
        print("The end effectors listed are:")
        for end_effector in end_effectors:
            print(end_effector["name"])

        print()


    def show_pick_models(self):
        pick_models = self.readers["datacollection"].pick_model_reader()
        print("The models available listed are:")
        for pick_model in pick_models.keys():
            print(pick_model)
            model_path = pick_models[pick_model]["config"][0]["saved_model"]["saved_model_dir"]
            if not os.path.exists(model_path):
                print("WARNING: ", model_path, "does not exist, please install the model")

    def show_bin_models(self):
        pass

    def show_camera_setting(self):
        pass

