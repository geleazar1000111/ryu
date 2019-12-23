import json
import os

import yaml
import argparse

def load_datacollection_config(path):
    datacollection_config_path = path
    with open(datacollection_config_path) as f:
        contents = f.read()
        config = yaml.load(contents)

    return config

def get_args():
    parser = argparse.ArgumentParser(description='Read data collection policy config to do tests')
    parser.add_argument('path', type=str)
    return vars(parser.parse_args())

def main():
    args = get_args()
    config = load_datacollection_config(args['path'])
    pick_models = list(config['models']['pick_models'].keys())
    print(pick_models)

    calibration = config['cached_calibrations']
    print(type(calibration))

    print(config["tooltips"]["end_effectors"])

if __name__ == '__main__':
    main()

