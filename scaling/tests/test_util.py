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

from scaling.util import natural_sort, generate_poly_label


class TestUtil(TestCase):
    def test_natural_sort(self):
        """Correctly sorts a list in natural sort"""
        l = ['100_b', '10_bb', '100_a', '20_aa', '500_c', '9_c']
        exp = ['9_c', '10_bb', '20_aa', '100_a', '100_b', '500_c']
        obs = natural_sort(l)

        self.assertEqual(obs, exp)

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

if __name__ == '__main__':
    main()
