#!/usr/bin/env python

from qiime.pycogent_backports.option_parsing import *

def check_existing_dirpaths(option, opt, value):
    paths = value.split(',')
    values = []
    for v in paths:
        check_existing_dirpath(option, opt, v)
        values.append(v)
    return values

class ScalingOption(CogentOption):
    TYPES = CogentOption.TYPES + ("existing_dirpaths",)
    
    TYPE_CHECKER = copy(CogentOption.TYPE_CHECKER)
    # for cases where the user passes one or more existing directories
    # as a comma-separated list - paths are returned as a list
    TYPE_CHECKER["existing_dirpaths"] = check_existing_dirpaths

make_option = ScalingOption