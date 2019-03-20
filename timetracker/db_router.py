import os
import sys
import csv
from prettytable import from_csv
from subprocess import check_output, CalledProcessError

TRACKFILE_OR_DB_NAME = 'timetracker'
ENTRY_ADDED_EXIT_CODE = 22
TRACK_FILE_NOTFOUND_EXIT_CODE = 33


def file_not_found_action():
    print('Data file not found!')
    sys.exit(TRACK_FILE_NOTFOUND_EXIT_CODE)


def get_db_driver(config):
    driver = config.get('db_driver', 'csv')
    if driver == 'sqlite':
        return DbSqlite(config)
    elif driver == 'csv':
        return DbCsv(config)
    else:
        sys.exit('No driver database is specified')


class Db:

    def __init__(self, config):
        self.config = config
        self.git_root_dir = self.get_git_root()

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

    def write_data(self, data):
        '''
        Write data to the tracking log.
        '''
        pass

    def read_data(self):
        pass

    def get_summary(self):
        pass

    def make_prettytable(self):
        pass


class DbCsv(Db):

    def __init__(self, config):
        super().__init__(config)
        self.trackfile = os.path.join(
            self.git_root_dir, '{}.csv'.format(TRACKFILE_OR_DB_NAME))

    def write_data(self, data: dict):
        '''
        Write data to the tracking log.
        '''
        new = not os.path.isfile(self.trackfile)
        with open(self.trackfile, 'a+') as f:
            writer = csv.writer(f, delimiter=self.config['csv_delimiter'])
            if new:
                header = [s.capitalize() for s in data.keys()]
                writer.writerow(header)
            writer.writerow(data.values())
            print('Data was successfully added')
        sys.exit(ENTRY_ADDED_EXIT_CODE)

    def get_summary(self, col_index=4):
        try:
            with open(self.trackfile, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
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
            file_not_found_action()

    def make_prettytable(self):
        try:
            with open(self.trackfile, "r") as fp:
                table = from_csv(fp)
        except FileNotFoundError:
            file_not_found_action()
        else:
            table.align = 'l'
            return table


class DbSqlite(Db):
    pass
