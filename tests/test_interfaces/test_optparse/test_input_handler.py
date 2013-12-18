#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

import os
from shutil import rmtree
from unittest import TestCase, main
from tempfile import mkdtemp
from scaling.interfaces.optparse.input_handler import (load_parameters,
                                                        get_bench_paths)

class InputHandlerTests(TestCase):
    def setUp(self):
        self.output_dir = mkdtemp()

        self.param_fp = os.path.join(self.output_dir, 'params.txt')
        with open(self.param_fp, 'w') as f:
            f.write(params)

        self.benchdir1 = os.path.join(self.output_dir, 'benchdir1')
        os.mkdir(self.benchdir1)
        self.bench_fp11 = os.path.join(self.benchdir1, '1_file.fna')
        with open(self.bench_fp11, 'w') as f:
            f.write("")
        self.bench_fp12 = os.path.join(self.benchdir1, '2_file.fna')
        with open(self.bench_fp12, 'w') as f:
            f.write("")
        self.bench_fp13 = os.path.join(self.benchdir1, '3_file.fna')
        with open(self.bench_fp13, 'w') as f:
            f.write("")

        self.benchdir2 = os.path.join(self.output_dir, 'benchdir2')
        os.mkdir(self.benchdir2)
        self.bench_fp21 = os.path.join(self.benchdir2, '1_file.fna')
        with open(self.bench_fp21, 'w') as f:
            f.write("")
        self.bench_fp22 = os.path.join(self.benchdir2, '2_file.fna')
        with open(self.bench_fp22, 'w') as f:
            f.write("")
        self.bench_fp23 = os.path.join(self.benchdir2, '3_file.fna')
        with open(self.bench_fp23, 'w') as f:
            f.write("")

        def tearDown(self):
            rmtree(self.output_dir)

    def test_load_parameters(self):
        """Correctly parses and loads the parameters"""
        obs = load_parameters(self.param_fp)
        self.assertEqual(type(obs), dict)

    def test_get_bench_paths(self):
        """Correctly traverses the input directories and creates paths list"""
        obs = get_bench_paths([self.benchdir1])
        exp = [[self.bench_fp11], [self.bench_fp12], [self.bench_fp13]]
        self.assertEqual(obs, exp)

        obs = get_bench_paths([self.benchdir1, self.benchdir2])
        exp = [[self.bench_fp11, self.bench_fp21],
                [self.bench_fp12, self.bench_fp22],
                [self.bench_fp13, self.bench_fp23]]
        self.assertEqual(obs, exp)        


params = """jobs_to_start\t4,8,16,32,64
similarity\t0.91,0.94,0.97,0.99"""

if __name__ == '__main__':
    main()