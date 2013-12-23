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
from tempfile import mkdtemp
from scaling.process_results import (natural_sort, process_timing_directory,
    compute_rsquare, curve_fitting, generate_poly_label, make_bench_plot,
    process_benchmark_results, make_comparison_plot, compare_benchmark_results)
import os
from matplotlib.figure import Figure
from shutil import rmtree
import numpy as np
from scaling.util import OutputRedirect

class TestProcessResults(TestCase):
    def setUp(self):
        """Set up data for use in unit tests"""
        self.output_dir = mkdtemp()
        # Get the tests folder
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to the test timing folder
        self.timing_dir = os.path.join(tests_dir, 'support_files/timing')
        self.timing_dir_2 = os.path.join(tests_dir, 'support_files/timing_2')
        self.timing_dir_bad = os.path.join(tests_dir,
                                            'support_files/timing_bad')
        # Test dictionaries
        self.data = {
            'label' : [100, 200, 300, 400, 500],
            'wall_time' : ([54, 104, 154, 204, 254],
                            [1, 2, 3, 4, 5]),
            'cpu_user' : ([23, 46, 70, 94, 123],
                            [0.9, 2, 2.9, 4.1, 5]),
            'cpu_kernel' : ([2, 4, 5, 6, 2],
                [0.1, 0.0, 0.001, 0.2, 0.02]),
            'memory' : ([1048576, 2097152, 3145728, 4194304, 5242880],
                [0.0, 0.0, 0.0, 0.2, 0.0])
        }
        self.data2 = {
            'label' : [100, 200, 300, 400, 500],
            'wall_time' : ([30, 55, 80, 105, 130],
                            [1, 2, 3, 4, 5]),
            'cpu_user' : ([27, 50, 75, 98, 124],
                            [0.9, 2, 2.9, 4.1, 5]),
            'cpu_kernel' : ([3, 5, 5, 7, 6],
                [0.1, 0.0, 0.001, 0.2, 0.02]),
            'memory' : ([1048576, 2097152, 3145728, 4194304, 5242880],
                [0.0, 0.0, 0.0, 0.2, 0.0])
        }
        self.comp_data = {'foo' : self.data,
                          'bar' : self.data2}

    def tearDown(self):
        rmtree(self.output_dir)

    def test_natural_sort(self):
        """Correctly sorts a list in natural sort"""
        l = ['100_b','10_bb','100_a','20_aa','500_c', '9_c']
        exp =['9_c','10_bb','20_aa','100_a','100_b','500_c']
        obs = natural_sort(l)

        self.assertEqual(obs, exp)

    def test_process_timing_directory_correct(self):
        """Correctly retrieves the measurements from the timing directory"""
        stdout_red = OutputRedirect()
        with stdout_red as out:
            obs = process_timing_directory(self.timing_dir)
            obs_out = out.getvalue()
        exp = {
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
        # Check the contents of the observed dictionary
        self.assertEqual(obs.keys(), exp.keys())
        for o, e in zip(obs['label'], exp['label']):
            self.assertAlmostEqual(o, e)
        for key in ['wall_time', 'cpu_user', 'cpu_kernel', 'memory']:
            for o, e in zip(obs[key][0], exp[key][0]):
                self.assertAlmostEqual(o, e)
            for o, e in zip(obs[key][1], exp[key][1]):
                self.assertAlmostEqual(o, e)
        # Check the printed string
        exp = "Warning - File %s/20/5.txt not used:\n" % self.timing_dir
        self.assertEqual(obs_out, exp)

    def test_process_timing_directory_bad(self):
        """Raises error with a wrong directory structure"""
        with open(os.path.join(self.output_dir, 'foo.txt'), 'w') as f:
            f.write('bar\n')
        self.assertRaises(ValueError, process_timing_directory, self.output_dir)

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
        x = np.array([100,200,300,400,500])
        # Linear test: y = 5*x + 50
        y = np.array([550, 1050, 1550, 2050, 2550])
        obs_poly, obs_deg = curve_fitting(x, y)
        exp_poly = np.array([5.0, 50.0])
        exp_deg = 1
        for o, e in zip(obs_poly, exp_poly):
            self.assertAlmostEqual(o, e)
        self.assertEqual(obs_deg, exp_deg)
        # Quadratic test: y = 3*x^2 - 5*x + 2
        y = np.array([29502, 119002, 268502, 478002,747502])
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

    def test_generate_poly_label(self):
        """Correctly generates the string representing the polynomial"""
        # Linear test: y = 5*x + 50
        poly = np.array([5.0, 50.0])
        deg = 1
        obs = generate_poly_label(poly, deg)
        exp = "5.0*x^1 + 50.0"
        self.assertEqual(obs, exp)
        # Quadratic test: y = 3*x^2 - 5*x + 2
        poly = np.array([3.0, -5.0, 2.0])
        deg = 2
        obs = generate_poly_label(poly, deg)
        exp = "3.0*x^2 + -5.0*x^1 + 2.0"
        self.assertEqual(obs, exp)
        # Cubic test: y = x^3 - 5x^2 - 10x + 500
        poly = np.array([1.0, -5.0, -10.0, 500.0])
        deg = 3
        obs = generate_poly_label(poly, deg)
        exp = "1.0*x^3 + -5.0*x^2 + -10.0*x^1 + 500.0"
        self.assertEqual(obs, exp)

    def test_make_bench_plot(self):
        """Correctly generates the benchmark figure"""
        obs_fig, obs_label = make_bench_plot(self.data, 'wall_time',
                                             ['wall_time', 'cpu_user'],
                                             'foo', 'bar')
        self.assertEqual(obs_fig.__class__, Figure)
        self.assertEqual(obs_label, "0.5*x^1 + 4.0")

    def test_process_benchmark_results(self):
        """Correctly processes the benchmark results"""
        stdout_red = OutputRedirect()
        with stdout_red as out:
            data, time_fig, time_str, mem_fig, mem_str = \
                                    process_benchmark_results(self.timing_dir)
            obs_out = out.getvalue()

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
        # Check the contents of the observed dictionary
        self.assertEqual(data.keys(), exp_data.keys())
        for o, e in zip(data['label'], exp_data['label']):
            self.assertAlmostEqual(o, e)
        for key in ['wall_time', 'cpu_user', 'cpu_kernel', 'memory']:
            for o, e in zip(data[key][0], exp_data[key][0]):
                self.assertAlmostEqual(o, e)
            for o, e in zip(data[key][1], exp_data[key][1]):
                self.assertAlmostEqual(o, e)

        self.assertEqual(time_fig.__class__, Figure)
        self.assertEqual(time_str, "40.65768*x^1 + -12.541")
        self.assertEqual(mem_fig.__class__, Figure)
        self.assertEqual(mem_str, "864455.776*x^1 + 1260592.0")

        # Check the printed string
        exp = "Warning - File %s/20/5.txt not used:\n" % self.timing_dir
        self.assertEqual(obs_out, exp)

    def test_make_comparison_plot(self):
        """Correctly generates a comparison plot"""
        obs = make_comparison_plot(self.comp_data, self.data['label'],
                                   'wall_time', 'foo', 'bar')
        self.assertEqual(obs.__class__, Figure)

    def test_compare_benchmark_results(self):
        """Correctly generates comparison plots"""
        input_dirs = [self.timing_dir, self.timing_dir_2]
        labels = ['foo', 'bar']
        stdout_red = OutputRedirect()
        with stdout_red as out:
            time_fig, mem_fig = compare_benchmark_results(input_dirs, labels)
            obs_out = out.getvalue()
        self.assertEqual(time_fig.__class__, Figure)
        self.assertEqual(mem_fig.__class__, Figure)
        exp = ("Warning - File %s/20/5.txt not used:\nWarning - File "
            "%s/20/5.txt not used:\n" % (self.timing_dir, self.timing_dir_2))
        self.assertEqual(obs_out, exp)

    def test_compare_bencmark_results_error(self):
        """Correctly handles erroneous timing folders"""
        input_dirs = [self.timing_dir, self.timing_dir_bad]
        labels = ['foo', 'bar']
        stdout_red = OutputRedirect()
        with stdout_red as out:
            self.assertRaises(ValueError, compare_benchmark_results, input_dirs,
                              labels)

if __name__ == '__main__':
    main()