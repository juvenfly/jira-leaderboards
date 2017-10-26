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
    try:
        data_frame = pd.DataFrame.from_csv('issues.csv')
    except FileNotFoundError:
        data_frame = pd.DataFrame(columns=HEADER)

    data_frame = collect_issues(jira, data_frame)

    print(data_frame)
    data_frame.tocsv('issues.csv')


def collect_issues(jirapi_conn, data_frame):
    """
    Compile all issues from a given board into
    :param jirapi_conn:
    :param data_frame:
    :return:
    """
    for issue in jirapi_conn.all_issues():
        row_index = get_issue_key(issue)
        row_dict = parse_issue_json(issue)
        row = [row_dict[field] for field in HEADER]
        data_frame.loc[row_index] = row

    return data_frame


def parse_issue_json(issue):
    row_dict = {key: get_leaf_value(issue, HEADER) for key in HEADER}
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
    if isinstance(result, list):
        result = ','.join(result)
    return result


def get_issue_key(issue):
    return issue['key'].split('-')[-1]


if __name__ == '__main__':
    main()
