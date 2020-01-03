import json
import os

import yaml

path = "/etc/odin/policies/develop/calibrate.yaml"

with open(path) as f:
    contents = f.read()
    config = yaml.load(contents)

print(config["policy"]["kwargs"]["subpolicies"])