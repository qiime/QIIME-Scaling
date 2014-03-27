#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from re import split
from collections import namedtuple

BenchCase = namedtuple('BenchCase', ('label', 'wall', 'user', 'kernel', 'mem'))
SummarizedResults = namedtuple('SummarizedResults', ('labels', 'means',
                                                     'stdevs', 'wall_curve',
                                                     'mem_curve'))
BenchData = namedtuple('BenchData', ('wall', 'user', 'kernel', 'mem'))
FittedCurve = namedtuple('FittedCurve', ('poly', 'deg'))
CompData = namedtuple('CompData', ('x', 'time', 'mem'))
BenchSummary = namedtuple('BenchSummary', ('label', 'wall_mean',
                                           'wall_stdev', 'user_mean',
                                           'user_stdev', 'kernel_mean',
                                           'kernel_stdev', 'mem_mean',
                                           'mem_stdev'))


def natural_sort(l):
    """Sorts the given list in the way that humans expect.

    Code adapted from:
        http://www.codinghorror.com/blog/2007/12/
            sorting-for-humans-natural-sort-order.html

    Parameters
    ----------
    l : list
        The list to be sorted

    Returns
    -------
    list
        The sorted list
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in split('([0-9]+)', key)]
    l.sort(key=alphanum_key)
    return l


def generate_poly_label(poly, deg):
    """Returns a string representing the given polynomial

    Parameters
    ----------
    poly: numpy array of float
        The coefficients of the polynomial
    deg: float
        The degree of the polynomial

    Returns
    -------
    string
        The string representation of the polynomial
    """
    s = ["%s*x^%s + " % (poly[i], deg-i) for i in range(deg)]
    s.append(str(poly[deg]))
    return "".join(s)
