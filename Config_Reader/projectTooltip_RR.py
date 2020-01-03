from config_reader import Reader, Reporter
from hardware_RR import  Hardware_Reader


class ProjectTooltip_Reader(Reader):

    def end_effector_reader(self):
        pass


    def pick_model_reader(self):
        pass
        """define method to read pick model setting"""


    def bin_model_reader(self):
        pass
        """define method to read bin model setting"""


    def camera_setting_reader(self):
        camera = {}
        for policy in self.config["policy"]["kwargs"]["subpolicies"]:
            if policy["kwargs"].get("camera", None) and policy["kwargs"].get("camera_transform_name", None):
                camera[policy["kwargs"].get("camera")["name"]] = policy["kwargs"].get("camera_transform_name")

        return camera


    def dof_reader(self):
        pass
        """reader the hand over dofs from configs"""

    def calibration_reader(self):
        calibrations = None
        for policy in self.config["policy"]["kwargs"]["subpolicies"]:
            if policy["kwargs"].get("transform_list", None):
                calibrations =  policy["kwargs"].get("transform_list", None)

        return calibrations


# create a reader class to decide how to show reports. The reader class is also instantiated here
class ProjectTooltip_Reporter(Reporter):

    def create_reader(self):
        for path in self.paths:
            if path.find("project_to_tooltip.yaml") != -1:
                print("Creating project_to_tooltip reader from", path)
                self.readers["projectTooltip"] = ProjectTooltip_Reader(path)
            elif path.find("hardware.yaml") != -1:
                print("Creating hardware reader from", path)
                self.readers["hardware"] = Hardware_Reader(path)

        print()


    def create_decorator(self):
        pass
        """create decorator reporters"""

    def show_report(self):
        print("Analyzing project_to_tooltip.yaml ......")
        self.show_camera_setting()

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
        cams = self.readers["projectTooltip"].camera_setting_reader()
        calibrations = self.readers["projectTooltip"].calibration_reader()
        camera_hardware = None
        if self.readers.get("hardware", None):
            camera_hardware = self.readers["hardware"].camera_setting_reader()
        for cam in cams:
            transform = cams[cam]
            print("For camera: {}, the transformation is: {}".format(cam, transform))
            if cam != transform:
                print("WARNING: The camera name is {}, but the transform: {} is not matching with the camera selection!".format(cam, transform))
            elif transform not in calibrations:
                print("WARNING: Transformation {} is not in the enabled transformation list!".format(transform))
            if camera_hardware:
                if cam not in camera_hardware:
                    print("FATAL ERROR: camera not enabled in hardware.yaml! Please delete {} in DC config or Hardware config!".format(cam))

        print()

