#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"

from unittest import TestCase, main
from scaling.commands.bench_results_processer import BenchResultsProcesser
from scaling.util import OutputRedirect
from matplotlib.figure import Figure
import os

class BenchResultsProcesserTests(TestCase):
    def setUp(self):
        """Set up data for use in unit tests"""
        self.cmd = BenchResultsProcesser()
        self.exp_keys = ['bench_data', 'time_fig', 'time_str',
                         'mem_fig', 'mem_str']
        # Get the tests folder
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to the test timing folder
        self.timing_dir = os.path.join(tests_dir, '../support_files/timing')

    def test_bench_results_processer(self):
        """Data correctly retrieved"""
        stdout_red = OutputRedirect()
        with stdout_red as out:
            obs = self.cmd(input_dir=self.timing_dir)
            obs_out = out.getvalue()
        self.assertEqual(set(obs.keys()), set(self.exp_keys))
        obs_data = obs['bench_data']
        exp_data = {
            'label' : [10.0, 20.0, 30.0, 40.0],
            'wall_time' : ([397.446, 797.59, 1203.004, 1617.564],
                        [9.102124148, 16.78580948, 20.07751638, 76.82548135]),
            'cpu_user' : ([383.344, 771.106, 1166.298, 1572.904],
                        [2.491654872, 15.08632971, 10.03758616, 59.19994041]),
            'cpu_kernel' : ([6.678, 13.544, 19.608, 25.89],
                        [2.336522202, 4.317965262, 6.659373544, 7.725679258]),
            'memory' : ([9710547.2, 18743296, 27390896, 35643206.4],
                        [92.9653699, 1068.531702852, 2554.55420768,
                            3185.4967336])
        }
        # Check the contents of the observed data dictionary
        self.assertEqual(obs_data.keys(), exp_data.keys())
        for o, e in zip(obs_data['label'], exp_data['label']):
            self.assertAlmostEqual(o, e)
        for key in ['wall_time', 'cpu_user', 'cpu_kernel', 'memory']:
            for o, e in zip(obs_data[key][0], exp_data[key][0]):
                self.assertAlmostEqual(o, e)
            for o, e in zip(obs_data[key][1], exp_data[key][1]):
                self.assertAlmostEqual(o, e)
        # Check the figures and strings
        self.assertEqual(obs['time_fig'].__class__, Figure)
        self.assertEqual(obs['time_str'], "40.65768*x^1 + -12.541")
        self.assertEqual(obs['mem_fig'].__class__, Figure)
        self.assertEqual(obs['mem_str'], "864455.776*x^1 + 1260592.0")
        # Check the standard output
        exp_stdout = ("Warning - File /Users/jose/qiime_software/QIIME-Scaling"
            "/tests/test_commands/../support_files/timing/20/5.txt not used:\n")
        self.assertEqual(obs_out, exp_stdout)

if __name__ == '__main__':
    main()