import re

import pandas as pd

from api import JirApi
from plotter import time_estimates_plot

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
    'sprints',
]

FIELD_MAP = {
    'key': ['key'],
    'summary': ['fields', 'summary'],
    'issue_type': ['fields', 'issuetype', 'name'],
    'components': ['fields', 'components'],
    'fix_versions': ['fields', 'fixVersions'],
    'reporter': ['fields', 'reporter', 'name'],
    'assignee': ['fields', 'assignee', 'name'],
    'created_datetime': ['fields', 'created'],
    'updated_datetime': ['fields', 'updated'],
    'resolved_datetime': ['fields', 'resolutiondate'],
    'status': ['fields', 'status', 'name'],
    'labels': ['fields', 'labels'],
    'original_estimate': ['fields', 'timetracking', 'originalEstimateSeconds'],
    'remaining_estimate': ['fields', 'timetracking', 'remainingEstimateSeconds'],
    'time_spent': ['fields', 'timetracking', 'timeSpentSeconds'],
    'sprints': ['fields', 'customfield_10004']
}


def main():
    jira = JirApi(start_issue=4300, end_issue=5000)
    try:
        data_frame = pd.DataFrame.from_csv('issues.csv')
    except FileNotFoundError:
        data_frame = pd.DataFrame(columns=HEADER)

    # data_frame = collect_issues(jira, data_frame)

    # data_frame.to_csv('issues.csv')
    calc_average_time_est_error(data_frame)
    time_estimates_plot(data_frame, xrange=[jira.start_issue, jira.end_issue])


def calc_average_time_est_error(data_frame):
    overestimated_count = 0
    underestimated_count = 0
    spot_on = 0
    total_diff = 0
    time_tracked_issues = 0
    for i, row in data_frame.iterrows():
        original_estimate = row['original_estimate'] if pd.notnull(row['original_estimate']) else None
        time_spent = row['time_spent'] if pd.notnull(row['time_spent']) else None
        if original_estimate and time_spent:
            if original_estimate < time_spent:
                underestimated_count += 1
            elif original_estimate > time_spent:
                overestimated_count += 1
            else:
                spot_on += 1
            time_tracked_issues += 1
            diff = original_estimate - time_spent
            total_diff += diff
            average_estimate = round(data_frame['original_estimate'].mean() / 60, 2)
            average_actual = round(data_frame['time_spent'].mean() / 60, 2)
    average_diff = round(total_diff / (time_tracked_issues * 60), 2)
    print('Overestimated issues: {}'.format(overestimated_count))
    print('Underestimated issues: {}'.format(underestimated_count))
    print('Spot on: {}'.format(spot_on))
    print('Total time tracked issues: {}'.format(time_tracked_issues))
    print('Average etimate: {}m'.format(average_estimate))
    print('Average actual: {}m'.format(average_actual))
    print('Average estimate off by {}m.'.format(average_diff))


def collect_issues(jirapi_conn, data_frame):
    """
    Compile all issues from a given board into
    :param jirapi_conn: JirApi object
    :param data_frame: pandas data_frame in which to store JIRA issue data
    :return: pandas data_frame with all JIRA issue data
    """
    for issue in jirapi_conn.all_issues():
        row_index = get_issue_num(issue)
        row_dict = parse_issue_json(issue)
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
    row_dict['sprints'] = get_sprints(issue)
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
            temp_result = ','.join([result[i].get('name') for i, obj in enumerate(result)])
            result = temp_result
    return result


def get_sprints(issue):
    try:
        sprints_string = issue['fields']['customfield_10004']
    except KeyError:
        return None
    sprints = ','.join([re.search(r'name=(.+),goal=', sprint).group(1) for sprint in sprints_string])

    return sprints


def get_issue_num(issue):
    return issue['key'].split('-')[-1]


if __name__ == '__main__':
    main()
