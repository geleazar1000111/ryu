# ryu
Collection of various tools to help improve workflow

Current tools:
  - Tooltip mesh generator:```python create_suctionv2_mesh_files.py [robot name] [height] [radius]```
  
    This easily creates a new tooltip kinbody (.xml file) that doesn't require the user to manually copy, paste, and edit the file themselves. Since end effector lengths can change often during the data collection process, this script will save more time as the user only has to provide the robot name, height, and radius when running it. Some caveats:
    - So far, the user must edit the paths in the file so that reading and writing are from the correct locations. ```tip_template.xml```should be run from wherever the user stored it, while ```tip_h[]_r[]_charuco.xml``` should be specified in the user's local ```odin``` repo.
    - This script only creates the tip kinbody. It does not create files within ```prefab```. I figured that editing prefab files doesn't take too long, but if it also adds to the tediousness, I may adjust the script so that it also creates that prefab file.
    - The positional arguments ```robot name```, ```height```, and ```radius``` must be input in that order.
    - The .xml files are created by copying from the tip template and then modifying them. I think it would be more efficient to create the .xml files without copying them, but since these aren't very large files I don't think it's that big of a deal (for now).
    

  - Robot booking: ```python book_robot.py [robot key] [start date] [end date]```
    
    This checks for the availability of a specified robot within a time range. The user must specify the positional arguments robot key (listed with the ```--help``` option), the start date, and the end date (both in the format ```MM/DD/YYYY```) in that order. The script will list when the robot is free within that time range and will allow the user to book a free time slot per their request.
