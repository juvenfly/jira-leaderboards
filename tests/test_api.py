from unittest import TestCase, mock

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

    @mock.patch('api.JirApi.store_state_json')
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
            print(issue)
            results.append(issue)

        self.assertEqual(len(results), 2)
