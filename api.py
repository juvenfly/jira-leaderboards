import base64
import getpass
import json
import re

import requests

from constants import HEADER, FIELD_MAP, EXCLUDED_ISSUE_TYPES


class JirApi(object):
    def __init__(self, basic_auth=True, start_issue=1, end_issue=None):
        if basic_auth:
            username = input('Username: ')
            password = getpass.getpass('Password: ')
            self.access_token = base64.b64encode('{}:{}'.format(username, password).encode('ascii'))
            self.headers = {
                'Authorization': 'Basic {}'.format(self.access_token),
                'Content-Type': 'application/json',
            }

        self.start_issue = start_issue
        self.end_issue = end_issue
        self.domain = 'https://farmobile.atlassian.net/rest/api/2/issue/{}'
        self.project = 'FARM'
        self.more_to_pull = True
        self.found_ticket = False

    def all_issues(self):
        """
        Generator that yields issue json for each issue in a project
        :return: yields JIRA issue JSON
        """
        issue_num = self.start_issue
        while self.more_to_pull:
            if self.end_issue and issue_num > self.end_issue:
                break
            issue_key = '{}-{}'.format(self.project, issue_num)
            if issue_num % 50 == 0:
                print('Fetching Issue: {}'.format(issue_key))
            issue_num += 1
            issue_json = self.get_issue_json(issue_key)
            yield issue_json

    def get_issue_json(self, issue_key):
        """
        Returns json for a given issue if able or sets self.more_to_pull to False when done
        :param issue_key: JIRA issue key (e.g. EX-123)
        :return: response JSON
        """
        url = self.domain.format(issue_key)
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            self.found_ticket = True
        elif resp.status_code == 404 and self.found_ticket:
            self.more_to_pull = False
            store_state_json(issue_key)
        elif resp.status_code == 401:
            raise Exception('Unauthorized')

        try:
            result = resp.json()
        except Exception as e:
            print(resp.text)
            raise
        return result

    def collect_issues(self, data_frame):
        """
        Compile all issues from a given board into a pandas dataframe
        :param jirapi_conn: JirApi object
        :param data_frame: pandas data_frame in which to store JIRA issue data
        :return: pandas data_frame with all JIRA issue data
        """
        for issue in self.all_issues():
            row_index = get_issue_num(issue)
            row_dict = parse_issue_json(issue)
            if row_dict['issue_type'] not in EXCLUDED_ISSUE_TYPES:
                row = [row_dict[field] for field in HEADER]
                data_frame.loc[row_index] = row

        return data_frame


def parse_issue_json(issue):
    """
    Create a dict of values to be inserted into pandas data_frame
    :param issue: issue JSON from JirApi
    :return: unordered dict of row values
    """
    row_dict = {key: get_leaf_value(issue, FIELD_MAP[key]) for key in HEADER if key != 'sprints'}
    row_dict['sprints'] = get_sprint_info(issue, 'name')
    return row_dict


def get_leaf_value(issue_json, keys):
    """
    Descends JSON object based on list of keys and returns leaf value.
    :param issue_json: issue_json from JIRA API
    :param keys: list of keys in order from outermost to innermost
    :return: leaf value or None if there is a None-ish value anywhere along the way
    """
    result = issue_json
    for i, key in enumerate(keys):
        result = result.get(keys[i])
        if result is None:
            break
    if result and isinstance(result, list):
        if isinstance(result[0], str):
            result = ','.join(result)
        elif isinstance(result[0], dict):
            result = ','.join([result[i].get('name') for i, obj in enumerate(result)])

    return result


def execute_jql_query(jql_query):
    url = 'https://farmobile.atlassian.net/rest/api/2/search'
    params = {
        'jql': jql_query,
        'fields': 'all',
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def store_state_json(issue_key):
    with open('state.json', 'w+') as state_file:
        state_json = json.loads(state_file)
        state_json['last_ticket_retrieved'] = issue_key
        json.dump(state_json, state_file)


def get_sprint_info(issue, val_name):
    if val_name not in {'name', 'startDate', 'endDate'}:
        raise ValueError('val_name must be one of "name", "startDate", or "endDate"')
    try:
        sprints_string = issue['fields']['customfield_10004']
    except KeyError:
        return None
    regex_map = {
        'name': r'name=(.+),goal=',
        'startDate': r'startDate=(.+),endDate',
        'endDate': r'endDate=(.+),completedDate',
    }
    regex = regex_map[val_name]
    sprints = ','.join([re.search(regex, sprint).group(1) for sprint in sprints_string])

    return sprints


def get_issue_num(issue):
    return issue['key'].split('-')[-1]
