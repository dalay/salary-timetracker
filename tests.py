import os
from unittest import TestCase
import timetracker

class TimeTrackerTest(timetracker.TimeTracker):
    CONGIFILE_NAME = 'timetracker.conf.test'
    CONFIG_ROOT = '/tmp'
    TRACKFILE_NAME = 'timetracker.csv.test'
    defaults = { # Dictionary containing default settings.
            'currency': 'USD',
            'hourly_rate': 20,
            'default_comment': '',
            'date_format': '%d %b %Y', 
            'time_format': '%H:%M',
            'csv_delimiter': ',',
            }



class TimeTrackerTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = timetracker.create_parser()
        cls.basepath = os.path.dirname(os.path.abspath(__file__))

    # def setUp(self):
    #     self.tt = create_parser()


    # def test_with_empty_args(self):
    #     """
    #     User passes no args, should fail with SystemExit
    #     """
    #     with self.assertRaises(SystemExit):
    #         self.parser.parse_args([])

    def get_tt_object_with_args(self, *args):
        args = self.parser.parse_args([*args])
        return TimeTrackerTest(args)

    def test_getting_stats(self):
        tt = self.get_tt_object_with_args('log', '30', 'some comment...')
        with self.assertRaises(SystemExit) as se:
            self.get_tt_object_with_args('-s')
            self.assertEqual(se.exception.code, timetracker.TRACK_FILE_NOTFOUND_EXIT_CODE)
        with self.assertRaises(SystemExit) as se:
            tt.write_data()
            self.assertEqual(se.exception.code, timetracker.ENTRY_ADDED_EXIT_CODE)
            self.get_tt_object_with_args('-s')
            self.assertEqual(se.exception.code, timetracker.STATS_EXIT_CODE)
        os.remove(tt.filename)

    def test_trackfile_path_is_correct(self):
        tt = self.get_tt_object_with_args('log', '30', 'some comment...')
        track_file_path = '%s/%s' % (self.basepath, tt.TRACKFILE_NAME)
        self.assertEqual(track_file_path, tt.filename)

    def test_trackfile_write_adding(self):
        tt = self.get_tt_object_with_args('log', '30', 'some comment...')
        track_file_path = '%s/%s' % (self.basepath, tt.TRACKFILE_NAME)
        self.assertEqual(os.path.isfile(track_file_path), False)
        with self.assertRaises(SystemExit) as se:
            tt.write_data()
            self.assertEqual(se.exception.code, timetracker.ENTRY_ADDED_EXIT_CODE)
        self.assertEqual(os.path.isfile(track_file_path), True)
        os.remove(track_file_path)
