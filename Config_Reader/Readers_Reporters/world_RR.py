from .config_reader import Reader, Reporter
import os
import numpy as np
import odin
import openravepy
import odin.simulator.openrave.factory as factory  # noqa
import warnings

OPENRAVE_DATABASE = "../openravedb"
os.environ.setdefault("ODIN_MESH_FOLDER", "/local/meshes/")

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

    def bin_mesh_reader(self):
        bins = {}
        for key in self.config.keys():
            if key == "a_bin" or key == "b_bin":
                bins[key] = self.config[key]["mesh"]["path"]

        return bins

class World_Reporter(Reporter):

    def create_reader(self):
        for path in self.paths:
            if path.find("world.yaml") != -1:
                print("Creating world reader from", path)
                self.readers["world"] = World_Reader(path)
            elif path.find("mesh") != -1:
                os.environ["ODIN_MESH_FOLDER"] = path

        print()

    def create_decorator(self):
        pass

    def show_report(self):
        print("Analyzing World config ......")
        print()
        self.show_end_effector()
        self.show_bins()

    def show_end_effector(self):
        end_effector = self.readers["world"].end_effector_reader()
        print("The end effector used is {}".format(end_effector))
        if not os.path.exists(os.path.join(os.environ["ODIN_MESH_FOLDER"], end_effector)):
            print(
                "WARNING: {} does not exist, please create and move the models in mesh directory:{} !".format(end_effector,
                                                                                                              os.environ[
                                                                                                                  "ODIN_MESH_FOLDER"]))
            print()

        print("Please check if the end effector with the correct radius and length is installed")
        print()

    def show_pick_models(self):
        pass

    def show_bin_models(self):
        pass

    def show_camera_setting(self):
        pass

    def create_world(self, ODIN_MESH_FOLDER):
        config = self.readers["world"].config
        if "world_config" in config:
            WORLD_CONFIG = config["world_config"]
        elif "world" in config:
            WORLD_CONFIG = config["world"]
        else:
            WORLD_CONFIG = config

        self.world = factory.create_world_from_config(WORLD_CONFIG, ODIN_MESH_FOLDER)

    def check_collision(self, pos):
        robot = self.world._env.GetRobots()[0]
        robot.SetDOFValues(np.deg2rad(pos))

        for bin in ["a_bin", "b_bin"]:
            bin = self.world._env.GetKinBody(bin)
            if self.world._env.CheckCollision(robot, bin):
                print("WARNING: robot is colliding with bin {}! Please jog the robot and change its handover pose!}".format(bin))
                print()

    def show_bins(self):
        bins = self.readers["world"].bin_mesh_reader()
        for bin in bins:
            print("For bin : {}, the bin path is: {}".format(bin, bins[bin]))
            if not os.path.exists(os.path.join(os.environ["ODIN_MESH_FOLDER"], bins[bin])):
                print("WARNING: {} does not exist, please create and move the models in mesh directory:{} !".format(bins[bin], os.environ["ODIN_MESH_FOLDER"]))
                print()

        print("Please check whether the bins are right ones in robot cell")

        print()
