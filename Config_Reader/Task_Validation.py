import argparse
from Readers_Reporters.task_RR import Task_Reporter
def get_args():
    parser = argparse.ArgumentParser(description='Please specify config path and mesh path. The order of the path is not essential. '
                                                 'Must have World config path')
    parser.add_argument("paths", nargs='+')
    return vars(parser.parse_args())

if __name__ == '__main__':
    args = get_args()
    paths = args["paths"]
    reporter = Task_Reporter(paths)
    reporter.show_report()