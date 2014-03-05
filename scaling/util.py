#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

import sys
from StringIO import StringIO
from re import split


class OutputRedirect:
    """Class to redirect the std output to StringIO using a `with` statement"""
    saved_stdout = None

    def __enter__(self):
        self.saved_stdout = sys.stdout
        out = StringIO()
        sys.stdout = out
        return out

    def __exit__(self, type, value, tb):
        sys.stdout = self.saved_stdout


def natural_sort(l):
    """ Sort the given list in the way that humans expect.
        Code adapted from:
            http://www.codinghorror.com/blog/2007/12/
                sorting-for-humans-natural-sort-order.html
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in split('([0-9]+)', key)]
    l.sort(key=alphanum_key)
    return l
