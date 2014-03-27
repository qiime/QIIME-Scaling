#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from os import mkdir
from os.path import join
from shutil import rmtree
from unittest import TestCase, main
from tempfile import mkdtemp

from scaling.parse import BenchSummary
from scaling.interfaces.optparse.input_handler import (
    load_summarized_results_list, load_parameters, get_bench_paths,
    parse_timing_directory, BenchCase)


class InputHandlerTests(TestCase):

    def setUp(self):
        self.output_dir = mkdtemp()

        # Create a parameter file
        params = "jobs_to_start\t4,8,16,32,64\nsimilarity\t0.91,0.94,0.97,0.99"
        self.param_fp = join(self.output_dir, 'params.txt')
        with open(self.param_fp, 'w') as f:
            f.write(params)

        # Create a couple of directories with fake bench files on them
        self.bench_dir_1 = join(self.output_dir, 'bench_dir_1')
        mkdir(self.bench_dir_1)
        self.bench_fp11 = join(self.bench_dir_1, '1_file.fna')
        self.bench_fp12 = join(self.bench_dir_1, '2_file.fna')
        self.bench_fp13 = join(self.bench_dir_1, '3_file.fna')
        with open(self.bench_fp11, 'w') as f:
            f.write("")
        with open(self.bench_fp12, 'w') as f:
            f.write("")
        with open(self.bench_fp13, 'w') as f:
            f.write("")

        self.bench_dir_2 = join(self.output_dir, 'bench_dir_2')
        mkdir(self.bench_dir_2)
        self.bench_fp21 = join(self.bench_dir_2, '1_file.fna')
        self.bench_fp22 = join(self.bench_dir_2, '2_file.fna')
        self.bench_fp23 = join(self.bench_dir_2, '3_file.fna')
        with open(self.bench_fp21, 'w') as f:
            f.write("")
        with open(self.bench_fp22, 'w') as f:
            f.write("")
        with open(self.bench_fp23, 'w') as f:
            f.write("")

        # Create a couple of summarize results files
        summary_data = ("#label\twall_mean\twall_std\tuser_mean\tuser_std\t"
                        "kernel_mean\tkernel_std\tmem_mean\tmem_std\n"
                        "100\t25\t1\t23\t0.9\t2\t0.1\t1048576\t0.0\n"
                        "200\t50\t2\t46\t2\t4\t0.0\t2097152\t0.0\n"
                        "300\t75\t3\t70\t2.9\t5\t0.001\t3145728\t0.0\n"
                        "400\t100\t4\t94\t4.1\t6\t0.2\t4194304\t0.2\n"
                        "500\t125\t5\t123\t5\t2\t0.02\t5242880\t0.0\n")
        self.summary_fp_1 = join(self.output_dir, 'summary_1')
        with open(self.summary_fp_1, 'w') as f:
            f.write(summary_data)
        self.summary_fp_2 = join(self.output_dir, 'summary_2')
        with open(self.summary_fp_2, 'w') as f:
            f.write(summary_data)

        # Create a directory with bench results
        self.results_dir = mkdtemp(dir=self.output_dir)
        case_dir = join(self.results_dir, '10')
        mkdir(case_dir)
        case_file = join(case_dir, '0.txt')
        with open(case_file, 'w') as f:
            f.write("415.29;388.29;11.35;9710640")
        case_file = join(case_dir, '1.txt')
        with open(case_file, 'w') as f:
            f.write("392.73;381.52;5.60;9710576")
        case_file = join(case_dir, '2.txt')
        with open(case_file, 'w') as f:
            f.write("396.18;382.33;5.45;9710624")
        case_file = join(case_dir, '3.txt')
        with open(case_file, 'w') as f:
            f.write("392.42;382.32;5.49;9710384")
        case_file = join(case_dir, '4.txt')
        with open(case_file, 'w') as f:
            f.write("390.61;382.26;5.50;9710512")

        case_dir = join(self.results_dir, '20')
        mkdir(case_dir)
        case_file = join(case_dir, '0.txt')
        with open(case_file, 'w') as f:
            f.write("815.21;771.32;22.17;18742320")
        case_file = join(case_dir, '1.txt')
        with open(case_file, 'w') as f:
            f.write("820.33;799.58;11.57;18744128")
        case_file = join(case_dir, '2.txt')
        with open(case_file, 'w') as f:
            f.write("788.19;765.59;11.02;18742704")
        case_file = join(case_dir, '3.txt')
        with open(case_file, 'w') as f:
            f.write("779.50;755.76;11.60;18742352")
        case_file = join(case_dir, '4.txt')
        with open(case_file, 'w') as f:
            f.write("784.72;763.28;11.36;18744976")

        case_dir = join(self.results_dir, '30')
        mkdir(case_dir)
        case_file = join(case_dir, '0.txt')
        with open(case_file, 'w') as f:
            f.write("1240.57;1177.48;32.92;27386400")
        case_file = join(case_dir, '1.txt')
        with open(case_file, 'w') as f:
            f.write("1191.88;1157.41;16.28;27389792")
        case_file = join(case_dir, '2.txt')
        with open(case_file, 'w') as f:
            f.write("1202.94;1174.34;15.95;27392640")
        case_file = join(case_dir, '3.txt')
        with open(case_file, 'w') as f:
            f.write("1181.67;1151.60;16.27;27393424")
        case_file = join(case_dir, '4.txt')
        with open(case_file, 'w') as f:
            f.write("1197.96;1170.66;16.62;27392224")

    def tearDown(self):
        rmtree(self.output_dir)

    def test_load_parameters(self):
        """Correctly parses and loads the parameters"""
        obs = load_parameters(self.param_fp)
        exp = exp = {'jobs_to_start': ['4', '8', '16', '32', '64'],
                     'similarity': ['0.91', '0.94', '0.97', '0.99']}
        self.assertEqual(obs, exp)

    def test_load_summarized_results_list(self):
        """Correctly loads a list of results summary files"""
        obs = list(load_summarized_results_list([self.summary_fp_1]))
        self.assertEqual(len(obs), 1)
        self.assertEqual(type(obs[0]), BenchSummary)

        obs = list(load_summarized_results_list([self.summary_fp_1,
                                                 self.summary_fp_2]))
        self.assertEqual(len(obs), 2)
        for o in obs:
            self.assertEqual(type(o), BenchSummary)

    def test_get_bench_paths(self):
        """Correctly traverses the input directories and creates paths list"""
        obs = get_bench_paths([self.bench_dir_1])
        exp = [[self.bench_fp11], [self.bench_fp12], [self.bench_fp13]]
        self.assertEqual(obs, exp)

        obs = get_bench_paths([self.bench_dir_1, self.bench_dir_2])
        exp = [[self.bench_fp11, self.bench_fp21],
               [self.bench_fp12, self.bench_fp22],
               [self.bench_fp13, self.bench_fp23]]
        self.assertEqual(obs, exp)

    def test_parse_timing_directory_correct(self):
        """Correctly retrieves the measurements from the timing directory"""
        obs = list(parse_timing_directory(self.results_dir))
        exp = [BenchCase('10',
                         [415.29, 392.73, 396.18, 392.42, 390.61],
                         [388.29, 381.52, 382.33, 382.32, 382.26],
                         [11.35, 5.60, 5.45, 5.49, 5.50],
                         [9710640, 9710576, 9710624, 9710384, 9710512]),
               BenchCase('20',
                         [815.21, 820.33, 788.19, 779.50, 784.72],
                         [771.32, 799.58, 765.59, 755.76, 763.28],
                         [22.17, 11.57, 11.02, 11.60, 11.36],
                         [18742320, 18744128, 18742704, 18742352, 18744976]),
               BenchCase('30',
                         [1240.57, 1191.88, 1202.94, 1181.67, 1197.96],
                         [1177.48, 1157.41, 1174.34, 1151.60, 1170.66],
                         [32.92, 16.28, 15.95, 16.27, 16.62],
                         [27386400, 27389792, 27392640, 27393424, 27392224])
               ]
        self.assertEqual(obs, exp)

    def test_parse_timing_directory_bad(self):
        """Raises error with a wrong directory structure"""
        with open(join(self.results_dir, 'foo.txt'), 'w') as f:
            f.write('bar\n')

        with self.assertRaises(ValueError):
            list(parse_timing_directory(self.results_dir))


if __name__ == '__main__':
    main()
