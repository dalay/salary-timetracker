#!/usr/bin/env python3

import sys
import time
import os
import csv
import configparser
from subprocess import check_output, CalledProcessError
from argparse import ArgumentParser


STATS_EXIT_CODE = 11
ENTRY_ADDED_EXIT_CODE = 22
TRACK_FILE_NOTFOUND_EXIT_CODE = 33


class TimeTracker(object):

    CONGIFILE_NAME = 'timetracker.conf'
    CONFIG_ROOT = '.config'
    TRACKFILE_NAME = 'timetracker.csv'
    defaults = { # Dictionary containing default settings.
            'currency': 'USD',
            'hourly_rate': 20,
            'default_comment': '',
            'date_format': '%d %b %Y', 
            'time_format': '%H:%M',
            'csv_delimiter': ',',
            }

    def __init__(self, args):
        '''
        Initializations the git repository, configuration, 
        and other required the class members.
        '''
        root_dir = self.get_git_root()
        self.config = self.get_config()
        filename = os.path.join(root_dir, self.TRACKFILE_NAME)
        if args.summary:
            summary = self.get_summary(filename)
            print(summary)
            sys.exit(STATS_EXIT_CODE)

        self.minutes, self.comment, self.filename = (args.minutes, 
                args.comments, filename)


    def get_config(self):
        '''
        Get the current configuration of the application, 
        depending on the user settings.
        '''
        config = self.defaults
        user_config = os.path.join(os.path.expanduser("~"),
                self.CONFIG_ROOT, self.CONGIFILE_NAME)
        config_file = user_config if os.path.isfile(user_config) else None
        if config_file:
            user_config = configparser.ConfigParser()
            user_config.read(config_file)
            if 'main' in user_config.sections():
                new_conf = user_config['main']
                for k in config.keys():
                    new_value = new_conf.get(k)
                    if new_value:
                        # Checking a user value for matching  needed type.
                        try:
                            config[k] = type(config[k])(new_value)
                        except ValueError: continue
        return config


    def get_git_root(self):
        '''
        Return the absolute path to the root directory of the git-repository.
        '''
        try:
            base = check_output(['git', 'rev-parse', '--show-toplevel'])
        except CalledProcessError:
            sys.exit('ERROR! At the moment you are not inside a git-repository!\nThe app finishes its work..')
        return base.decode('utf-8').strip()


    def get_summary(self, filename, col_index=4):
        '''
        Geting statistics on time spent and money earned.
        '''
        try:
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                next(reader) # Skip header
                hours = 0
                for row in reader:
                    hours += float(row[col_index])
                sum = hours * self.config['hourly_rate']
                stats_msg = 'Hours worked: {0} | Salary: {1} {2} ({3} {2}/hour)'.format(
                    round(hours, 2), 
                    int(sum), 
                    self.config['currency'], 
                    self.config['hourly_rate']
                    )
                return stats_msg
        except FileNotFoundError:
            print('Data file not found!')
            sys.exit(TRACK_FILE_NOTFOUND_EXIT_CODE)

    def collect_data(self):
        '''
        Formation of data for writing in the tracker log.
        '''
        start_datetime = time.localtime(time.time() - (int(self.minutes) * 60))
        log_date = time.strftime(self.config['date_format'], start_datetime)
        log_start_time = time.strftime(self.config['time_format'], start_datetime)
        log_end_time = time.strftime(self.config['time_format'], time.localtime())
        log_comment = (''.join(self.comment)) or self.config['default_comment']
        log_hours = '%.1f' % (self.minutes / 60)

        data = (log_date, log_start_time, log_end_time, log_comment, log_hours)
        return data

    def write_data(self):
        '''
        Write data to the tracking log.
        '''
        data = self.collect_data()
        new = not os.path.isfile(self.filename)
        with open(self.filename, 'a+') as f:
            writer = csv.writer(f, delimiter=self.config['csv_delimiter'])
            if new:
                header =('Date', 'Start', 'End', 'Comment', 'Hour(s)')
                writer.writerow(header)
            writer.writerow(data)
            print('Data was successfully added')
        sys.exit(ENTRY_ADDED_EXIT_CODE)





def get_log_from_input():
    '''
    If an application is invoked without any arguments, 
    the data for a log is retrieved through an interactive session.
    '''
    while True:
        minutes = input("Enter the working time (in minutes, Ctrl-C for cancel): ")
        if not minutes.isdigit():
            print("No minutes have been entered. Try once more...")
            continue
        comment = input('Comment on the entry: ') or None
        return [minutes, comment]

def create_parser():
    '''
    Creating a parser for an allowed arguments when calling the app 
    through a command line interface.
    '''
    parser = ArgumentParser()
    parser.add_argument('-s', '--summary', action='store_true',
            help='Show summary.')
    subparsers = parser.add_subparsers()

    log_parser = subparsers.add_parser('log',
            help='Create a new timetracker log record with time and comments(optional)' )
    log_parser.add_argument(
            'minutes', help='Time in minutes spent on work.', type=int)
    log_parser.add_argument(
            'comments', nargs='*', help='Commens on the work done (optional)')
    return parser

def parse_args():
    if len(sys.argv) < 2:
        argv = (['log'] + get_log_from_input())
    else:
        argv = sys.argv[1:]
    parser = create_parser()
    args = parser.parse_args(argv)
    return args


def main():
    try:
        args = parse_args()
        if args is not None:
            tt = TimeTracker(args)
            tt.write_data()
    except KeyboardInterrupt:
        sys.exit('\nCanceled by user')


if __name__ == '__main__':
    main()
