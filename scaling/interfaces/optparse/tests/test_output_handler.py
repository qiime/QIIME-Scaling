#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from imghdr import what
from os.path import join
from shutil import rmtree
from unittest import TestCase, main
from tempfile import mkdtemp

from pyqi.core.exception import IncompetentDeveloperError

from scaling.process_results import (SummarizedResults, BenchData, FittedCurve,
                                     CompData)

from scaling.interfaces.optparse.output_handler import (write_bench_results,
                                                        write_comp_results)


class OutputHandlerTests(TestCase):

    def setUp(self):
        self.output_dir = mkdtemp()

        num_label = ['100', '200', '300', '400', '500']
        str_label = ['file_100', 'file_200', 'file_300',
                     'file_400', 'file_500']
        means = BenchData([25, 50, 75, 100, 125],
                          [23, 46, 70, 94, 123],
                          [2, 4, 5, 6, 2],
                          [1048576, 2097152, 3145728, 4194304, 5242880])
        stdevs = BenchData([1, 2, 3, 4, 5],
                           [0.9, 2, 2.9, 4.1, 5],
                           [0.1, 0.0, 0.001, 0.2, 0.02],
                           [0.0, 0.0, 0.0, 0.2, 0.0])
        time_curve = FittedCurve([0.25, 0], 1)
        mem_curve = FittedCurve([10486, 0], 1)
        self.num_data = SummarizedResults(num_label, means, stdevs, time_curve,
                                          mem_curve)
        self.str_data = SummarizedResults(str_label, means, stdevs, time_curve,
                                          mem_curve)

        time = {'dataset1': ([25, 50, 75, 100, 125], [1, 2, 3, 4, 5]),
                'dataset2': ([50, 100, 150, 200, 250], [1, 2, 3, 4, 5])}
        mem = {'dataset1': ([1048576, 2097152, 3145728, 4194304, 5242880],
                            [0.0, 0.0, 0.0, 0.2, 0.0]),
               'dataset2': ([104857, 209715, 314572, 419430, 524288],
                            [0.0, 0.0, 0.0, 0.2, 0.0])}
        self.num_comp_data = CompData(num_label, time, mem)
        self.str_comp_data = CompData(str_label, time, mem)

    def tearDown(self):
        rmtree(self.output_dir)

    def test_write_bench_results_developer_error(self):
        """Raises an error if a path is not provided"""
        with self.assertRaises(IncompetentDeveloperError):
            write_bench_results('bench_data', self.num_data)

    def test_write_bench_results_oserror_error(self):
        """Raises an error if the output directory exists and its a file"""
        error_path = join(self.output_dir, 'foo.txt')
        with open(error_path, 'w') as f:
            f.write("bar")
        with self.assertRaises(IOError):
            write_bench_results('bench_data', self.num_data, error_path)

    def test_write_bench_results_correct_num(self):
        """Correctly writes the bench results with numerical labels"""
        write_bench_results('bench_data', self.num_data, self.output_dir)

        # Correctly generates the summarized_results.txt file
        fp = join(self.output_dir, 'summarized_results.txt')
        with open(fp, 'U') as f:
            obs = f.read()
        exp = ("#label\twall_mean\twall_std\tuser_mean\tuser_std\t"
               "kernel_mean\tkernel_std\tmem_mean\tmem_std\n"
               "100\t25\t1\t23\t0.9\t2\t0.1\t1048576\t0.0\n"
               "200\t50\t2\t46\t2\t4\t0.0\t2097152\t0.0\n"
               "300\t75\t3\t70\t2.9\t5\t0.001\t3145728\t0.0\n"
               "400\t100\t4\t94\t4.1\t6\t0.2\t4194304\t0.2\n"
               "500\t125\t5\t123\t5\t2\t0.02\t5242880\t0.0\n")
        self.assertEqual(obs, exp)

        # Correctly generates the curves.txt file
        fp = join(self.output_dir, 'curves.txt')
        with open(fp, 'U') as f:
            obs = f.read()
        exp = ("Wall time fitted curve\n0.25*x^1 + 0\n"
               "Memory usage fitted curve\n10486*x^1 + 0\n")
        self.assertEqual(obs, exp)

        # Correctly generates the plot figures
        fp = join(self.output_dir, 'time_fig.png')
        self.assertEqual(what(fp), 'png')
        fp = join(self.output_dir, 'mem_fig.png')
        self.assertEqual(what(fp), 'png')

    def test_write_bench_results_correct_str(self):
        """Correctly writes the bench results with string labels"""
        write_bench_results('bench_data', self.str_data, self.output_dir)

        # Correctly generates the summarized_results.txt file
        fp = join(self.output_dir, 'summarized_results.txt')
        with open(fp, 'U') as f:
            obs = f.read()
        exp = ("#label\twall_mean\twall_std\tuser_mean\tuser_std\t"
               "kernel_mean\tkernel_std\tmem_mean\tmem_std\n"
               "file_100\t25\t1\t23\t0.9\t2\t0.1\t1048576\t0.0\n"
               "file_200\t50\t2\t46\t2\t4\t0.0\t2097152\t0.0\n"
               "file_300\t75\t3\t70\t2.9\t5\t0.001\t3145728\t0.0\n"
               "file_400\t100\t4\t94\t4.1\t6\t0.2\t4194304\t0.2\n"
               "file_500\t125\t5\t123\t5\t2\t0.02\t5242880\t0.0\n")
        self.assertEqual(obs, exp)

        # Correctly generates the curves.txt file
        fp = join(self.output_dir, 'curves.txt')
        with open(fp, 'U') as f:
            obs = f.read()
        exp = ("Wall time fitted curve\n0.25*x^1 + 0\n"
               "Memory usage fitted curve\n10486*x^1 + 0\n")
        self.assertEqual(obs, exp)

        # Correctly generates the plot figures
        fp = join(self.output_dir, 'time_fig.png')
        self.assertEqual(what(fp), 'png')
        fp = join(self.output_dir, 'mem_fig.png')
        self.assertEqual(what(fp), 'png')

    def test_write_comp_results_developer_error(self):
        """Raises an error if a path is not provided"""
        with self.assertRaises(IncompetentDeveloperError):
            write_comp_results('comp_data', self.num_comp_data)

    def test_write_comp_results_oserror_error(self):
        """Raises an error if the output directory exists and its a file"""
        error_path = join(self.output_dir, 'foo.txt')
        with open(error_path, 'w') as f:
            f.write("bar")
        with self.assertRaises(IOError):
            write_comp_results('comp_data', self.num_comp_data, error_path)

    def test_write_comp_results_correct_num(self):
        """Correctly writes the comp results with numerical labels"""
        write_comp_results('comp_data', self.num_comp_data, self.output_dir)

        # Correctly generates the plot figures
        fp = join(self.output_dir, 'time_fig.png')
        self.assertEqual(what(fp), 'png')
        fp = join(self.output_dir, 'mem_fig.png')
        self.assertEqual(what(fp), 'png')

    def test_write_comp_results_correct_str(self):
        """Correctly writes the comp results with string labels"""
        write_comp_results('comp_data', self.str_comp_data, self.output_dir)

        # Correctly generates the plot figures
        fp = join(self.output_dir, 'time_fig.png')
        self.assertEqual(what(fp), 'png')
        fp = join(self.output_dir, 'mem_fig.png')
        self.assertEqual(what(fp), 'png')

if __name__ == '__main__':
    main()
