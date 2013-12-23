#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "GPL"
__version__ = "0.0.1-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

import sys
from StringIO import StringIO

class OutputRedirect:
    """Class to redirect the standard output to a StringIO"""
    saved_stdout = None
    def __enter__(self):
        self.saved_stdout = sys.stdout
        out = StringIO()
        sys.stdout = out
        return out
    def __exit__(self, type, value, tb):
        sys.stdout = self.saved_stdout