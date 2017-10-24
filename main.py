import getpass

import pandas as pd
from jira import JIRA, JIRAError

HEADER = [
    'key',
    'summary',
    'issue_type',
    'components',
    'fix_versions',
    'reporter',
    'assignee',
    'created_datetime',
    'updated_datetime',
    'resolved_datetime',
    'status',
    'labels',
    # 'original_estimate',
    # 'remaining_estimate',
    # 'time_spent',
]


def main():
    username = input('Username: ')
    password = getpass.getpass('Password: ')
    jira = JIRA(options={"server": "https://farmobile.atlassian.net/"}, basic_auth=(username, password))
    i = 1000

    data_frame = pd.DataFrame(columns=HEADER)

    while True:
        try:
            row = []
            issue_key = 'FARM-{}'.format(i)

            issue = jira.issue(issue_key)
            row_dict = {
                'key': issue_key,
                'summary': issue.fields.summary,
                'issue_type': ','.join(issue.fields.labels),
                'components': issue.fields.priority.name,
                'fix_versions': ','.join([issue.fields.components[i].name for i, obj in enumerate(issue.fields.components)]),
                'reporter': issue.fields.reporter.name,
                'assignee': issue.fields.assignee.name,
                'created_datetime': issue.fields.created,
                'updated_datetime': issue.fields.updated,
                'resolved_datetime': issue.fields.resolutiondate,
                'status': issue.fields.status.name,
                'labels': ','.join(issue.fields.labels),
                # 'original_estimate': issue.fields.timetracking.originalEstimateSeconds,
                # 'remaining_estimate': issue.fields.timetracking.remainingEstimateSeconds,
                # 'time_spent': issue.fields.timetracking.timeSpentSeconds,
            }

            for field in HEADER:
                print('{}: {}'.format(field, row_dict[field]))
                row.append(row_dict[field])

            print(len(row))
            print(row)
            data_frame.loc[i] = row

            i += 1
            if i >= 1010:
                break

        except JIRAError as e:
            print('status_code: {}\ttext: {}'.format(e.status_code, e.text))
            break

    print(data_frame)


if __name__ == '__main__':
    main()
