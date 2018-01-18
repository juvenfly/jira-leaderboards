import numpy
import pandas
from dateutil import parser
from sklearn.feature_extraction.text import TfidfVectorizer

from constants import EXCLUDED_FIELDS, LABEL_FIELDS, NUMERICAL_FIELDS, TEXT_FIELDS


def impute_missing_values(column):
    pass


def vectorize_text_fields(dataframe):
    """
    Creates a tfidf vector for all columns of dtype numpy.object
    :param dataframe: pandas data frame
    :return: pandas data frame
    """
    vectorizer = TfidfVectorizer()

    for column_name in dataframe:
        if column_name in TEXT_FIELDS and column_name != 'time_spent':

            vect_df = vectorizer.fit_transform(dataframe[column_name].values.astype('U')).toarray()

            dataframe[column_name] = vect_df

    return dataframe


def get_datetime_fields(dataframe, column_name):
    """
    Replaces single datetime column with separate columns for day, month, and year
    :param dataframe: pandas dataframe
    :param column_name: datetime column label
    :return: updated pandas dataframe
    """
    date_type = column_name.split('_')[0]

    for i, date_part in enumerate(['day', 'month', 'year']):
        new_column = '{}_{}'.format(date_type, date_part)

        dataframe[new_column] = [fetch_date_part(date, date_part) for date in dataframe[column_name]]

        dataframe[new_column].describe()

    return dataframe


def fetch_date_part(date, part):
    try:
        date_part = int(parser.parse(date).__getattribute__(part))
    except TypeError:
        date_part = None

    return date_part


def get_dummy_variables(dataframe):
    df_with_dummies = pandas.get_dummies(dataframe, columns=LABEL_FIELDS)
    return df_with_dummies


def remove_unwanted_columns(dataframe):
    unwanted_columns = [
        # 'components',
        'sprints',
        'fix_versions',
        'key',
        'created_datetime',
        'updated_datetime',
        'resolved_datetime',
    ]

    return dataframe.drop(unwanted_columns, axis=1)