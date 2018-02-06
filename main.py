import datetime
from argparse import ArgumentParser

import numpy
import pandas
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, Imputer
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from api import JirApi
from constants import HEADER, EXCLUDED_FIELDS
from janitor import (
    vectorize_text_fields,
    get_datetime_fields,
    remove_unwanted_columns,
    get_dummy_variables,
    impute_missing_values,
)


def main(update_type, update_model_flag, start_issue, end_issue):
    # TODO programatically generate model filename based on type
    model_name = 'test.pkl'

    dataframe = fetch_data(update_type, start_issue, end_issue)
    dataframe = remove_unwanted_columns(dataframe)
    for column in dataframe.columns.values:
        if column in ['time_spent', 'original_estimate', 'remaining_estimate', 'resolved_day', 'resolved_month', 'resolved_year']:
            dataframe = impute_missing_values(dataframe, column)

    if update_model_flag:
        model = update_or_create_model(dataframe)
    else:
        model = joblib.load(model_name)

    x_vals = dataframe.fillna(0)  # TODO Don't impute 0s

    result = model.predict(x_vals)
    dataframe['predicted_time_spent'] = result
    print(dataframe.loc[:, ['key', 'time_spent', 'predicted_time_spent']])


def update_or_create_model(dataframe):
    """
    Updates or creates model based upon data in dataframe.
    :param dataframe: pandas dataframe object
    :return: returns model
    """
    # TODO accept model_type as commandline arg
    model_type = 'knn'

    # TODO currently only creates; need to implement model updates
    training_set = dataframe

    x_vals = training_set
    y_vals = training_set['time_spent']

    x_train, x_test, y_train, y_test = train_test_split(x_vals, y_vals, test_size=0.3, random_state=100)

    if model_type == 'classifier':
        model = train_decision_tree_classifier(x_train, y_train)

    # TODO: This is probably not the right model type. Switch back to classifier? Try random forrest? k-NN?
    elif model_type == 'regressor':
        model = train_decision_tree_regressor(x_train, y_train)
    else:
        raise Exception('Model type not selected or incorrectly specified: {}'.format(model_type))

    print('Model Type: {}'.format(model_type))
    print('Score: {}'.format(model.score(x_vals, y_vals)))
    print('Cross Validation Score: {}'.format(cross_val_score(model, x_test, y_test)))

    return model


def fetch_data(update_type, start_issue, end_issue):
    """
    Gets data from file, JIRA API or both depending on update_type
    :param update_type: val of "all" recreates dataset from scratch, "append" not yet implemented
    :param start_issue: starting ticket number to pull from
    :param end_issue: end ticket number to pull from
    :return: returns pandas data frame
    """
    try:
        # TODO: validate header from archive is same as above
        dataframe = pandas.DataFrame.from_csv('issues.csv')
    except FileNotFoundError:
        if not update_type:
            raise
        dataframe = pandas.DataFrame(columns=HEADER)

    if update_type == 'all':
        print("Updating all issue data")
        jira = JirApi(start_issue=start_issue, end_issue=end_issue)
        dataframe = jira.collect_issues(dataframe)
        dataframe.to_csv('issues.csv')
    elif update_type == 'append':
        # TODO: Programatically determine start_ & end_issue vals
        raise Exception('Append new data not implemented. Use -U to update entire dataset.')

    for column_name in ['created_datetime', 'updated_datetime', 'resolved_datetime']:
        dataframe = get_datetime_fields(dataframe, column_name)

    dataframe = get_dummy_variables(dataframe)
    dataframe = vectorize_text_fields(dataframe)

    return dataframe

def train_knn_classifier(x_train, y_train):
    """
    Trains KNeighborClassifier on given x and y vals
    :param x_train: training x vals from train_test_split
    :param y_train: training y vals from train_test_split
    :return: model
    """
    knn_classifier = KNeighborsClassifier(
        weights='distance',
        n_jobs=-1,
    )
    knn_classifier.fit(x_train, y_train)

    return knn_classifier


def train_decision_tree_regressor(x_train, y_train):
    """
    Trains DecisionTreeRgressor on given x and y vals
    :param x_train: training x vals from train_test_split
    :param y_train: training y vals from train_test_split
    :return: model
    """
    regressor = DecisionTreeRegressor()
    regressor.fit(x_train, y_train)

    return regressor


def train_decision_tree_classifier(x_train, y_train):
    """
    Trains DecisionTreeClassifier on given x and y vals
    :param x_train: training x vals from train_test_split
    :param y_train: training y vals from train_test_split
    :return: model
    """
    classifier_gini = DecisionTreeClassifier(
        criterion='gini',
        random_state=100,
        max_depth=3,
        min_samples_leaf=5,
    )
    classifier_gini.fit(x_train, y_train)

    return classifier_gini


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
        type=int,
        dest="start_issue",
        help="First issue to pull",
    )
    parser.add_argument(
        "-e",
        "--end-issue",
        type=int,
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
