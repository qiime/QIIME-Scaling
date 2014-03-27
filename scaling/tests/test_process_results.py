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
from numpy.testing import assert_almost_equal

from scaling.util import (BenchCase, BenchData, FittedCurve, SummarizedResults,
                          CompData, BenchSummary)
from scaling.process_results import (compute_rsquare, curve_fitting,
                                     process_benchmark_results,
                                     compare_benchmark_results)


class TestProcessResults(TestCase):

    def setUp(self):
        """Set up data for use in unit tests"""
        self.num_cases = [BenchCase('10',
                                    [100, 101, 105, 104, 102],
                                    [98, 98.4, 97.3, 98.3, 99],
                                    [1.7, 1.5, 1.6, 1.75, 1.43],
                                    [2530, 2534, 2533, 2520, 2525]),
                          BenchCase('20',
                                    [151, 162, 149, 155, 157],
                                    [143, 148, 145.86, 150.4, 151.2],
                                    [6.5, 7.2, 5.87, 6.12, 6.98],
                                    [5143, 5200, 5098, 5142, 5183]),
                          BenchCase('30',
                                    [210, 205.1, 207.21, 211.54, 212.56],
                                    [200.12, 198.52, 202.14, 205.21, 196.98],
                                    [8.54, 6.83, 5.12, 6.14, 7.143],
                                    [10541, 10621, 10421, 10514, 10589])]
        self.str_cases = [BenchCase('file_10',
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
        self.results_error = [BenchSummary(['10', '20', '30'],
                                           [102.4, 154.8, 209.282],
                                           [1.8547237, 4.57820926, 2.76194424],
                                           [98.2, 147.692, 200.594],
                                           [0.55497748, 3.00350728,
                                            2.87348986],
                                           [1.596, 6.534, 6.7546],
                                           [0.11943199, 0.5011826, 1.13082653],
                                           [2528.4, 5153.2, 10537.2],
                                           [5.23832034, 35.65052594,
                                            68.93591227]),
                              BenchSummary(['20', '30', '40'],
                                           [102.4, 154.8, 209.282],
                                           [1.8547237, 4.57820926, 2.76194424],
                                           [98.2, 147.692, 200.594],
                                           [0.55497748, 3.00350728,
                                            2.87348986],
                                           [1.596, 6.534, 6.7546],
                                           [0.11943199, 0.5011826, 1.13082653],
                                           [2528.4, 5153.2, 10537.2],
                                           [5.23832034, 35.65052594,
                                            68.93591227])]
        self.labels = ['data_series_1', 'data_series_2']

    def test_compute_rsquare(self):
        """Correctly computes the R square value"""
        y = np.array([15.0, 20.0, 25.0, 30.0, 35.0])
        SSerr = np.array([0.05])
        obs = compute_rsquare(y, SSerr)
        exp = 0.9998
        assert_almost_equal(obs, exp)

        y = np.array([10, 12, 15, 25, 50])
        SSerr = np.array([0.03])
        obs = compute_rsquare(y, SSerr)
        exp = 0.99997236
        assert_almost_equal(obs, exp)

    def test_curve_fitting(self):
        """Correctly fits a curve to the a given data points"""
        x = np.array([100, 200, 300, 400, 500])
        # Linear test: y = 5*x + 50
        y = np.array([550, 1050, 1550, 2050, 2550])
        obs_poly, obs_deg = curve_fitting(x, y)
        exp_poly = np.array([5.0, 50.0])
        exp_deg = 1
        assert_almost_equal(obs_poly, exp_poly)
        self.assertEqual(obs_deg, exp_deg)
        # Quadratic test: y = 3*x^2 - 5*x + 2
        y = np.array([29502, 119002, 268502, 478002, 747502])
        obs_poly, obs_deg = curve_fitting(x, y)
        exp_poly = np.array([3.0, -5.0, 2.0])
        exp_deg = 2
        assert_almost_equal(obs_poly, exp_poly)
        self.assertEqual(obs_deg, exp_deg)
        # Cubic test: y = x^3 - 5x^2 - 10x + 500
        y = np.array([949500, 7798500, 26547500, 63196500, 123745500])
        obs_poly, obs_deg = curve_fitting(x, y)
        exp_poly = np.array([1.0, -5.0, -10.0,  500.00000015])
        exp_deg = 3
        assert_almost_equal(obs_poly, exp_poly)
        self.assertEqual(obs_deg, exp_deg)

    def test_process_benchmark_results_num(self):
        """Correctly processes the benchmark results with numerical labels"""
        obs = process_benchmark_results(self.num_cases)
        labels = ['10', '20', '30']
        means = BenchData([102.4, 154.8, 209.282],
                          [98.2, 147.692, 200.594],
                          [1.596, 6.534, 6.7546],
                          [2528.4, 5153.2, 10537.2])
        std_devs = BenchData([1.8547237, 4.57820926, 2.76194424],
                             [0.55497748, 3.00350728, 2.87348986],
                             [0.11943199, 0.5011826, 1.13082653],
                             [5.23832034, 35.65052594, 68.93591227])
        wall_curve = FittedCurve(np.array([5.3441, 48.612]), 1)
        mem_curve = FittedCurve(np.array([13.796, -151.4, 2662.8]), 2)
        exp = SummarizedResults(labels, means, std_devs, wall_curve, mem_curve)
        self.assertEqual(obs.labels, exp.labels)
        assert_almost_equal(obs.means, exp.means)
        assert_almost_equal(obs.stdevs, exp.stdevs)
        assert_almost_equal(obs.wall_curve.poly, exp.wall_curve.poly)
        self.assertEqual(obs.wall_curve.deg, exp.wall_curve.deg)
        assert_almost_equal(obs.mem_curve.poly, exp.mem_curve.poly)
        self.assertEqual(obs.mem_curve.deg, exp.mem_curve.deg)

    def test_process_benchmark_results_str(self):
        """Correctly processes the benchmark results with numerical labels"""
        obs = process_benchmark_results(self.str_cases)
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

    def test_compare_benchmark_results_error(self):
        """Raises an error if the tests are not from the same bench suite"""
        with self.assertRaises(ValueError):
            compare_benchmark_results(self.results_error, self.labels)

    def test_compare_benchmark_results(self):
        """Correctly generates the strucute for comparing the benchmark results
        """
        obs = compare_benchmark_results(self.results, self.labels)
        exp = CompData(['10', '20', '30'],
                       {'data_series_1': ([102.4, 154.8, 209.282],
                                          [1.8547237, 4.57820926, 2.76194424]),
                        'data_series_2': ([102.4, 154.8, 209.282],
                                          [1.8547237, 4.57820926, 2.76194424])
                        },
                       {'data_series_1': ([2528.4, 5153.2, 10537.2],
                                          [5.23832034, 35.65052594,
                                           68.93591227]),
                        'data_series_2': ([2528.4, 5153.2, 10537.2],
                                          [5.23832034, 35.65052594,
                                           68.93591227])
                        })
        self.assertEqual(obs, exp)


if __name__ == '__main__':
    main()
