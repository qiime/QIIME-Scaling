#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

def parse_parameters_file(lines):
	"""Returns a dict with the parameters to test and its values

	Inputs:
		lines: open file object
	"""
	param_dict = {}
	for line in lines:
		line = line.strip()
		if line:
			(param, values) = line.split('\t')
			param_dict[param] = values.split(',')
	return param_dict