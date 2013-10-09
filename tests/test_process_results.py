#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "GPL"
__version__ = "0.0.1-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from cogent.util.unit_test import TestCase, main
from qiime.util import load_qiime_config, get_tmp_filename
from os import remove, mkdir
from os.path import dirname, abspath, join, exists
from shutil import rmtree
import numpy as np
from string import digits
from scaling.process_results import (process_timing_directory, natural_sort,
    write_summarized_results, compute_rsquare, curve_fitting,
    generate_poly_label, make_plots, process_benchmark_results,
    make_comparison_plots, compare_benchmark_results)

class TestProcessResults(TestCase):
    def setUp(self):
        # Get the tests folder
        tests_dir = dirname(abspath(__file__))
        # Path to the test timing folder
        self.timing_dir = join(tests_dir, 'support_files/timing')
        self.timing_dir_2 = join(tests_dir, 'support_files/timing_2')
        self.timing_dir_bad = join(tests_dir, 'support_files/timing_bad')
        # Get QIIME's temp dir
        self.qiime_config = load_qiime_config()
        self.tmp_dir = self.qiime_config['temp_dir'] or '/tmp/'
        # Test dictionaries
        self.data = {
            'label' : [100, 200, 300, 400, 500],
            'wall_time' : ([25, 50, 75, 100, 125],
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
        # Clean up variables
        self._paths_to_clean_up = []
        self._dirs_to_clean_up = []

    def tearDown(self):
        map(remove, self._paths_to_clean_up)
        map(rmtree, self._dirs_to_clean_up)

    def remove_nums(self, text):
        """Removes all digits from the given string.

        Returns the string will all digits removed. Useful for testing strings
        for equality in unit tests where you don't care about numeric values,
        or if some values are random.

        This code was taken from http://bytes.com/topic/python/answers/
            850562-finding-all-numbers-string-replacing

        Arguments:
            text - the string to remove digits from
        """
        return text.translate(None, digits)

    def test_natural_sort(self):
        """Tests natural_sort performs natural sort correctly"""
        l = ['100_b','10_bb','100_a','20_aa','500_c', '9_c']
        exp =['9_c','10_bb','20_aa','100_a','100_b','500_c']
        obs = natural_sort(l)

        self.assertEqual(obs, exp)

    def test_process_timing_directory_correct(self):
        """Tests process_timing_directory with a correct directory"""
        # Get a tmp path for a log file
        log_fp = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.txt')
        log_file = open(log_fp, 'w')
        
        # Add the log file to the clean up variable
        self._paths_to_clean_up = [log_fp]

        obs = process_timing_directory(self.timing_dir, log_file)
        exp = {
            'label' : [10.0, 20.0, 30.0, 40.0],
            'wall_time' : ([397.446, 797.59, 1203.004, 1617.564],
                        [9.102124148, 16.78580948, 20.07751638, 76.82548135]),
            'cpu_user' : ([383.344, 771.106, 1166.298, 1572.904],
                        [2.491654872, 15.08632971, 10.03758616, 59.19994041]),
            'cpu_kernel' : ([6.678, 13.544, 19.608, 25.89],
                        [2.336522202, 4.317965262, 6.659373544, 7.725679258]),
            'memory' : ([9710547.2, 18743296, 27390896, 35643206.4],
                        [92.9653699, 1068.531703, 2554.554208, 3185.496734])
        }
        log_file.close()

        # Check the two dictionaries are the same
        self.assertEqual(obs.keys(), exp.keys())
        self.assertFloatEqual(obs['label'], exp['label'])
        for key in ['wall_time', 'cpu_user', 'cpu_kernel', 'memory']:
            self.assertFloatEqual(obs[key][0], exp[key][0])
            self.assertFloatEqual(obs[key][1], exp[key][1])
        # Check that the contents of the log file are correct
        log_file = open(log_fp, 'U')
        obs = log_file.readlines()
        log_file.close()
        exp = exp_log_process_timing_dir % self.timing_dir
        exp = exp.splitlines(True)
        self.assertEqual(obs, exp)

    def test_process_timing_directory_bad(self):
        """Tests process_timing_directory raises an error with a bad directory
        """
        dir_name = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        mkdir(dir_name)
        filename = get_tmp_filename(tmp_dir=dir_name, suffix='.txt')
        f = open(filename, 'w')
        f.close()
        self._dirs_to_clean_up = [dir_name]
        self.assertRaises(ValueError, process_timing_directory, dir_name, "")

    def test_write_summarized_results(self):
        """Tests write_summarized_results generates the correct file"""
        filename = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.txt')
        self._paths_to_clean_up = [filename]
        write_summarized_results(self.data, filename)
        self.assertTrue(exists(filename))
        f = open(filename, 'U')
        obs = f.readlines()
        f.close()
        exp = exp_write_summarized_results.splitlines(True)
        self.assertEqual(obs, exp)

    def test_compute_rsquare(self):
        """Tests compute_rsquare generates the correct answer"""
        y = np.array([15.0, 20.0, 25.0, 30.0, 35.0])
        SSerr = np.array([0.05])
        obs = compute_rsquare(y, SSerr)
        exp = 0.9998
        self.assertFloatEqual(obs, exp)

        y = np.array([10, 12, 15, 25, 50])
        SSerr = np.array([0.03])
        obs = compute_rsquare(y, SSerr)
        exp = 0.999972
        self.assertFloatEqual(obs, exp)

    def test_curve_fitting(self):
        """Tests curve_fitting returns correct polynomial"""
        x = np.array([100,200,300,400,500])
        # Linear test: y = 5*x + 50
        y = np.array([550, 1050, 1550, 2050, 2550])
        obs_poly, obs_deg = curve_fitting(x, y)
        exp_poly = np.array([5.0, 50.0])
        exp_deg = 1
        self.assertFloatEqual(obs_poly, exp_poly)
        self.assertEqual(obs_deg, exp_deg)
        # Quadratic test: y = 3*x^2 - 5*x + 2
        y = np.array([29502, 119002, 268502, 478002,747502])
        obs_poly, obs_deg = curve_fitting(x, y)
        exp_poly = np.array([3.0, -5.0, 2.0])
        exp_deg = 2
        self.assertFloatEqual(obs_poly, exp_poly)
        self.assertEqual(obs_deg, exp_deg)
        # Cubic test: y = x^3 - 5x^2 - 10x + 500
        y = np.array([949500, 7798500, 26547500, 63196500, 123745500])
        obs_poly, obs_deg = curve_fitting(x, y)
        exp_poly = np.array([1.0, -5.0, -10.0, 500.0])
        exp_deg = 3
        self.assertFloatEqual(obs_poly, exp_poly)
        self.assertEqual(obs_deg, exp_deg)
        # Test with linear = True
        y = np.array([550, 1050.00005, 1550, 2049.99995, 2550])
        obs_poly, obs_deg = curve_fitting(x, y, lineal=True)
        exp_poly = np.array([5.0, 50.0])
        exp_deg = 1
        self.assertFloatEqual(obs_poly, exp_poly)
        self.assertEqual(obs_deg, exp_deg)

    def test_generate_poly_label(self):
        """Tests generate_poly_label returns correct string"""
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

    def test_make_plots(self):
        """Tests make_plots generates plots in the correct place"""
        out_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        mkdir(out_dir)
        log_fp = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.txt')
        log_file = open(log_fp, 'w')
        self._dirs_to_clean_up = [out_dir]
        self._paths_to_clean_up = [log_fp]
        make_plots(self.data, out_dir, log_file)
        log_file.close()
        # Check the plots exists
        self.assertTrue(exists(join(out_dir, 'time_plot.png')))
        self.assertTrue(exists(join(out_dir, 'memory_plot.png')))
        self.assertTrue(exists(join(out_dir, 'time_plot_lin.png')))
        self.assertTrue(exists(join(out_dir, 'memory_plot_lin.png')))
        # Check the contents of the log file
        f = open(log_fp, 'U')
        obs = f.readlines()
        f.close()
        exp = exp_log_make_plots.splitlines(True)
        for o, e in zip(obs, exp):
            self.assertEqual(self.remove_nums(o), e)

    def test_process_benchmark_results(self):
        """Tests process_benchmark_results"""
        out_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        self._dirs_to_clean_up = [out_dir]
        process_benchmark_results(self.timing_dir, out_dir)
        log_fp = join(out_dir, 'get_benchmark_results_log.txt')
        time_fp = join(out_dir, 'time_plot.png')
        mem_fp = join(out_dir, 'memory_plot.png')
        time_lin_fp = join(out_dir, 'time_plot_lin.png')
        mem_lin_fp = join(out_dir, 'memory_plot_lin.png')
        summ_fp = join(out_dir, 'summarized_results.txt')
        self.assertTrue(exists(log_fp))
        self.assertTrue(exists(time_fp))
        self.assertTrue(exists(mem_fp))
        self.assertTrue(exists(time_lin_fp))
        self.assertTrue(exists(mem_lin_fp))
        self.assertTrue(exists(summ_fp))

    def test_make_comparison_plots(self):
        """Tests make_comparison_plots generates plots int he correct place"""
        out_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        mkdir(out_dir)
        log_fp = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.log')
        log_file = open(log_fp, 'w')
        self._dirs_to_clean_up = [out_dir]
        self._paths_to_clean_up = [log_fp]
        x_axis = self.data['label']
        data_dict = {
            'labelA': self.data,
            'labelB': self.data2
        }
        make_comparison_plots(data_dict, x_axis, out_dir, log_file)
        log_file.close()
        # Check the plots exist
        self.assertTrue(exists(join(out_dir, 'comp_time_plot.png')))
        self.assertTrue(exists(join(out_dir, 'comp_mem_plot.png')))
        # Check the contents of the log file
        f = open(log_fp, 'U')
        obs = f.readlines()
        f.close()
        exp = exp_log_compare_plots.splitlines(True)
        self.assertEqual(obs, exp)

    def test_compare_benchmark_results(self):
        """Tests compare_benchmark_results"""
        out_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        self._dirs_to_clean_up = [out_dir]
        path_list = [self.timing_dir, self.timing_dir_2]
        labels = ['labelA', 'labelB']
        compare_benchmark_results(path_list, labels, out_dir)
        log_fp = join(out_dir, 'compare_bench_results.log')
        time_fp = join(out_dir, 'comp_time_plot.png')
        mem_fp = join(out_dir, 'comp_mem_plot.png')
        self.assertTrue(exists(log_fp))
        self.assertTrue(exists(time_fp))
        self.assertTrue(exists(mem_fp))
        # Test that raises a ValueError when the benchmarks have been run
        # over a different benchmark set
        out_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        self._dirs_to_clean_up.append(out_dir)
        path_list = [self.timing_dir, self.timing_dir_bad]
        self.assertRaises(ValueError, compare_benchmark_results, path_list,
            labels, out_dir)



exp_log_process_timing_dir = """File %s/20/5.txt not used: the command didn't finish correctly\n"""

exp_write_summarized_results = """#label\twall_mean\twall_std\tuser_mean\tuser_std\tkernel_mean\tkernel_std\tmem_mean\tmem_std
100\t25\t1\t23\t0.9\t2\t0.1\t1048576\t0.0
200\t50\t2\t46\t2\t4\t0.0\t2097152\t0.0
300\t75\t3\t70\t2.9\t5\t0.001\t3145728\t0.0
400\t100\t4\t94\t4.1\t6\t0.2\t4194304\t0.2
500\t125\t5\t123\t5\t2\t0.02\t5242880\t0.0
"""

exp_log_make_plots = """Generating time plot... 
Best fit: .*x^ + .e-
Generating time plot finished
Generating lineal time plot... 
Best fit: .*x^ + .e-
Generating lineal time plot finished
Generating memory plot... 
Best fit: .*x^ + .e-
Generating memory plot finished
Generating lineal memory plot... 
Best fit: .*x^ + .e-
Generating lineal memory plot finished
"""

exp_log_compare_plots = """Generating time plot...
Generating time plot finished
Generating memory plot...
Generating memory plot finished
"""


if __name__ == '__main__':
    main()