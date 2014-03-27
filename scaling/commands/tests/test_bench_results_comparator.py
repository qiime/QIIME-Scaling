#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"

from unittest import TestCase, main

from pyqi.core.exception import CommandError

from scaling.util import BenchSummary, CompData
from scaling.commands.bench_results_comparator import BenchResultsComparator


class BenchResultsComparatorTests(TestCase):
    def setUp(self):
        """Set up data for use in unit tests"""
        self.cmd = BenchResultsComparator()
        # Get the folder with the tests files
        self.results = [BenchSummary(['10', '20', '30'],
                                     [102.4, 154.8, 209.282],
                                     [1.8547237, 4.57820926, 2.76194424],
                                     [98.2, 147.692, 200.594],
                                     [0.55497748, 3.00350728, 2.87348986],
                                     [1.596, 6.534, 6.7546],
                                     [0.11943199, 0.5011826, 1.13082653],
                                     [2528.4, 5153.2, 10537.2],
                                     [5.23832034, 35.65052594, 68.93591227]),
                        BenchSummary(['10', '20', '30'],
                                     [102.4, 154.8, 209.282],
                                     [1.8547237, 4.57820926, 2.76194424],
                                     [98.2, 147.692, 200.594],
                                     [0.55497748, 3.00350728, 2.87348986],
                                     [1.596, 6.534, 6.7546],
                                     [0.11943199, 0.5011826, 1.13082653],
                                     [2528.4, 5153.2, 10537.2],
                                     [5.23832034, 35.65052594, 68.93591227])]
        self.labels = ['data_1', 'data_2']

    def test_bench_results_comparator(self):
        """Correctly generates the output structure"""
        obs = self.cmd(bench_results=self.results, labels=self.labels)
        exp = {'comp_data': CompData(['10', '20', '30'],
                                     {'data_1': ([102.4, 154.8, 209.282],
                                                 [1.8547237, 4.57820926,
                                                  2.76194424]),
                                      'data_2': ([102.4, 154.8, 209.282],
                                                 [1.8547237, 4.57820926,
                                                  2.76194424])},
                                     {'data_1': ([2528.4, 5153.2, 10537.2],
                                                 [5.23832034,
                                                  35.65052594,
                                                  68.93591227]),
                                      'data_2': ([2528.4, 5153.2, 10537.2],
                                                 [5.23832034,
                                                  35.65052594,
                                                  68.93591227])})}
        self.assertEqual(obs, exp)

    def test_invalid_bench_results(self):
        """Raises a CommandError if len(bench_results) < 2"""
        with self.assertRaises(CommandError):
            self.cmd(bench_results=[self.results[0]], labels=[self.labels[0]])

    def test_inconsistent_inputs(self):
        """Raises a CommandError if len(bench_results) != len(labels)"""
        with self.assertRaises(CommandError):
            self.cmd(bench_results=self.results, labels=['data_1', 'data_2',
                                                         'data_extra'])


if __name__ == '__main__':
    main()
