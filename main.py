from argparse import ArgumentParser

import numpy
import pandas
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from api import JirApi
from constants import HEADER, EXCLUDED_FIELDS, TEXT_FIELDS, LABEL_FIELDS
from janitor import DataJanitor


def main(update_type, update_model_flag, start_issue, end_issue):
    # TODO programatically generate model filename based on type
    model_name = 'test.pkl'

    dataframe = fetch_data(update_type, start_issue, end_issue)
    janitor = DataJanitor(
        dataframe=dataframe,
        date_columns=['created_datetime', 'updated_datetime', 'resolved_datetime'],
    )
    data = janitor.clean_data()
    print(data.columns.values)

    if update_model_flag:
        model = update_or_create_model(data)
    else:
        model = joblib.load(model_name)

    x_vals = data.drop(['time_spent'])

    result = model.predict(x_vals)
    data['predicted_time_spent'] = result
    temp_df = data[['time_spent', 'predicted_time_spent']]
    print('Subset, where time_spent is unobserved and predicted_time_spent is not -1:')
    print(temp_df.loc[(temp_df['predicted_time_spent'] != -1) & (temp_df['time_spent'] == -1)])
    print(f'Data head {data.head()}')


def update_or_create_model(dataframe):
    """
    Updates or creates model based upon data in dataframe.
    :param dataframe: pandas dataframe object
    :return: returns model
    """
    # TODO accept model_type as commandline arg
    model_type = 'knn'

    # TODO currently only creates; need to implement model updates
    training_set = dataframe.loc[dataframe['time_spent'].notnull()]

    x_vals = training_set.drop(['time_spent'])
    y_vals = training_set['time_spent']

    x_train, x_test, y_train, y_test = train_test_split(x_vals, y_vals, test_size=0.3, random_state=100)

    if model_type == 'classifier':
        model = train_decision_tree_classifier(x_train, y_train)
    elif model_type == 'regressor':
        model = train_decision_tree_regressor(x_train, y_train)
    elif model_type == 'knn':
        model = train_knn_classifier(x_train, y_train)
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
        dataframe = pandas.read_csv('issues.csv', index_col=0)
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
