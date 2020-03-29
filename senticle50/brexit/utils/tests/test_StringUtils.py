from utils import StringUtils
from collections import Counter

import unittest

class TestStringUtilsMethods(unittest.TestCase):

    #TODO: Add test for checking single delimitter with no trailing word is not recognised

    def test_get_delimited_strings_count_no_strings(self):
        expected_output = Counter({})
        actual_output = StringUtils.get_delimited_strings_count([], 3, "#")
        self.assertEqual(actual_output, expected_output)

    def test_get_delimited_strings_count_one_string(self):
        string_arr = [
            "This is #an #example #tweet",
        ]
        expected_output = Counter({'#an': 1, '#example': 1, '#tweet': 1})
        actual_output = StringUtils.get_delimited_strings_count(string_arr, 3,
                                                                "#")
        self.assertEqual(actual_output, expected_output)

    def test_get_delimited_strings_count_multiple_strings(self):
        string_arr = [
            "This is an example #tweet",
            "I love to #tweet it makes my #day #great",
            "#tweet #fun #great"
        ]
        expected_output = Counter({'#tweet': 3, '#great': 2, '#fun': 1, '#day': 1})
        actual_output = StringUtils.get_delimited_strings_count(string_arr,
                                                                3, "#")
        self.assertEqual(actual_output, expected_output)

    def test_get_delimited_strings_count_no_match(self):
        string_arr = [
            "This is an example #tweet",
            "I love to #tweet it makes my #day #great",
            "#tweet #fun #great"
        ]
        expected_output = Counter({})
        actual_output = StringUtils.get_delimited_strings_count(string_arr,
                                                                3, "/")
        self.assertEqual(actual_output, expected_output)