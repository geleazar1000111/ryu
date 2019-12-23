# isort:skip_file
import os

import click
import yaml

import numpy as np

import odin
import argparse
import openravepy

OPENRAVE_DATABASE = "../openravedb"
ODIN_MESH_FOLDER = None
TRAJOPT_LOG_THRESH = "WARN"
# Needs to be set before factory import
import odin.simulator.openrave.factory as factory  # noqa
import odin.simulator.openrave.utils as openrave_utils  # noqa
from odin.simulator.openrave.debugger import OpenRAVEDebugger  # noqa

def get_args():
    parser = argparse.ArgumentParser(description='Please specify mesh path and world.yaml location in global')
    parser.add_argument('path', type=str)
    return vars(parser.parse_args())

def _load_world(config_file, ODIN_MESH_FOLDER):
    with open(config_file) as f:
        config = yaml.load(f)
        if "world_config" in config:
            WORLD_CONFIG = config["world_config"]
        elif "world" in config:
            WORLD_CONFIG = config["world"]
        else:
            WORLD_CONFIG = config

    return factory.create_world_from_config(WORLD_CONFIG, ODIN_MESH_FOLDER)

@click.command()
@click.argument("world_file", type=click.Path(exists=True))
@click.argument("odin_mesh_folder", type=click.Path(exists=True))
def cli(world_file, odin_mesh_folder):
    """
        Load the given world file and open a visualization window. This script opens an IPython session,
        with predefined variables `world` and `plotter`. The former is of type `OpenRAVEWorld` and the
        latter is of type `OpenRAVEDebugger` (see `odin/simulator/openrave/debugger.py` for details).
        There's also a predefined convenience function `fanuc_decouple` for decoupling joint values
        from the fanuc pendant.  Another predefined convenience function `set_robot_dofs(world, dofs_deg)` sets the
        joint values for the robot in the world visualization
    """
    world = _load_world(world_file, odin_mesh_folder)
    world._env.SetViewer("qtcoin")  # Viewer

    # convenience function for decoupling joint values from fanuc pendant
    def fanuc_decouple(joints):
        joints = joints.copy()
        joints[2] += joints[1]
        return joints

    def set_robot_dofs(dofs_deg: np.ndarray):
        """Utility to set the dofs easily from the IPython console"""
        robot = world._env.GetRobots()[0]
        robot.SetDOFValues(np.deg2rad(dofs_deg))

    def get_distance_query():
        # NOT WORKING!
        report = openravepy.CollisionReport()
        env = world._env
        if not env.GetCollisionChecker().SetCollisionOptions(openravepy.CollisionOptions.Distance | openravepy.CollisionOptions.Contacts):
            print('current checker does not support distance, switching to pqp...')
            collisionChecker = openravepy.RaveCreateCollisionChecker(env, 'pqp')
            collisionChecker.SetCollisionOptions(openravepy.CollisionOptions.Distance | openravepy.CollisionOptions.Contacts)
            env.SetCollisionChecker(collisionChecker)
        env.CheckCollision(body1 = world._env.GetRobots()[0].GetLink('base_link_gripper'), body2 = world._env.GetKinBody("a_bin"), report = report)
        print('mindist: ',report.minDistance * 1000, "mm")




    # convenience object for plotting/drawing in the OpenRAVE renderer
    plotter = OpenRAVEDebugger(world)

    # robot = world._env.GetRobots()[0]

    import IPython; IPython.embed()  # noqa

if __name__ == '__main__':
    # Next 3 lines prevent "Floating point exception" when called with --help
    import openravepy
    openrave_utils.initialize_openrave()
    openravepy.Environment()
    cli()