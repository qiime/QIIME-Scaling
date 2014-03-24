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
from scaling.util import natural_sort

class TestUtil(TestCase):
    def test_natural_sort(self):
        """Correctly sorts a list in natural sort"""
        l = ['100_b','10_bb','100_a','20_aa','500_c', '9_c']
        exp =['9_c','10_bb','20_aa','100_a','100_b','500_c']
        obs = natural_sort(l)

        self.assertEqual(obs, exp)

if __name__ == '__main__':
    main()