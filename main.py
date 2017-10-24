import pandas as pd

from api import JirApi

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
    'original_estimate',
    'remaining_estimate',
    'time_spent',
]


def main():
    jira = JirApi()
    data_frame = pd.DataFrame(columns=HEADER)

    for issue in jira.all_issues():
        row_index = get_issue_key(issue)
        row_dict = parse_issue_json(issue)
        row = [row_dict[field] for field in HEADER]
        data_frame.loc[row_index] = row

    print(data_frame)


def parse_issue_json(issue):
    row_dict = {
        'key': issue['key'],
        'summary': issue['fields']['summary'],
        'issue_type': issue['fields']['issuetype']['name'],
        'components': ','.join([issue['fields']['components'][i]['name'] for i, obj in enumerate(issue['fields']['components'])]),
        'fix_versions': ','.join([issue['fields']['fixVersions'][i]['name'] for i, obj in enumerate(issue['fields']['fixVersions'])]),
        'reporter': issue['fields']['reporter']['displayName'],
        'assignee': issue['fields']['assignee']['displayName'],
        'created_datetime': issue['fields']['created'],
        'updated_datetime': issue['fields']['updated'],
        'resolved_datetime': issue['fields']['resolutiondate'],
        'status': issue['fields']['status']['name'],
        'labels': ','.join(issue['fields']['labels']),
        'original_estimate': issue['fields']['timetracking'].get('originalEstimateSeconds'),
        'remaining_estimate': issue['fields']['timetracking'].get('remainingEstimateSeconds'),
        'time_spent': issue['fields']['timetracking'].get('timeSpentSeconds'),
    }
    return row_dict


def get_issue_key(issue):
    return issue['key'].split('-')[-1]


if __name__ == '__main__':
    main()
