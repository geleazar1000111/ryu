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

    def bin_position_reader(self):
        bins = {}
        for key in self.config.keys():
            if key == "a_bin" or key == "b_bin":
                bins[key] = [self.config[key]["local_position"], self.config[key]["local_euler"]]

        return bins

class World_Reporter(Reporter):

    def create_reader(self):
        for path in self.paths:
            if path.find("world.yaml") != -1:
                #print("Creating world reader from", path)
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

    def check_pose_position(self, pos, motion, bin):
        robot = self.world._env.GetRobots()[0]
        robot.SetDOFValues(np.deg2rad(pos))
        tooltip_transform = robot.GetLink("frame_osaro_tooltip").GetTransform()[:3,3]
        bins = self.readers["world"].bin_mesh_reader()

        bin_transform = self.world._env.GetKinBody(bin).GetTransform()

        origin = bin_transform[:3,3]
        if tooltip_transform[2] < origin[2]:
            print("WARNING: {} motion for bin {} is too low!".format(motion, bin))
        else:
            print("The tooltip distance from the bin {} is {} mm".format(bin, (tooltip_transform[2] - origin[2]) * 1000))

        xyz_dimension = self.get_bin_size(bins[bin])
        xy_dimension_extend = np.ones(4)
        xy_dimension_extend[:3] = xyz_dimension
        xy_dimension_extend[2] = 0
        corner = np.dot(bin_transform, xy_dimension_extend)[:3]
        if motion == 'pick':
            if self.pose_within_bin(tooltip_transform[:2], origin[:2], corner[:2]):
                print(tooltip_transform[:2], origin[:2], corner[:2])
                print("WARNING: {} motion for bin {} is not away from the bin!".format(motion, bin))
        elif motion == 'place':
            if not self.pose_within_bin(tooltip_transform[:2], origin[:2], corner[:2]):
                print(tooltip_transform[:2], origin[:2], corner[:2])
                print("WARNING: {} motion for bin {} is not within the x y range of bin!".format(motion, bin))

        print()


    def pose_within_bin(self, tooltip_transform, origin, corner):
        for a, b, c in zip(tooltip_transform, origin, corner):
            if (a - b) * (a - c) >= 0:
                return False

        return True

    def get_bin_size(self, bin_path):
        """

        :param bin_path: The path of the bin mesh
        :return: A 3D array of the dimension of bin in [x, y, z] in mm
        """
        path = os.path.dirname(bin_path)

        dimension = []
        size = 0
        dim = ""
        for c in path[::-1]:
            if c == "_":
                break
            dim += c
        dim = dim[::-1]
        for i in range(0, len(dim) + 1):
            if i == len(dim):
                dimension.append(size)

            elif dim[i] == "x":
                dimension.append(size)
                size = 0
            else:
                size = size * 10 + int(dim[i])

        dimension = [dimension[0], dimension[1], dimension[2]]
        return np.divide(dimension, 1000)




    def show_bins(self):
        bins = self.readers["world"].bin_mesh_reader()
        bin_locations = self.readers["world"].bin_position_reader()
        for bin in bins:
            if not os.path.exists(os.path.join(os.environ["ODIN_MESH_FOLDER"], bins[bin])):
                print("WARNING: {} does not exist, please create and move the models in mesh directory:{} !".format(bins[bin], os.environ["ODIN_MESH_FOLDER"]))
                print()
                continue
            print("For bin {}, the x y z coordinate of its origin relative to the world is {}, and its rotation is {}.".format(bin_locations[bin][0], bin_locations[bin][1]))

        print("The origin of bin is the top left corner if it is not rotated. ")
        print("Please run bin bottom validation module to verify if the bin height setting is reasonable.")
        print("The tooltip robot should just touch the bottom of bin if you run it.")

        print()
