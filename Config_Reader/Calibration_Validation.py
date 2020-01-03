import argparse
from calibrate_RR import Calibrate_Reporter

def get_args():
    parser = argparse.ArgumentParser(description='Please specify config path '
                                                 'Must have calibration config path')
    parser.add_argument("paths", nargs='+')
    return vars(parser.parse_args())

if __name__ == '__main__':
    args = get_args()
    paths = args["paths"]
    reporter = Calibrate_Reporter(paths)
    reporter.show_report()