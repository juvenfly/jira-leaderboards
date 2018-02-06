import numpy
import pandas
from dateutil import parser
from sklearn.feature_extraction.text import TfidfVectorizer

from constants import EXCLUDED_FIELDS, LABEL_FIELDS, NUMERICAL_FIELDS, TEXT_FIELDS


class DataJanitor(object):
    def __init__(self, dataframe, date_columns, text_fields, label_fields):
        self.data = dataframe
        self.date_columns = date_columns
        self.text_fields = text_fields
        self.label_fields = label_fields

    def clean_data(self):
        for column in self.date_columns:
            self.get_datetime_fields(column)

        self.vectorize_text_fields()
        self.remove_unwanted_columns()
        self.get_dummy_variables()

    def remove_unwanted_columns(self):
        unwanted_columns = [
            # 'components',
            'sprints',
            'fix_versions',
            'key',
            'created_datetime',
            'updated_datetime',
            'resolved_datetime',
        ]

        self.data = self.data.drop(unwanted_columns, axis=1)

    def get_datetime_fields(self, column_name):
        """
        Replaces single datetime column with separate columns for day, month, and year
        :param dataframe: pandas dataframe
        :param column_name: datetime column label
        :return: updated pandas dataframe
        """
        date_type = column_name.split('_')[0]

        for i, date_part in enumerate(['day', 'month', 'year']):
            new_column = '{}_{}'.format(date_type, date_part)

            self.data[new_column] = [fetch_date_part(date, date_part) for date in self.data[column_name]]

            self.data[new_column].describe()

    def vectorize_text_fields(self):
        """
        Creates a tfidf vector for all columns of dtype numpy.object
        :param dataframe: pandas data frame
        :return: pandas data frame
        """
        vectorizer = TfidfVectorizer()

        for column_name in self.data:
            if column_name in self.text_fields and column_name != 'time_spent':
                vect_df = vectorizer.fit_transform(self.data[column_name].values.astype('U')).toarray()

                self.data[column_name] = vect_df

    def get_dummy_variables(self):
        # TODO: THis does not handle Labels field correctly since it is a comma delimited string
        self.data = pandas.get_dummies(self.data, columns=self.label_fields)

def impute_missing_values(dataframe, column):
    value_present_column = '{}_present'.format(column)

    dataframe[value_present_column] = dataframe[column].notnull()
    dataframe[column] = dataframe[column].fillna(-1)

    return dataframe


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
