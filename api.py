import base64
import getpass
import json

import requests


class JirApi(object):
    def __init__(self, basic_auth=True):
        if basic_auth:
            username = input('Username: ')
            password = getpass.getpass('Password: ')
            self.access_token = base64.b64encode('{}:{}'.format(username, password))
            self.headers = {
                'Authorization': 'Basic {}'.format(self.access_token),
                'Content-Type': 'application/json',
            }

        self.domain = 'https://farmobile.atlassian.net/rest/api/2/issue/{}'
        self.project = 'FARM'
        self.more_to_pull = True
        self.found_ticket = False

    def all_issues(self):
        """
        Generator that yields issue json for each issue in a project
        :return:
        """
        issue_num = 1
        while self.more_to_pull:
            issue_key = '{}-{}'.format(self.project, issue_num)
            issue_num += 1
            issue_json = self.get_issue_json(issue_key)
            yield issue_json

    def get_issue_json(self, issue_key):
        """
        Returns json for a given issue if able or sets self.more_to_pull to False when done
        :param issue_key:
        :return:
        """
        url = self.domain.format(issue_key)
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            self.found_ticket = True
        elif resp.status_code == 404 and self.found_ticket:
            self.more_to_pull = False
            with open('state.json', 'w+') as state_file:
                state_json = json.loads(state_file)
                state_json['last_ticket_retrieved'] = issue_key
                json.dump(state_json, state_file)

        return resp.json()
