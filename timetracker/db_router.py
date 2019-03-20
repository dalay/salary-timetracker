import os
import sys
import csv
import time
import datetime
import sqlite3
from prettytable import from_csv, PrettyTable
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
        new = not os.path.isfile(self.trackfile)
        hours = (data.pop('minutes') / 60)
        data['hours'] = '%.1f' % hours
        with open(self.trackfile, 'a+') as f:
            writer = csv.writer(f, delimiter=self.config['csv_delimiter'])
            if new:
                header = [s.capitalize() for s in data.keys()]
                writer.writerow(header)
            writer.writerow(data.values())
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

    def __init__(self, config):
        super().__init__(config)
        db_name = '%s.sqlite' % TRACKFILE_OR_DB_NAME
        self.db = os.path.join(self.git_root_dir, db_name)
        # if not os.path.isfile(self.db):
        #     self.create_table()
        self.connect = sqlite3.connect(self.db)
        self.cursor = self.connect.cursor()
        self.create_table()

    def query(self, sql, params=()):
        q = self.cursor.execute(sql, params)
        self.connect.commit()
        return q

    def __del__(self):
        self.connect.close()

    def create_table(self):
        sql = '''CREATE TABLE IF NOT EXISTS {}(
                        timestamp INTEGER PRIMARY KEY NOT NULL,
                        minutes INTEGER NOT NULL,
                        comment TEXT NULL)'''.format(TRACKFILE_OR_DB_NAME)
        self.query(sql)

    def write_data(self, data: dict):
        minutes = data.get('minutes')
        comment = data.get('comment')
        if minutes:
            sql = 'INSERT INTO {} (timestamp, minutes, comment) VALUES(?, ?, ?)'.format(
                TRACKFILE_OR_DB_NAME)
            params = [int(time.time()), int(minutes), comment]
            self.query(sql, params)
        else:
            sys.exit('No data to write')
        sys.exit(ENTRY_ADDED_EXIT_CODE)

    def make_prettytable(self):
        sql = "SELECT * FROM {}".format(TRACKFILE_OR_DB_NAME)
        q = self.query(sql)
        table = PrettyTable()
        table.field_names = ['Date', 'Start Time',
                             'End Time', 'Hours', 'Comment']
        for ts, minuts, comment in q.fetchall():
            hours = round((minuts / 60), 1)

            start_ts = (ts - (minuts * 60))

            start_time = datetime.datetime.fromtimestamp(
                start_ts).strftime('%H:%M')
            ts_time = datetime.datetime.fromtimestamp(ts)
            start_date = ts_time.strftime('%d.%m.%y')
            end_time = ts_time.strftime('%H:%M')

            table.add_row([start_date, start_time, end_time,
                           hours, comment or ''])

        table.align = 'l'
        return table

    def get_summary(self):
        sql = "SELECT SUM(minutes) FROM {}".format(TRACKFILE_OR_DB_NAME)
        q = self.query(sql)
        minutes = q.fetchone()[0]
        hours = (minutes / 60)
        sum = hours * self.config['hourly_rate']
        stats_msg = 'Hours worked: {0} | Salary: {1} {2} ({3} {2}/hour)'.format(
            round(hours, 1),
            int(sum),
            self.config['currency'],
            self.config['hourly_rate']
        )
        return stats_msg
