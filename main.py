from argparse import ArgumentParser

import numpy
import pandas
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from api import JirApi
from constants import HEADER


def main(update_type, update_model_flag, start_issue, end_issue):
    # TODO programatically generate model filename based on type
    model_name = 'test.pkl'

    data_frame = fetch_data(update_type, start_issue, end_issue)

    if update_model_flag:
        model = update_or_create_model(data_frame)
    else:
        model = joblib.load(model_name)


def update_or_create_model(data_frame):
    x_vals = data_frame.drop('time_spent', axis=1)
    y_vals = data_frame['time_spent']

    x_train, x_test, y_train, y_test = train_test_split(x_vals, y_vals, test_size=0.3, random_state=100)

    classifier_gini = DecisionTreeClassifier(
        criterion='gini',
        random_state=100,
        max_depth=3,
        min_samples_leaf=5,
    )
    classifier_gini.fit(x_train, y_train)

    return classifier_gini


def fetch_data(update_type, start_issue, end_issue):
    try:
        # TODO: validate header from archive is same as above
        data_frame = pandas.DataFrame.from_csv('issues.csv')
    except FileNotFoundError:
        if not update_type:
            raise
        data_frame = pandas.DataFrame(columns=HEADER)

    if update_type == 'all':
        jira = JirApi(start_issue=start_issue, end_issue=end_issue)
        data_frame = jira.collect_issues(data_frame)
        data_frame.to_csv('issues.csv')
    elif update_type == 'append':
        # TODO: Programatically determine start_ & end_issue vals
        raise Exception('Append new data not implemented. Use -U to update entire dataset.')


    data_frame = vectorize_text_fields(data_frame)

    return data_frame


def vectorize_text_fields(data_frame):
    vectorizer = TfidfVectorizer()
    for column_name in data_frame:
        if column_name != 'time_spent' and data_frame[column_name].dtype == numpy.object:
            tfidf_vect = vectorizer.fit_transform(data_frame[column_name])
            vect_column_name = column_name + '_tfidf'
            data_frame[vect_column_name] = tfidf_vect
    return data_frame


if __name__ == '__main__':
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-u",
        "--update-issues",
        dest="update_issues",
        help="Update issue data set",
        action="store_true",
    )
    group.add_argument(
        "-U",
        "--update-all-issues",
        dest="update_all_issues",
        help="Recreate issue data set",
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
    parser.add_argument(
        "-m",
        "--update-model",
        dest="update_model",
        help="Update model flag",
        action="store_true",
    )
    args = parser.parse_args()
    update_issues_flag = args.update_issues
    update_all_issues = args.update_all_issues
    update_model_flag = args.update_model
    start_issue = args.start_issue
    end_issue = args.end_issue

    if update_all_issues:
        update_type = 'all'
    elif update_issues_flag:
        update_type = 'append'
    else:
        update_type = None

    main(update_type, update_model_flag, start_issue, end_issue)
