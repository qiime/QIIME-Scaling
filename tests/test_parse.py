#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "GPL"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"

from unittest import TestCase, main
from scaling.parse import parse_parameters_file

class ParseTests(TestCase):
    """Tests of parse functions"""

    def setUp(self):
        """Set up data for use in unit tests"""
        self.single_parameter = single_parameter.split('\n')
        self.multiple_parameter = multiple_parameter.split('\n')

    def test_parse_single_parameter(self):
        """Correctly parses a parameter file with a single entry"""
        exp = {'jobs_to_start' : ['2','4','8','16','32','64']}
        obs = parse_parameters_file(self.single_parameter)
        self.assertEqual(obs, exp)

    def test_parse_single_parameter(self):
        """Correctly parses a parameter file with a multiple entry"""
        exp = {'jobs_to_start' : ['2','4','8','16','32','64'],
                'similarity': ['0.94', '0.97', '0.99']}
        obs = parse_parameters_file(self.multiple_parameter)
        self.assertEqual(obs, exp)

single_parameter = """jobs_to_start\t2,4,8,16,32,64"""

multiple_parameter = """jobs_to_start\t2,4,8,16,32,64
similarity\t0.94,0.97,0.99"""

if __name__ == '__main__':
    main()