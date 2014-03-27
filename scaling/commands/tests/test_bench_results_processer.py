#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"

from unittest import TestCase, main

import numpy as np
from numpy.testing import assert_almost_equal

from scaling.util import BenchCase, BenchData, FittedCurve, SummarizedResults
from scaling.commands.bench_results_processer import BenchResultsProcesser


class BenchResultsProcesserTests(TestCase):
    def setUp(self):
        """Set up data for use in unit tests"""
        self.cmd = BenchResultsProcesser()
        self.results = [BenchCase('file_10',
                                  [100, 101, 105, 104, 102],
                                  [98, 98.4, 97.3, 98.3, 99],
                                  [1.7, 1.5, 1.6, 1.75, 1.43],
                                  [2530, 2534, 2533, 2520, 2525]),
                        BenchCase('file_20',
                                  [151, 162, 149, 155, 157],
                                  [143, 148, 145.86, 150.4, 151.2],
                                  [6.5, 7.2, 5.87, 6.12, 6.98],
                                  [5143, 5200, 5098, 5142, 5183]),
                        BenchCase('file_30',
                                  [210, 205.1, 207.21, 211.54, 212.56],
                                  [200.12, 198.52, 202.14, 205.21, 196.98],
                                  [8.54, 6.83, 5.12, 6.14, 7.143],
                                  [10541, 10621, 10421, 10514, 10589])]

    def test_bench_results_processer(self):
        """Correctly processes the benchmark outputs"""
        obs = self.cmd(bench_results=self.results)

        self.assertEqual(obs.keys(), ['bench_data'])
        obs = obs['bench_data']

        labels = ['file_10', 'file_20', 'file_30']
        means = BenchData([102.4, 154.8, 209.282],
                          [98.2, 147.692, 200.594],
                          [1.596, 6.534, 6.7546],
                          [2528.4, 5153.2, 10537.2])
        std_devs = BenchData([1.8547237, 4.57820926, 2.76194424],
                             [0.55497748, 3.00350728, 2.87348986],
                             [0.11943199, 0.5011826, 1.13082653],
                             [5.23832034, 35.65052594, 68.93591227])
        wall_curve = FittedCurve(np.array([53.441, 102.053]), 1)
        mem_curve = FittedCurve(np.array([1379.6, 1245.2, 2528.4]), 2)
        exp = SummarizedResults(labels, means, std_devs, wall_curve, mem_curve)
        self.assertEqual(obs.labels, exp.labels)
        assert_almost_equal(obs.means, exp.means)
        assert_almost_equal(obs.stdevs, exp.stdevs)
        assert_almost_equal(obs.wall_curve.poly, exp.wall_curve.poly)
        self.assertEqual(obs.wall_curve.deg, exp.wall_curve.deg)
        assert_almost_equal(obs.mem_curve.poly, exp.mem_curve.poly)
        self.assertEqual(obs.mem_curve.deg, exp.mem_curve.deg)

if __name__ == '__main__':
    main()