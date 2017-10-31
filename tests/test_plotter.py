from unittest import TestCase

import pandas

import plotter


class TestPlotter(TestCase):

    def test__tally_bugs_by_sprint(self):
        data = [
            {'sprints': 'Sprint 1', 'issue_type': 'Task'},
            {'sprints': 'Sprint 1,Sprint 2', 'issue_type': 'Bug'},
            {'sprints': 'Sprint 2', 'issue_type': 'Bug'},
            {'sprints': 'Sprint 2,Sprint 3', 'issue_type': 'Task'},
            {'sprints': 'Sprint 3', 'issue_type': 'Bug'},
            {'sprints': None, 'issue_type': 'Bug'}
        ]
        data_frame = pandas.DataFrame(data)

        expected_tally = {
            'Sprint 1': 1,
            'Sprint 2': 2,
            'Sprint 3': 1,
        }
        expected_sprint_list = ['Sprint 1', 'Sprint 2', 'Sprint 3']
        actual_tally, actual_sprint_list = plotter._tally_bugs_by_sprint(data_frame)

        self.assertEqual(expected_tally, actual_tally)
        self.assertEqual(expected_sprint_list, actual_sprint_list)
