#!/usr/bin/env python3

import sys
import time
import os
import configparser
from functools import lru_cache
from subprocess import check_output, CalledProcessError
from argparse import ArgumentParser
from .db_router import get_db_driver


STATS_EXIT_CODE = 11


class TimeTracker(object):

    CONGIFILE_NAME = 'timetracker.conf'
    CONFIG_ROOT = '.config'
    TRACKFILE_NAME = 'timetracker.csv'

    defaults = {  # Dictionary containing default settings.
        'currency': 'USD',
        'hourly_rate': 20,
        'default_comment': '',
        'date_format': '%d %b %Y',
        'time_format': '%H:%M',
        'db_driver': 'csv',
        'csv_delimiter': ',',
    }

    def __init__(self, args):
        '''
        Initializations the git repository, configuration,
        and other required the class members.
        '''
        self.config = self.get_config()
        self.project_dir = self.get_git_root()
        self.trackfile = os.path.join(self.project_dir, self.TRACKFILE_NAME)
        self._db = get_db_driver(self.config)

        if args.summary:
            summary = self.get_summary()
            print(summary)
            sys.exit(STATS_EXIT_CODE)
        elif args.show_table:
            table = self.make_prettytable()
            print(table)
            sys.exit(STATS_EXIT_CODE)
        elif args.create_config:
            self.create_configfile_in_rootdir()
            sys.exit(STATS_EXIT_CODE)

        self.minutes, self.comment = (args.minutes, args.comments)

    @lru_cache(maxsize=30)
    def get_config(self):
        '''
        Get the current configuration of the application,
        depending on the user settings.

        Config file example:
        [main]
        currency = USD
        hourly_rate = 20
        default_comment = ''
        date_format = '%d %b %Y'
        time_format = '%H:%M'
        db_driver = 'csv'
        csv_delimiter = ','
        '''
        config = self.defaults

        # Config from the git project dir
        project_config = os.path.join(self.get_git_root(), self.CONGIFILE_NAME)
        # Config from the user conf dir
        user_config = os.path.join(os.path.expanduser("~"),
                                   self.CONFIG_ROOT, self.CONGIFILE_NAME)
        config_file = None
        for conf in (project_config, user_config):
            if os.path.isfile(conf):
                config_file = conf
                break

        if config_file is not None:
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
                        except ValueError:
                            continue
        return config

    def create_configfile_in_rootdir(self):
        if os.path.exists(self.trackfile):
            sys.exit('At the moment there is already data recorded in accordance with the settings of another configuration file. Creating a new settings file may damage this data and therefore the operation is canceled.')
        conf_path = os.path.join(self.project_dir, self.CONGIFILE_NAME)
        if not os.path.exists(conf_path):
            config = configparser.ConfigParser()
            config['main'] = {k: str(v).replace('%', '%%')
                              for k, v in self.config.items()}
            with open(conf_path, 'w') as f:
                config.write(f)

    def make_prettytable(self):
        return self._db.make_prettytable()

    def get_git_root(self):
        '''
        Return the absolute path to the root directory of the git-repository.
        '''
        try:
            base = check_output(['git', 'rev-parse', '--show-toplevel'])
        except CalledProcessError:
            sys.exit(
                'ERROR! At the moment you are not inside a git-repository!\nThe app finishes its work..')
        return base.decode('utf-8').strip()

    def collect_data(self):
        '''
        Formation of data for writing in the tracker log.
        '''
        start_datetime = time.localtime(time.time() - (int(self.minutes) * 60))
        log_date = time.strftime(self.config['date_format'], start_datetime)
        log_start_time = time.strftime(
            self.config['time_format'], start_datetime)
        log_end_time = time.strftime(
            self.config['time_format'], time.localtime())
        # log_comment = (''.join(self.comment)) or self.config['default_comment']
        log_comment = ''
        log_hours = '%.1f' % (self.minutes / 60)

        # Dict: Column Header -> Column Data
        return {
            'date': log_date,
            'start': log_start_time,
            'end': log_end_time,
            'comment': self.format_comment(log_comment, 60),
            'hours': log_hours
        }

    def format_comment(self, comment, max_line_length):
        if not comment:
            return
        # accumulated line length
        line_length = 0
        words = comment.split(" ")
        formatted_comment = ""
        for word in words:
            # if line_length + len(word) and a space is <= max_line_length
            if line_length + (len(word) + 1) <= max_line_length:
                # append the word and a space
                formatted_comment = formatted_comment + word + " "
                # length = length + length of word + length of space
                line_length = line_length + len(word) + 1
            else:
                # append a line break, then the word and a space
                formatted_comment = formatted_comment + "\n" + word + " "
                # reset counter of length to the length of a word and a space
                line_length = len(word) + 1
        return formatted_comment

    def write_data(self):
        '''
        Write data to the tracking log.
        '''
        data = self.collect_data()
        self._db.write_data(data)

    def get_summary(self):
        '''
        Geting statistics on time spent and money earned.
        '''
        return self._db.get_summary()


def get_log_from_input():
    '''
    If an application is invoked without any arguments,
    the data for a log is retrieved through an interactive session.
    '''
    while True:
        minutes = input(
            "Enter the working time (in minutes, Ctrl-C for cancel): ").strip()
        if not minutes.isdigit():
            print("No minutes have been entered. Try once more...")
            continue
        comment = input('Comment on the entry: ') or None
        print('Data was successfully added: Minutes - {}, Comment - {}'.format(minutes, comment))
        return [minutes, comment]


def create_parser():
    '''
    Creating a parser for an allowed arguments when calling the app
    through a command line interface.
    '''
    parser = ArgumentParser()
    parser.add_argument('-s', '--summary', action='store_true',
                        help='Show summary.')
    parser.add_argument('-t', '--show-table', action='store_true',
                        help='Show entries as formatted table(prettytable).')
    parser.add_argument('--create-config', action='store_true',
                        help='Create a configuration file with default settings in the project directory.')
    subparsers = parser.add_subparsers()

    log_parser = subparsers.add_parser('log',
                                       help='Create a new timetracker log record with time and comments(optional)')
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
