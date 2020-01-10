import FreeBusy_App as fb_app
import re
import argparse

valid_date = re.compile("[\d]{1,2}/[\d]{1,2}/[\d]{4}")


def get_args():
    parser = argparse.ArgumentParser(description='Check availability in time range and/or book robot calendar based '
                                                 'on that availability', epilog='Robot keys: VS, M-20, LR-MATE, IIWA, '
                                                                                'KR10, UR10, YASK, KWSK, IRB')
    parser.add_argument('robot name', type=str, help='name of robot i.e. VS, M-20, etc.')
    parser.add_argument('start date', type=str, help='start of range MM/DD/YYYY')
    parser.add_argument('end date', type=str, help='end of range MM/DD/YYYY')
    return vars(parser.parse_args())


def parse_date_from_args(datestr):
    return [int(x) for x in datestr.split("/")]


if __name__ == "__main__":
    args = get_args()
    robot_id = args['robot name']
    assert valid_date.match(
        args['start date']), "Invalid date format" '''TODO: use strftime. This will only check the format'''
    assert valid_date.match(args['end date']), "Invalid date format"
    start_date = parse_date_from_args(args['start date'])
    end_date = parse_date_from_args(args['end date'])
    app = fb_app.FreebusyApp(robot_id, start_date, end_date)
    app.run()
