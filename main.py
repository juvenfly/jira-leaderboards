from argparse import ArgumentParser

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from api import JirApi
from constants import HEADER, FIELD_MAP
from plotter import time_estimates_plot


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-u",
        "--update-issues",
        dest="update_issues",
        help="Update issue data set",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--start-issue",
        dest="start_issue",
        help="First issue to pull",
    )
    parser.add_argument(
        "-e",
        "--end-issue",
        dest="end_issue",
        help="Last issue to pull",
    )
    args = parser.parse_args()
    update_issues = args.update_issues

    try:
        # TODO: validate header from archive is same as above
        data_frame = pd.DataFrame.from_csv('issues.csv')
    except FileNotFoundError:
        data_frame = pd.DataFrame(columns=HEADER)

    if update_issues:
        jira = JirApi(start_issue=4300, end_issue=5000)
        data_frame = jira.collect_issues(data_frame)
        data_frame.to_csv('issues.csv')


if __name__ == '__main__':
    main()
