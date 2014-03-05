#!/usr/bin/env python
from __future__ import division

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "BSD"
__version__ = "0.0.2-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from pyqi.core.interfaces.optparse import (OptparseUsageExample,
                                           OptparseOption, OptparseResult)
from pyqi.core.command import (make_command_in_collection_lookup_f,
                               make_command_out_collection_lookup_f)
from pyqi.core.interfaces.optparse.input_handler import string_list_handler
from pyqi.core.interfaces.optparse.output_handler import write_string
from scaling.commands.bench_suite_maker import CommandConstructor
from scaling.interfaces.optparse.input_handler import (get_bench_paths,
                                                       load_parameters)

# Convenience function for looking up parameters by name.
cmd_in_lookup = make_command_in_collection_lookup_f(CommandConstructor)
cmd_out_lookup = make_command_out_collection_lookup_f(CommandConstructor)

# Examples of how the command can be used from the command line using an
# optparse interface.
usage_examples = [
    OptparseUsageExample(ShortDesc="Parameters example usage",
                         LongDesc="Test the command \"pick_otus.py\" using "
                         "different similarity values. The file parameters.txt"
                         " should follow these structure\nsimilarity<tab>"
                         "val1,val2,val3",
                         Ex="%prog -c \"pick_otus.py -i seqs.fna\" -p "
                         "parameters.txt -o pick_otus_bench_suite.sh"),
    OptparseUsageExample(ShortDesc="Input files example usage",
                         LongDesc="Test the command \"pick_otus.py\" using "
                         "different input files. The folder bench_files should"
                         " include only the input files used by the command",
                         Ex="%prog -c \"pick_otus.py\" -i bench_files -o "
                         "pick_otus_bench_suite.sh"),
    OptparseUsageExample(ShortDesc="Multiple input files example usage",
                         LongDesc="Test the command \"split_librarires_fastq."
                         "py\" using different input files. These command "
                         "takes the input file in pairs so we provide the "
                         "input files in two different folders",
                         Ex="%prog -c \"split_librarires_fastq.py -m "
                         "mapping.txt\" -i seqs_folder,barcode_folder "
                         "--in_opts \"-i,-q\" -o "
                         "split_librarires_fastq_bench_suite.sh")
]

# inputs map command line arguments and values onto Parameters. It is possible
# to define options here that do not exist as parameters, e.g., an output file.
inputs = [
    OptparseOption(Parameter=cmd_in_lookup('bench_files'),
                   Type='existing_dirpaths',
                   Action='store',
                   Handler=get_bench_paths,
                   ShortName='i',
                   # Name='bench_files',
                   # Required=False,
                   # Help='List of lists of paths to the benchmark files to use
                   #    as input for the command. Each inner list is a test
                   #    case and should have the same length as the in_opts
                   #    parameter.',
                   # Default=None,
                   # DefaultDescription='No bench_files used',
                   ),
    OptparseOption(Parameter=cmd_in_lookup('command'),
                   Type='str',
                   Action='store',
                   Handler=None,
                   ShortName='c',
                   # Name='command',
                   # Required=True,
                   # Help='command to benchmark',
                   ),
    OptparseOption(Parameter=cmd_in_lookup('in_opts'),
                   Type='str',
                   Action='store',
                   Handler=string_list_handler,
                   ShortName=None,
                   # Name='in_opts',
                   # Required=False,
                   # Help='list of options used for providing the benchmark
                   #    files to the command. It should have the same length
                   #    and order than the inner lists of bench_files.'
                   Default='-i',
                   # DefaultDescription='["-i"] is used as a default'
                   ),
    OptparseOption(Parameter=cmd_in_lookup('out_opt'),
                   Type='str',
                   Action='store',
                   Handler=None,
                   ShortName=None,
                   # Name='out_opt', # implied by Parameter
                   # Required=False, # implied by Parameter
                   # Help='Option used for providing the output path to the
                   #    command to benchmark.',
                   # Default='-o',
                   # DefaultDescription='"-o" is used as default'
                   ),
    OptparseOption(Parameter=cmd_in_lookup('parameters'),
                   Type='existing_filepath',
                   Action='store',
                   Handler=load_parameters,
                   ShortName='p',
                   # Name='parameters',
                   # Required=False,
                   # Help='dictionary where the keys are the parameters to test
                   #    and the values are a list of values for such
                   #    parameter.',
                   # Default=None,
                   # DefaultDescription='No parameters used',
                   ),
    OptparseOption(Parameter=cmd_in_lookup('pbs'),
                   Type=None,
                   Action='store_true',
                   Handler=None,
                   ShortName=None,
                   ),
    OptparseOption(Parameter=cmd_in_lookup('job_prefix'),
                   Type=str,
                   Action='store',
                   Handler=None,
                   ShortName=None,
                   ),
    OptparseOption(Parameter=cmd_in_lookup('queue'),
                   Type=str,
                   Action='store',
                   Handler=None,
                   ShortName=None,
                   ),
    OptparseOption(Parameter=cmd_in_lookup('pbs_extra_args'),
                   Type=str,
                   Action='store',
                   Handler=None,
                   ShortName=None,
                   ),
    OptparseOption(Parameter=None,
                   Type='new_filepath',
                   ShortName='o',
                   Name='output-fp',
                   Required=True,
                   Help='the output filepath')
]

# outputs map result keys to output options and handlers. It is not necessary
# to supply an associated option, but if you do, it must be an option from the
# inputs list (above).
outputs = [
    OptparseResult(Parameter=cmd_out_lookup('bench_suite'),
                   Handler=write_string,
                   InputName='output-fp'),
]
