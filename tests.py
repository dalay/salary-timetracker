import os
from unittest import TestCase
import timetracker

class TimeTrackerTest(timetracker.TimeTracker):
    '''
    Needed to adapt some attributes of the timetracker class to the 
    test environment.
    '''
    CONGIFILE_NAME = 'timetracker.conf.test'
    CONFIG_ROOT = '/tmp'
    TRACKFILE_NAME = 'timetracker.csv.test'



class TimeTrackerTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = timetracker.create_parser()
        cls.basepath = os.path.dirname(os.path.abspath(__file__))
        cls.cmd_args = {
                'summary': ('-s',),
                'summary_log': ('--summary',),
                'write_log': ('log', '30', 'some comment...'),
                }

    def get_tt_object_with_args(self, args):
        '''
        Creating an object for testing.
        '''
        args = self.parser.parse_args(args)
        return TimeTrackerTest(args)

    def test_getting_stats(self):
        '''
        Check the summary based on previously recorded data.
        '''
        tt = self.get_tt_object_with_args(self.cmd_args['write_log'])
        with self.assertRaises(SystemExit) as se:
            self.get_tt_object_with_args(self.cmd_args['summary'])
            self.assertEqual(se.exception.code, timetracker.TRACK_FILE_NOTFOUND_EXIT_CODE)
        with self.assertRaises(SystemExit) as se:
            tt.write_data()
            self.assertEqual(se.exception.code, timetracker.ENTRY_ADDED_EXIT_CODE)
            self.get_tt_object_with_args(self.cmd_args['summary'])
            self.assertEqual(se.exception.code, timetracker.STATS_EXIT_CODE)
        os.remove(tt.filename)

    def test_trackfile_path_is_correct(self):
        '''
        Verify the correctness of the resulting path for the data file.
        '''
        tt = self.get_tt_object_with_args(self.cmd_args['write_log'])
        track_file_path = '%s/%s' % (self.basepath, tt.TRACKFILE_NAME)
        self.assertEqual(track_file_path, tt.filename)

    def test_trackfile_write_adding(self):
        '''
        Verify the addition of a record.
        '''
        tt = self.get_tt_object_with_args(self.cmd_args['write_log'])
        track_file_path = '%s/%s' % (self.basepath, tt.TRACKFILE_NAME)
        self.assertEqual(os.path.isfile(track_file_path), False)
        with self.assertRaises(SystemExit) as se:
            tt.write_data()
            self.assertEqual(se.exception.code, timetracker.ENTRY_ADDED_EXIT_CODE)
        self.assertEqual(os.path.isfile(track_file_path), True)
        os.remove(track_file_path)

    def test_entry_added(self):
        '''
        Data writing check.
        '''
        text = 'bla-bla comment'
        cmd_args = ('log', '60', text)
        tt = self.get_tt_object_with_args(cmd_args)
        with self.assertRaises(SystemExit):
            tt.write_data()
        with open(tt.filename, 'r') as f:
            self.assertIn(text, f.read())
        os.remove(tt.filename)
