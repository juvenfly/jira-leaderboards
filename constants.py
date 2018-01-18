import sys

inf = sys.maxsize

HEADER = [
    'key',
    'summary',
    'description',
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
    'sprints': ['fields', 'customfield_10004'],
    'description': ['fields', 'description'],
}

EXCLUDED_ISSUE_TYPES = [
    'Epic',
    'Story',
]

EXCLUDED_FIELDS = [
    'key',
    'fix_versions',
    'created_datetime',
    'updated_datetime',
    'resolved_datetime',
    'status',
    'sprints',
]

TEXT_FIELDS = [
    'summary',
    'description',
]

LABEL_FIELDS = [
    'issue_type',
    'components',
    'reporter',
    'assignee',
    'labels',
    'status'
]

NUMERICAL_FIELDS = [
    'original_estimate',
    'remaining_estimate',
    'time_spent',
    'created_day',
    'created_month',
    'created_year',
    'updated_day',
    'updated_month',
    'updated_year',
    'resolved_day',
    'resolved_month',
    'resolved_year',
]

INCLUDED_PROJECTS = [
    'FARM',
]

STORY_POINT_BUCKETS = {
    (0, 3600): 1,
    (3600, 14400): 2,
    (14400, 28800): 3,
    (28800, 144000): 5,
    (144000, 288000): 8,
    (288000, inf): 13,
}
