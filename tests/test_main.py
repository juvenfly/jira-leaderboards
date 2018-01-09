from unittest import TestCase

import pandas
from numpy import array
from numpy.testing import assert_array_equal

import main


class TestMainHelpers(TestCase):

    @classmethod
    def setUpClass(cls):
        data = {
            'key': ['TEST-1', 'TEST-2', 'TEST-3'],
            'summary': ['foo bar baz', 'bar bar bar', ''],
            'descripiton': [
                'One morning, when Gregor Samsa woke from troubled dreams,',
                'he found himself transformed in his bed into a horrible vermin.',
                'He lay on his armour-like back, and if he lifted his head a little he could see his brown belly.',
            ],
            'issue_type': ['Epic', 'Task', 'Bug'],
            'components': ['', 'Data', 'Dashboard'],
            'fix_versions': ['', '4.8.0', '4.8.0'],
            'reporter': ['bob', 'jim', 'sally'],
            'assignee': ['Unassigned', 'sally', 'beth'],
            'created_datetime': [
                '2017-03-30T11:51:04.130-0500',
                '2017-03-30T11:51:04.130-0500',
                '2017-03-30T11:51:04.130-0500',
            ],
            'updated_datetime': [
                '2017-03-30T11:51:04.130-0500',
                '2017-03-30T11:51:04.130-0500',
                '2017-03-30T11:51:04.130-0500',
            ],
            'resolved_datetime': [
                '2017-03-30T11:51:04.130-0500',
                '2017-03-30T11:51:04.130-0500',
                '2017-03-30T11:51:04.130-0500',
            ],
            'status': ['Open', 'Resolved', 'In Progress'],
            'labels': ['', 'Boundaries', 'API'],
            'original_estimate': [None, 3600, 28800],
            'remaining_estimate': [None, 0, 14400],
            'time_spent': [None, 3600, 14400],
            'sprints': [None, 'Team 1 2017: 11/6 - 11/10', 'Team 22017: 11/6 - 11/10'],
        }
        cls.dataframe = pandas.DataFrame(data)

    @classmethod
    def tearDownClass(cls):
        cls.dataframe = None

    def test_convert_datetimes_to_ordinals(self):
        expected_results = {
            'created_datetime': 736418,
            'updated_datetime': 736418,
            'resolved_datetime': 736418,
        }

        dataframe = main.convert_datetimes_to_ordinals(self.dataframe)

        for column, result in expected_results.items():
            self.assertEqual(dataframe[column].iloc[0], result)

    def test_vectorize_text_fields(self):
        expected_results = {
            'descripiton': array(0.0),
            'summary': array(0.4736296010332684),
        }

        dataframe = main.vectorize_text_fields(self.dataframe)
        for column, result in expected_results.items():
            assert_array_equal(dataframe[column].iloc[0], result)
