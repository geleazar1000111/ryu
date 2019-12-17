# ryu
Collection of various tools to help improve workflow

Current tools:
  - Tooltip mesh generator:
  
    This easily creates a new tooltip kinbody (.xml file) that doesn't require the user to manually copy, paste, and edit the file themselves. Since end effector lengths can change often during the data collection process, this script will save more time as the user only has to provide the robot name, height, and radius when running it. Some caveats:
    - So far, the user must edit the paths in the file so that reading and writing are from the correct locations. ```tip_template.xml```should be run from wherever the user stored it, while ```tip_h[]_r[]_charuco.xml``` should be specified in the user's local ```odin``` repo.
    - This script only creates the tip kinbody. It does not create files within ```prefab```. I figured that editing prefab files doesn't take too long, but if it also adds to the tediousness, I may adjust the script so that it also creates that prefab file.
    - The positional arguments ```robot name```, ```height```, and ```radius``` must be input in that order.
