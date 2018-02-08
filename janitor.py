import numpy
import pandas
from dateutil import parser
from sklearn.feature_extraction.text import TfidfVectorizer

from constants import EXCLUDED_FIELDS, LABEL_FIELDS, NUMERICAL_FIELDS, TEXT_FIELDS, MULTILABEL_FIELDS


class DataJanitor(object):
    def __init__(self, dataframe, date_columns):
        self.data = dataframe
        self.date_columns = date_columns
        self.text_fields = TEXT_FIELDS
        self.label_fields = LABEL_FIELDS
        self.multilabel_fields = MULTILABEL_FIELDS

    def clean_data(self):
        for column in self.date_columns:
            self.get_datetime_fields(column)

        self.vectorize_text_fields()
        self.get_dummy_variables()
        self.remove_unwanted_columns()
        self.impute_missing_values()

        return self.data

    def remove_unwanted_columns(self):
        unwanted_columns = [
            'sprints',
            'fix_versions',
            'key',
            'created_datetime',
            'updated_datetime',
            'resolved_datetime',
            'original_estimate',  # estimate w/out original estimate?
        ]

        self.data = self.data.drop(unwanted_columns, axis=1)

    def get_datetime_fields(self, column_name):
        """
        Replaces single datetime column with separate columns for day, month, and year
        :param column_name: datetime column label
        :return: Does not return
        """
        date_type = column_name.split('_')[0]

        for i, date_part in enumerate(['day', 'month', 'year']):
            new_column = '{}_{}'.format(date_type, date_part)

            self.data[new_column] = [fetch_date_part(date, date_part) for date in self.data[column_name]]

            self.data[new_column].describe()

    def vectorize_text_fields(self):
        """
        Creates a tfidf vector for all columns of dtype numpy.object
        :return: Does not return
        """
        vectorizer = TfidfVectorizer()

        for column_name in self.data:
            if column_name in self.text_fields and column_name != 'time_spent':
                vect_df = vectorizer.fit_transform(self.data[column_name].values.astype('U')).toarray()

                self.data[column_name] = vect_df

    def get_dummy_variables(self):
        """
        Creates a separate column for each value in a category with a 1 or 0 corresponding to that value's presence
        or absence. label_fields are parsed using pandas default get_dummies() method, while fields that contain
        comma delimited strings of multiple values are handled separately in the get_multilabel_dummies() of this class.
        :return: Does not return
        """
        self.data = pandas.get_dummies(self.data, columns=self.label_fields)
        for column_name in self.multilabel_fields:
            self.get_multilabel_dummies(column_name)

    def get_multilabel_dummies(self, column_name):
        """
        Parses comma delimited sets of categorical varable values into values much like pandas default get_dummies()
        method
        :param column_name: Name of the source column
        :return: Does not return
        """
        temp_dataframe = self.data[column_name].str.get_dummies(sep=',')
        column_name_map = {old_name: '{}_{}'.format(column_name, old_name) for old_name in temp_dataframe.columns.values}
        temp_dataframe = temp_dataframe.rename(index=str, columns=column_name_map)
        self.data = pandas.concat([self.data, temp_dataframe])

    def impute_missing_values(self, strategy=-1):
        """
        Checks each column for NaNs. If any exist, creates a separate column to track whether the value exists in the
        source data, then imputes a value according to the strategy.
        :return: Does not return
        """
        if strategy != -1:
            raise Exception("Altenate imputation strategies not yet implemented. Please use -1.")
        for column in self.data.columns.values:
            if self.data[column].isnull().values.any():
                value_observed_column = '{}_observed'.format(column)
                # TODO Implement other strategies
                impute_val = -1

                self.data[value_observed_column] = self.data[column].notnull()
                self.data[column] = self.data[column].fillna(impute_val)

            if column in MULTILABEL_FIELDS:
                self.data = self.data.drop([column], axis=1)


def fetch_date_part(date, part):
    try:
        date_part = int(parser.parse(date).__getattribute__(part))
    except TypeError:
        date_part = None

    return date_part
