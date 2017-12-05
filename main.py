from argparse import ArgumentParser

import numpy
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

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
        if not update_issues:
            raise
        data_frame = pd.DataFrame(columns=HEADER)

    if update_issues:
        jira = JirApi(start_issue=4300, end_issue=5000)
        data_frame = jira.collect_issues(data_frame)
        data_frame.to_csv('issues.csv')

    data_frame = vectorize_text_fields(data_frame)

    x_vals = data_frame.drop('time_spent', axis=1)
    y_vals = data_frame['time_spent']

    x_train, x_test, y_train, y_test = train_test_split(x_vals, y_vals, test_size=0.3, random_state=100)


def vectorize_text_fields(data_frame):
    vectorizer = TfidfVectorizer()
    for column_name in data_frame:
        if data_frame[column_name].dtype == numpy.object:
            tfidf_vect = vectorizer.fit_transform(data_frame[column_name])
            vect_column_name = column_name + '_tfidf'
            data_frame[vect_column_name] = tfidf_vect
    return data_frame

if __name__ == '__main__':
    main()
