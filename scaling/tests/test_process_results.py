#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from unittest import TestCase, main
import numpy as np

from scaling.util import BenchCase, BenchData, FittedCurve, SummarizedResults
from scaling.process_results import (compute_rsquare, curve_fitting,
                                     process_benchmark_results,
                                     compare_benchmark_results)


class TestProcessResults(TestCase):

    def setUp(self):
        """Set up data for use in unit tests"""
        self.num_cases = [BenchCase('10',
                                    [415.29, 392.73, 396.1, 392.42, 390.60],
                                    [388.29, 381.52, 382.4, 382.32, 382.26],
                                    [5.75, 5.65, 5.45, 5.49, 5.50],
                                    [9710640, 9710576, 9710624, 9710384,
                                     9710512]),
                          BenchCase('20',
                                    [815.21, 820.33, 788.19, 779.50, 784.72],
                                    [771.32, 799.58, 765.59, 755.76, 763.28],
                                    [22.17, 11.57, 11.02, 11.60, 11.36],
                                    [18742320, 18744128, 18742704, 18742352,
                                     18744976]),
                          BenchCase('30',
                                    [1240.57, 1191.88, 1202.94, 1181.67,
                                     1197.96],
                                    [1177.48, 1157.41, 1174.34, 1151.60,
                                     1170.66],
                                    [32.92, 16.28, 15.95, 16.27, 16.62],
                                    [27386400, 27389792, 27392640, 27393424,
                                     27392224])]
        self.str_cases = [BenchCase('file_10',
                                    [415.29, 392.73, 396.18, 392.42, 390.61],
                                    [388.29, 381.52, 382.33, 382.32, 382.26],
                                    [11.35, 5.60, 5.45, 5.49, 5.50],
                                    [9710640, 9710576, 9710624, 9710384,
                                     9710512]),
                          BenchCase('file_20',
                                    [815.21, 820.33, 788.19, 779.50, 784.72],
                                    [771.32, 799.58, 765.59, 755.76, 763.28],
                                    [22.17, 11.57, 11.02, 11.60, 11.36],
                                    [18742320, 18744128, 18742704, 18742352,
                                     18744976]),
                          BenchCase('file_30',
                                    [1240.57, 1191.88, 1202.94, 1181.67,
                                     1197.96],
                                    [1177.48, 1157.41, 1174.34, 1151.60,
                                     1170.66],
                                    [32.92, 16.28, 15.95, 16.27, 16.62],
                                    [27386400, 27389792, 27392640, 27393424,
                                     27392224])]

    def test_compute_rsquare(self):
        """Correctly computes the R square value"""
        y = np.array([15.0, 20.0, 25.0, 30.0, 35.0])
        SSerr = np.array([0.05])
        obs = compute_rsquare(y, SSerr)
        exp = 0.9998
        self.assertAlmostEqual(obs, exp)

        y = np.array([10, 12, 15, 25, 50])
        SSerr = np.array([0.03])
        obs = compute_rsquare(y, SSerr)
        exp = 0.99997236
        self.assertAlmostEqual(obs, exp)

    def test_curve_fitting(self):
        """Correctly fits a curve to the a given data points"""
        x = np.array([100, 200, 300, 400, 500])
        # Linear test: y = 5*x + 50
        y = np.array([550, 1050, 1550, 2050, 2550])
        obs_poly, obs_deg = curve_fitting(x, y)
        exp_poly = np.array([5.0, 50.0])
        exp_deg = 1
        for o, e in zip(obs_poly, exp_poly):
            self.assertAlmostEqual(o, e)
        self.assertEqual(obs_deg, exp_deg)
        # Quadratic test: y = 3*x^2 - 5*x + 2
        y = np.array([29502, 119002, 268502, 478002, 747502])
        obs_poly, obs_deg = curve_fitting(x, y)
        exp_poly = np.array([3.0, -5.0, 2.0])
        exp_deg = 2
        for o, e in zip(obs_poly, exp_poly):
            self.assertAlmostEqual(o, e)
        self.assertEqual(obs_deg, exp_deg)
        # Cubic test: y = x^3 - 5x^2 - 10x + 500
        y = np.array([949500, 7798500, 26547500, 63196500, 123745500])
        obs_poly, obs_deg = curve_fitting(x, y)
        exp_poly = np.array([1.0, -5.0, -10.0, 500.0])
        exp_deg = 3
        for o, e in zip(obs_poly, exp_poly):
            self.assertAlmostEqual(o, e)
        self.assertEqual(obs_deg, exp_deg)

    def test_process_benchmark_results_num(self):
        """Correctly processes the benchmark results with numerical labels"""
        obs = process_benchmark_results(self.num_cases)
        labels = ['10', '20', '30']
        means = BenchData([397.428],
                          [383.358],
                          [5.5680000000000005],
                          [9710547.1999999993])
        std_devs = BenchData([9.1059044580975055],
                             [2.4861086058336368],
                             [0.11356055653262712],
                             [92.965369896537283])
        wall_curve = FittedCurve([], 1)
        mem_curve = FittedCurve([], 1)
        exp = SummarizedResults(labels, means, std_devs, wall_curve, mem_curve)
        self.assertEqual(obs, exp)


if __name__ == '__main__':
    main()
