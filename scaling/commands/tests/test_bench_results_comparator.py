#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"

from unittest import TestCase, main
from os.path import dirname, join, abspath

from pyqi.core.exception import CommandError

from scaling.commands.bench_results_comparator import BenchResultsComparator
from scaling.util import OutputRedirect


class BenchResultsComparatorTests(TestCase):
    def setUp(self):
        """Set up data for use in unit tests"""
        self.cmd = BenchResultsComparator()
        self.exp_keys = ['time_fig', 'mem_fig']
        # Get the folder with the tests files
        tests_dir = dirname(abspath(__file__))
        self.timing_dir = join(tests_dir, '../support_files/timing')
        self.timing_dir_2 = join(tests_dir, '../support_files/timing_2')
        self.labels = ['foo', 'bar']

    def test_bench_results_comparator(self):
        """Correctly generates the output figures"""
        stdout_red = OutputRedirect()
        with stdout_red as out:
            obs = self.cmd(input_dirs=[self.timing_dir, self.timing_dir_2],
                           labels=self.labels)
            obs_out = out.getvalue()
        self.assertEqual(obs.keys(), self.exp_keys)
        self.assertEqual(obs['time_fig'].__class__, Figure)
        self.assertEqual(obs['mem_fig'].__class__, Figure)
        out_exp = ("Warning - File %s/20/5.txt not used:\nWarning - File "
                   "%s/20/5.txt not used:\n" % (self.timing_dir,
                                                self.timing_dir_2))
        self.assertEqual(obs_out, out_exp)

    def test_invalid_input(self):
        """Correctly handles invalid input by rising a CommandError"""
        # Too few paths
        with self.assertRaises(CommandError):
            _ = self.cmd(input_dirs=['/foo/bar'], labels=self.labels)

if __name__ == '__main__':
    main()
