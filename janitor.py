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

    def remove_unwanted_columns(self):
        unwanted_columns = [
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
        # TODO This does not handle labels well. Need to split them manually.
        self.data = pandas.get_dummies(self.data, columns=self.label_fields)
        for column_name in self.multilabel_fields:
            self.get_multilabel_dummies(column_name)

    def get_multilabel_dummies(self, column_name):
        temp_dataframe = self.data[column_name].str.get_dummies(sep=',')
        column_name_map = {old_name: '{}_{}'.format(column_name, old_name) for old_name in temp_dataframe.columns.values}
        print(column_name_map)
        temp_dataframe = temp_dataframe.rename(index=str, columns=column_name_map)
        self.data = pandas.concat([self.data, temp_dataframe])


def impute_missing_values(dataframe, column):
    value_present_column = '{}_present'.format(column)

    dataframe[value_present_column] = dataframe[column].notnull()
    dataframe[column] = dataframe[column].fillna(-1)

    return dataframe


def fetch_date_part(date, part):
    try:
        date_part = int(parser.parse(date).__getattribute__(part))
    except TypeError:
        date_part = None

    return date_part
