import argparse
from projectTooltip_RR import ProjectTooltip_Reporter
def get_args():
    parser = argparse.ArgumentParser(description='Please specify config path'
                                                 'Must have project_to_tooltip.yaml config path')
    parser.add_argument("paths", nargs='+')
    return vars(parser.parse_args())

if __name__ == '__main__':
    args = get_args()
    paths = args["paths"]
    reporter = ProjectTooltip_Reporter(paths)
    reporter.show_report()