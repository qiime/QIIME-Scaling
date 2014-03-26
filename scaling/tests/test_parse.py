#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "GPL"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"

from unittest import TestCase, main

from scaling.util import BenchSummary
from scaling.parse import parse_parameters_file, parse_summarized_results


class ParseTests(TestCase):
    """Tests of parse functions"""

    def setUp(self):
        """Set up data for use in unit tests"""
        self.single_parameter = single_parameter.splitlines()
        self.multiple_parameter = multiple_parameter.splitlines()
        self.summarized_results = summarized_results.splitlines()

    def test_parse_single_parameter(self):
        """Correctly parses a parameter file with a single entry"""
        exp = {'jobs_to_start': ['2', '4', '8', '16', '32', '64']}
        obs = parse_parameters_file(self.single_parameter)
        self.assertEqual(obs, exp)

    def test_parse_multiple_parameter(self):
        """Correctly parses a parameter file with a multiple entry"""
        exp = {'jobs_to_start': ['2', '4', '8', '16', '32', '64'],
               'similarity': ['0.94', '0.97', '0.99']}
        obs = parse_parameters_file(self.multiple_parameter)
        self.assertEqual(obs, exp)

    def test_parse_summarized_results(self):
        """Correctly parses a file with the results summary"""
        exp = BenchSummary(["100", "200", "300", "400", "500"],
                           [25, 50, 75, 100, 125],
                           [1, 2, 3, 4, 5],
                           [23, 46, 70, 94, 123],
                           [0.9, 2, 2.9, 4.1, 5],
                           [2, 4, 5, 6, 2],
                           [0.1, 0.0, 0.001, 0.2, 0.02],
                           [1048576, 2097152, 3145728, 4194304, 5242880],
                           [0.0, 0.0, 0.0, 0.2, 0.0])
        obs = parse_summarized_results(self.summarized_results)
        self.assertEqual(obs, exp)

single_parameter = """jobs_to_start\t2,4,8,16,32,64"""

multiple_parameter = """jobs_to_start\t2,4,8,16,32,64
similarity\t0.94,0.97,0.99"""

summarized_results = """#label\twall_mean\twall_std\tuser_mean\tuser_std\tkernel_mean\tkernel_std\tmem_mean\tmem_std
100\t25\t1\t23\t0.9\t2\t0.1\t1048576\t0.0
200\t50\t2\t46\t2\t4\t0.0\t2097152\t0.0
300\t75\t3\t70\t2.9\t5\t0.001\t3145728\t0.0
400\t100\t4\t94\t4.1\t6\t0.2\t4194304\t0.2
500\t125\t5\t123\t5\t2\t0.02\t5242880\t0.0
"""

if __name__ == '__main__':
    main()
