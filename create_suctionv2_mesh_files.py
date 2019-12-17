"""Script to make suction tip kinbodies"""
import argparse
import shutil
import xml.etree.ElementTree as ET


def main():
    args = get_args()
    robot_name = args['robot name']
    radius = args['radius']
    height = args['height']
    translation = height / 2
    compressed = height - 20

    radius_mm = radius / 1000
    height_mm = height / 1000
    translation_mm = translation / 1000

    compressed_height_mm = compressed / 1000
    compressed_translation_mm = compressed_height_mm / 2

    '''TODO: replace with odin pathname'''
    tip_pathname = "/Users/geraldineeleazar/Desktop/tip_temps/tip_h{}_r{}_charuco.xml".format(height, radius)
    try:
        '''TODO: replace with odin pathname'''
        shutil.copy('/Users/geraldineeleazar/Desktop/tip_template.xml', tip_pathname)
    except shutil.Error as err:
        print(err)
    create_tip_kinbody(tip_pathname, radius_mm, height_mm, translation_mm, compressed_height_mm,
                       compressed_translation_mm)


def get_args():
    parser = argparse.ArgumentParser(description='Create suctionv2 tip kinbody .xml files and put them in '
                                                 'user-specified directory', epilog='List of robot file names in the '
                                                                                    'office: | VS: vs050 | IIWA: '
                                                                                    'iiwa14 | KR10: kr10 | Fanuc LR '
                                                                                    'Mate: lr_mate_200id_7l | M-20: '
                                                                                    'm-20ia | UR10: ur10')
    parser.add_argument('robot name', type=str, help='name of robot i.e. vs050, ur10, etc.')
    parser.add_argument('height', type=int, help='length of the tooltip')
    parser.add_argument('radius', type=int, help='radius of suction cup')
    return vars(parser.parse_args())


def create_tip_kinbody(pathname, radius_mm, height_mm, translation_mm, compressed_height_mm, compressed_translation_mm):
    tree = ET.parse(pathname)
    root = tree.getroot()
    for child in root.findall('Body'):
        if child.attrib['name'] == "link_suction_tube":
            geom_tag = child.find('Geom')
            geom_tag.find("Radius").text = str(radius_mm)
            geom_tag.find("Height").text = str(height_mm)
            geom_tag.find("Translation").text = "0 0 {}".format(str(translation_mm))
        elif child.attrib['name'] == "link_compressed_suction_tube":
            geom_tag = child.find('Geom')
            geom_tag.find("Radius").text = str(radius_mm)
            geom_tag.find("Height").text = str(compressed_height_mm)
            geom_tag.find("Translation").text = "0 0 {}".format(str(compressed_translation_mm))
        elif child.attrib['name'] == "frame_tooltip":
            child.find("Translation").text = "0 0 {}".format(str(height_mm))
        elif child.attrib['name'] == "frame_compressed_tooltip":
            child.find("Translation").text = "0 0 {}".format(str(height_mm))
    tree.write(pathname)


if __name__ == '__main__':
    main()
