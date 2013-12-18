#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "GPL"
__version__ = "0.0.1-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from scaling.option_parsing import parse_command_line_parameters, make_option
from scaling.make_pbs import make_pbs
from os import makedirs

script_info = {}
script_info['brief_description'] = "Generates a PBS file for benchmark purposes"
script_info['script_description'] = "Given a QIIME command, a folder with "+\
    "benchmark files and the option used for providing input files to the "+\
    "QIIME command, this script generates a PBS file containing the needed "+\
    "calls to benchmark the QIIME command in a torque environment."

script_info['script_usage'] = [
    ("Example:", "Create a PBS file for benchmark the 'pick_de_novo_otus.py'"+\
        " QIIME script",
        "%prog -c \"pick_de_novo_otus.py\" -i bench_files --in_opts \"-i\" "),
    ("Example:","Create a PBS file for benchmark the 'split_libraries_fastq"+\
        ".py' QIIME script, which takes multiple files as input",
        "%prog -c \"split_libraries_fastq.py -m mapping.txt\" -i seqs_folder"+\
        ",barcode_folder --in_opts \"-i,-q\"")]
script_info['output_description'] = "A PBS file for submitting the benchmark"+\
    " calls in a torque system."

script_info['required_options'] = [
    make_option('-c', '--command', type='string',
        help='Command to benchmark.'),
    ]
script_info['optional_options'] = [
    make_option('-p', '--parameters', type='existing_filepath', default=None,
        help='Parameters file with the parameter values to test'),
    make_option('-i', '--input_dirs', type='existing_dirpaths', default=None,
        help='Comma-separated list of paths to the directories that contain '+\
            'the benchmark files. Should be in the same order as --in_opts'),

    make_option('--in_opts', type='string', default=None,
        help='Comma-separated list of options used for providing the '+\
            'benchmark files to the command. Should be in the same order as' +\
            '--input_dirs'),
    
    make_option('-o', '--output_fp', type='new_filepath',
        default='./submit_bench.pbs',
        help='The output PBS file path. [default: %default]'),

    make_option('--out_opt', type='string', default='-o',
        help='Option used for providing the output path to the command. '+\
            '[default: %default]'),

    make_option('-b', '--bench_dir', type='new_dirpath', default='./',
        help='Path to the directory where the output of the scripts and the ' +\
            'benchmark results will be stored. [default: %default]'),

    make_option('--name', type='string', default='benchmark',
        help='Name of the job. [default: %default]'),

    make_option('-n', '--num_reps', type='int', default='10',
        help='Number of times each command should be executed. ' +\
            '[default: %default]'),

    make_option('-f', '--force', action='store_true', default=False,
        help='Override the bench directory if it already exists')
    ]
script_info['version'] = __version__

if __name__ == '__main__':
    option_parser, opts, args = parse_command_line_parameters(**script_info)
    command = opts.command

    parameters = opts.parameters
    input_dirs = opts.input_dirs
    var_opts = opts.in_opts.split(',') if opts.in_opts else None

    pbs_fp = opts.output_fp
    out_opt = opts.out_opt
    bench_dir = opts.bench_dir
    name = opts.name
    num_reps = opts.num_reps
    force = opts.force


    if var_opts and input_dirs:
        if len(var_opts) != len(input_dirs):
            option_parser.error("The options --input_dirs and --in_opts must have "
                "the same number of elements.")

    if not parameters and not input_dirs:
        option_parser.error("One of the options --parameters or --input_dirs "
            "must be provided.")

    if parameters and input_dirs:
        option_parser.error("Only one of the options --parameters or "
            "--input_dirs must be provided.")

    try:
        makedirs(bench_dir)
    except OSError:
        if force:
            pass
        else:
            option_parser.error("Output directory already exists. Please "
                "choose a different directory, or force overwrite with -f.")

    make_pbs(command, var_opts, input_dirs, parameters, out_opt, bench_dir,
        pbs_fp, name, num_reps)
