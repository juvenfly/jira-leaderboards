from unittest import TestCase

import main


class TestMainHelpers(TestCase):

    def test_get_leaf_value(self):
        test_json = {
            'depth_1': 'return_me',
            'depth_2_1': {
                'depth_2_2': 'return_me'
            },
            'list_leaf_1': {
                'list_leaf_2': ['return', 'me']
            },
            'broken': {
                None: "don't return me"
            },
            'broken_2': "don't return me"
        }

        good_keys = [
            ['depth_1'],
            ['depth_2_1', 'depth_2_2'],
        ]
        list_keys = [
            ['list_leaf_1', 'list_leaf_2'],
        ]
        fail_keys = [
            ['broken', 'broken_2'],
            ['does', 'not', 'exist'],
        ]

        for key_list in good_keys:
            self.assertEqual(main.get_leaf_value(test_json, key_list), 'return_me')

        for key_list in list_keys:
            self.assertEqual(main.get_leaf_value(test_json, key_list), 'return,me')

        for key_list in fail_keys:
            self.assertIsNone(main.get_leaf_value(test_json, key_list))
