from unittest import TestCase, mock

import api
from api import JirApi


class TestJirApi(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.jira = JirApi(basic_auth=False)
        cls.jira.domain = 'http://www.test.test/{}'
        cls.jira.project = 'TEST'
        cls.jira.headers = {'headers': 'test'}

    @classmethod
    def tearDownClass(cls):
        cls.jira = None

    def setUp(self):
        self.jira.found_ticket = False
        self.jira.start_issue = 1
        self.jira.end_issue = 3

    @mock.patch('api.store_state_json')
    @mock.patch('api.requests.get')
    def test_get_issue_json(self, mock_get, mock_store):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'return': 'me'}

        result = self.jira.get_issue_json('TEST-123')
        self.assertEqual(result, {'return': 'me'})

        mock_get.return_value.status_code = 404
        self.jira.found_ticket = True
        self.jira.get_issue_json('TEST-123')
        mock_store.assert_called_with('TEST-123')

        self.jira.found_ticket = False
        result = self.jira.get_issue_json('TEST-123')
        self.assertEqual(result, {'return': 'me'})

        mock_get.return_value.status_code = 401
        # TODO: broad exception, this is bad
        with self.assertRaises(Exception):
            self.jira.get_issue_json('TEST-123')

    @mock.patch('api.JirApi.get_issue_json')
    def test_all_issues(self, mock_get_issue_json):
        responses = [
            {'return': {'me': '1'}},
            {'return': {'me': '2'}},
            {'return': {'me': '3'}},
        ]
        mock_get_issue_json.side_effect = responses

        for i, issue in enumerate(self.jira.all_issues()):
            self.assertEqual(issue, responses[i])

    @mock.patch('api.JirApi.get_issue_json')
    def test_all_issues_end_issue(self, mock_get_issue_json):
        responses = [
            {'return': {'me': '1'}},
            {'return': {'me': '2'}},
            {'return': {'me': '3'}},
        ]
        mock_get_issue_json.side_effect = responses
        self.jira.end_issue = 2
        results = []
        for i, issue in enumerate(self.jira.all_issues()):
            results.append(issue)

        self.assertEqual(len(results), 2)

    @mock.patch('api.JirApi.get_issue_json')
    def test_all_issues_start_issue(self, mock_get_issue_json):
        responses = [
            {'return': {'me': '1'}},
            {'return': {'me': '2'}},
            {'return': {'me': '3'}},
        ]
        mock_get_issue_json.side_effect = responses
        self.jira.start_issue = 2
        results = []
        for i, issue in enumerate(self.jira.all_issues()):
            results.append(issue)

        self.assertEqual(len(results), 2)


class TestJirApiHelpers(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_json = {
            "key": "TEST-123",
            "fields": {
                "summary": "return_summary",
                "issuetype": {"other_stuff": "don't_return_me", "name": "return_issuetype"},
                "components": [
                    {"other_stuff": "don't_return_me", "name": "return_component"}
                ],
                "fixVersions": [
                    {"other_stuff": "don't_return_me", "name": "return_fixVersions"}
                ],
                "reporter": {"other_stuff": "don't_return_me", "name": "return_reporter"},
                "assignee": {"other_stuff": "don't_return_me", "name": "return_assignee"},
                "created": "return_created",
                "updated": "return_updated",
                "resolutiondate": "return_resolutiondate",
                "status": {"other_stuff": "don't_return_me", "name": "return_status"},
                "labels": ["return_label"],
                "timetracking": {
                    "originalEstimate": "don't_return_me",
                    "remainingEstimate": "don't_return_me",
                    "timeSpent": "don't_return_me",
                    "originalEstimateSeconds": "return_originalEstimateSeconds",
                    "remainingEstimateSeconds": "return_remainingEstimateSeconds",
                    "timeSpentSeconds": "return_timeSpentSeconds",
                },
                "customfield_10004": [
                    "com.atlassian.greenhopper.service.sprint.Sprint@5a1b0835[id=56,rapidViewId=37,state=CLOSED,name=Total pkg 2017: 10/23 - 10/27,goal=,startDate=2017-10-23T14:09:09.683Z,endDate=2017-10-30T14:09:00.000Z,completeDate=2017-10-30T17:05:27.549Z,sequence=56]",
                    "com.atlassian.greenhopper.service.sprint.Sprint@18508c4a[id=59,rapidViewId=37,state=ACTIVE,name=Total pkg 2017: 10/30 - 11/3,goal=,startDate=2017-10-30T17:06:02.051Z,endDate=2017-11-06T18:06:00.000Z,completeDate=<null>,sequence=59]"
                ],
            }
        }

    def test_parse_issue_json(self):

        expected_outocmes = {
            'key': 'TEST-123',
            'summary': 'return_summary',
            'issue_type': 'return_issuetype',
            'components': 'return_component',
            'fix_versions': 'return_fixVersions',
            'reporter': 'return_reporter',
            'assignee': 'return_assignee',
            'created_datetime': 'return_created',
            'updated_datetime': 'return_updated',
            'resolved_datetime': 'return_resolutiondate',
            'status': 'return_status',
            'labels': 'return_label',
            'original_estimate': 'return_originalEstimateSeconds',
            'remaining_estimate': 'return_remainingEstimateSeconds',
            'time_spent': 'return_timeSpentSeconds',
            'sprints': 'Total pkg 2017: 10/23 - 10/27,Total pkg 2017: 10/30 - 11/3',
        }

        for key, outcome in expected_outocmes.items():
            result = api.parse_issue_json(self.test_json)[key]
            self.assertEqual(result, expected_outocmes[key])

        json_with_nulls = {
            "key": "TEST-234",
            "fields": {
                "timetracking": {
                    "originalEstimateSeconds": None,
                }
            }
        }

        expected_outcomes = {
            "key": "TEST-234",
            "original_estimate": None,
        }
        for key, outcome in expected_outcomes.items():
            result = api.parse_issue_json(json_with_nulls)[key]
            self.assertEqual(result, expected_outcomes[key])

    def test_get_leaf_value(self):
        test_json = {
            'depth_1': 'return_me',
            'depth_2_1': {
                'depth_2_2': 'return_me'
            },
            'list_leaf_1': {
                'list_leaf_2': ['return', 'me'],
            },
            'broken': {
                None: "don't return me"
            },
            'broken_2': "don't return me"
        }

        good_keys = [
            ['depth_1'],
            ['depth_2_1', 'depth_2_2'],
        ]
        list_keys = [
            ['list_leaf_1', 'list_leaf_2'],
        ]
        fail_keys = [
            ['broken', 'broken_2'],
            ['does', 'not', 'exist'],
        ]

        for key_list in good_keys:
            self.assertEqual(api.get_leaf_value(test_json, key_list), 'return_me')

        for key_list in list_keys:
            self.assertEqual(api.get_leaf_value(test_json, key_list), 'return,me')

        for key_list in fail_keys:
            self.assertIsNone(api.get_leaf_value(test_json, key_list))

    def test_get_sprint_info(self):
        no_sprint_string_json = {
            "fields": {
                "some_fields": "non_sprint_data",
            }
        }

        # TODO: Test other values of val_name
        self.assertIsNone(api.get_sprint_info(no_sprint_string_json, 'name'))

        expected_result = 'Total pkg 2017: 10/23 - 10/27,Total pkg 2017: 10/30 - 11/3'
        result = api.get_sprint_info(self.test_json, 'name')
        self.assertEqual(result, expected_result)
