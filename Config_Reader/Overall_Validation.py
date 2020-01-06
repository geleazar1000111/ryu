import argparse
import os
from Readers_Reporters.task_RR import Task_Reporter
from Readers_Reporters.datacollection_RR import Datacollection_Reporter

"""
This script run a overall diagnosis on Data Collection config. It checks whether the required settings for a specific DC task 
exist in the data collection config and then whether the parameters are legal or not.
"""
def get_args():
    parser = argparse.ArgumentParser(description='Please specify the task information yaml file and the root path of all config files')
    parser.add_argument("paths", nargs='+')
    return vars(parser.parse_args())

list_configs = ["policies/datacollection/config.yaml", "world.yaml", "hardware.yaml", "armcontrol.yaml"]

if __name__ == '__main__':
    args = get_args()
    paths = args["paths"]
    new_paths = []
    for path in paths:
        if path.find("DC") != -1:
            new_paths.append(path)
        elif path.find("/etc/odin") != -1 or path.find("odin") != -1:
            for config in list_configs:
                new_paths.append(os.path.join(path, config))
    task_reporter = Task_Reporter(new_paths)
    task_reporter.show_report()

    DC_reporter = Datacollection_Reporter(new_paths)
    DC_reporter.show_report()