inf = float('inf')

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
]

NUMERICAL_FIELDS = [
    'original_estimate',
    'remaining_estimate',
    'time_spent',
]

INCLUDED_PROJECTS = [
    'FARM',
]

STORY_POINTS_BUCKETS = {
    (0, 10800): 1,
    (10800, 21600): 2,
    (21600, 108000): 3,
    (108000, 216000): 5,
    (216000, 432000): 8,
    (432000, inf): 13,
}
