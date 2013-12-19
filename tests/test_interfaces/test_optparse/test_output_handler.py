#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from matplotlib import use
use('Agg', warn=False)
import matplotlib.pyplot as plt
import numpy as np
import os
import imghdr
from shutil import rmtree
from unittest import TestCase, main
from tempfile import mkdtemp
from pyqi.core.exception import IncompetentDeveloperError
from scaling.interfaces.optparse.output_handler import (write_summarized_results,
                                                        write_matplotlib_figure,
                                                        write_string_to_dir)

class OutputHandlerTests(TestCase):
    def setUp(self):
        self.output_dir = mkdtemp()
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
        self.figure = plt.figure()
        # ax = self.figure.add_subplot(111)
        # ax.plot()

    def tearDown(self):
        rmtree(self.output_dir)

    def test_write_summarized_results(self):
        """Correctly writes the bench results to a file"""
        # Can't write without a path
        self.assertRaises(IncompetentDeveloperError, write_summarized_results,
                          'a', self.data)
        write_summarized_results('foo', self.data, self.output_dir)
        fp = os.path.join(self.output_dir, 'foo.txt')
        with open(fp, 'U') as obs_f:
            obs = obs_f.read()
        self.assertEqual(obs, exp_write_summarized_results)

    def test_write_matplotlib_figure(self):
        """Correctly writes a matplotlib figure to a file"""
        # Can't write without a path
        self.assertRaises(IncompetentDeveloperError, write_matplotlib_figure,
                          'a', self.figure)
        write_matplotlib_figure('foo', self.figure, self.output_dir)
        fp = os.path.join(self.output_dir, 'foo.png')
        self.assertEqual(imghdr.what(fp), 'png')

    def test_write_string_to_dir(self):
        """Correctly writes a string in a directory"""
        # Can't write without a path
        self.assertRaises(IncompetentDeveloperError, write_string_to_dir,
                          'a', 'foo')
        write_string_to_dir('foo', 'bar', self.output_dir)
        fp = os.path.join(self.output_dir, 'foo.txt')
        with open(fp, 'U') as obs_f:
            obs = obs_f.read()

        self.assertEqual(obs, 'bar\n')


exp_write_summarized_results = """#label\twall_mean\twall_std\tuser_mean\tuser_std\tkernel_mean\tkernel_std\tmem_mean\tmem_std
100\t25\t1\t23\t0.9\t2\t0.1\t1048576\t0.0
200\t50\t2\t46\t2\t4\t0.0\t2097152\t0.0
300\t75\t3\t70\t2.9\t5\t0.001\t3145728\t0.0
400\t100\t4\t94\t4.1\t6\t0.2\t4194304\t0.2
500\t125\t5\t123\t5\t2\t0.02\t5242880\t0.0
"""

if __name__ == '__main__':
    main()