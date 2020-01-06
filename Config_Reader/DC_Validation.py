import argparse
from Readers_Reporters.datacollection_RR import Datacollection_Reporter


def get_args():
    parser = argparse.ArgumentParser(description='Please specify config path and mesh path. The order of the path is not essential. '
                                                 'Must have Data Collection config path, '
                                                 'configs such as World, Hardware, Armcontrol are optional but recommended')
    parser.add_argument("paths", nargs='+')
    return vars(parser.parse_args())

if __name__ == '__main__':
    args = get_args()
    paths = args["paths"]
    reporter = Datacollection_Reporter(paths)
    reporter.show_report()