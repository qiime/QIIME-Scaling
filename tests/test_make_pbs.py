#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2013, The QIIME Scaling Project"
__credits__ = ["Jose Antonio Navas Molina"]
__license__ = "GPL"
__version__ = "0.0.1-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from cogent.util.unit_test import TestCase, main
from qiime.util import get_tmp_filename, load_qiime_config
from os import remove, mkdir
from os.path import join, exists
from shutil import rmtree
from scaling.make_pbs import get_bench_files, get_command_string, make_pbs_file

class TestMakePbs(TestCase):
    def setUp(self):
        # Get QIIME's temp dir
        self.qiime_config = load_qiime_config()
        self.tmp_dir = self.qiime_config['temp_dir'] or '/tmp/'

        # Single input example command
        self.single_input_command = "pick_de_novo_otus.py"

        # Multiple input example command
        self.mult_input_command = "split_libraries_fastq.py -m mapping.txt"

        self._paths_to_clean_up = []
        self._dirs_to_clean_up = []

    def tearDown(self):
        map(remove, self._paths_to_clean_up)
        map(rmtree, self._dirs_to_clean_up)

    def _create_bench_files_dir(self, multiple=False):
        """Creates a directory with some bench files on it
            If multiple is True, creates 2 directories instead of one
        """
        dir_name = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        mkdir(dir_name)

        bench_fp_1 = join(dir_name, '1.txt')
        f = open(bench_fp_1, 'w')
        f.close()
        bench_fp_2 = join(dir_name, '2.txt')
        f = open(bench_fp_2, 'w')
        f.close()
        bench_fp_3 = join(dir_name, '3.txt')
        f = open(bench_fp_3, 'w')
        f.close()
        files = [[bench_fp_1],
            [bench_fp_2],
            [bench_fp_3]]

        if multiple:
            dir_name_2 = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
            mkdir(dir_name_2)
            self._dirs_to_clean_up = [dir_name_2]

            bench_fp_1_b = join(dir_name_2, '1.txt')
            f = open(bench_fp_1_b, 'w')
            f.close()
            bench_fp_2_b = join(dir_name_2, '2.txt')
            f = open(bench_fp_2_b, 'w')
            f.close()
            bench_fp_3_b = join(dir_name_2, '3.txt')
            f = open(bench_fp_3_b, 'w')
            f.close()
            files = [[bench_fp_1, bench_fp_1_b],
                [bench_fp_2, bench_fp_2_b],
                [bench_fp_3, bench_fp_3_b]]

            dir_name = [dir_name, dir_name_2]

        return dir_name, files

    def test_get_bench_files_single(self):
        """Tests get_bench_files with a single directory"""
        # Create a directory with some 'bench' files on it
        dir_name, exp = self._create_bench_files_dir();
        self._dirs_to_clean_up = [dir_name]
        obs = get_bench_files([dir_name])
        self.assertEqual(obs, exp)

    def test_get_bench_files_multiple(self):
        """Tests get_bench_files with multiple directories"""
        dir_names, exp = self._create_bench_files_dir(multiple=True)
        self._dirs_to_clean_up = dir_names
        obs = get_bench_files(dir_names)
        self.assertEqual(obs, exp)

    def test_get_bench_files_error(self):
        """Tests get_bench_files raises an error is there is any directory"""
        # Create a directory inside a directory to check if it raises an error
        dir_break_base = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        mkdir(dir_break_base)
        dir_break = get_tmp_filename(tmp_dir=dir_break_base, suffix='')
        mkdir(dir_break)

        self._dirs_to_clean_up = [dir_break_base]

        self.assertRaises(ValueError, get_bench_files, [dir_break_base])

    def test_get_command_string_single(self):
        """Tests get_command_string using a command with a single input"""
        obs = get_command_string(self.single_input_command, ['-i'], 
            ['seqs.fna'], '-o', 'output_dir', 'time_dir', 0)
        exp = "timing_wrapper.sh time_dir/0.txt pick_de_novo_otus.py " +\
            " -i seqs.fna -o output_dir/0\n"
        self.assertEqual(obs, exp)

    def test_get_command_string_multiple(self):
        """Tests get_command_string using a command with multiple inputs"""
        obs = get_command_string(self.mult_input_command, ['-i', '-b'],
            ['seqs.fastq','barcodes.fastq'], '-o', 'output_dir', 'time_dir', 1)
        exp = "timing_wrapper.sh time_dir/1.txt split_libraries_fastq.py -m" +\
            " mapping.txt  -i seqs.fastq -b barcodes.fastq -o output_dir/1\n"
        self.assertEqual(obs, exp)

    def test_get_command_strin_error(self):
        """Tests get_command_string raises an error if number of opts and files
            are different
        """
        self.assertRaises(ValueError, get_command_string,
            self.mult_input_command, ['-i', '-b'], ['seqs.fastq'], '-o',
            'output_dir', 'time_dir', 1)

    def test_make_pbs_file_single(self):
        """Tests make_pbs_file using a command with a single input"""
        
        # Create bench files
        dir_name, files = self._create_bench_files_dir()
        bench_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        pbs_fp = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.pbs')

        self._dirs_to_clean_up = [dir_name, bench_dir]
        self._paths_to_clean_up = [pbs_fp]

        make_pbs_file(self.single_input_command, ['-i'], [dir_name], '-o', 
            bench_dir, pbs_fp, "test", 3, False)

        # Check the benchmark output structure has been created
        exp_timing_dir = join(bench_dir, 'timing')
        self.assertTrue(exists(exp_timing_dir))

        exp_timing_dir_1 = join(exp_timing_dir, '1')
        self.assertTrue(exists(exp_timing_dir_1))

        exp_timing_dir_2 = join(exp_timing_dir, '2')
        self.assertTrue(exists(exp_timing_dir_2))

        exp_timing_dir_3 = join(exp_timing_dir, '3')
        self.assertTrue(exists(exp_timing_dir_3))

        exp_output_dir = join(bench_dir, 'command_outputs')
        self.assertTrue(exists(exp_output_dir))

        exp_output_dir_1 = join(exp_output_dir, '1')
        self.assertTrue(exists(exp_output_dir_1))

        exp_output_dir_2 = join(exp_output_dir, '2')
        self.assertTrue(exists(exp_output_dir_2))

        exp_output_dir_3 = join(exp_output_dir, '3')
        self.assertTrue(exists(exp_output_dir_3))

        # Check the pbs file has been created
        self.assertTrue(exists(pbs_fp))

        # Check the pbs file contents
        f = open(pbs_fp, 'U')
        obs = f.readlines()
        f.close()
        exp = exp_single_pbs % (bench_dir, dir_name, bench_dir,
                                bench_dir, dir_name, bench_dir,
                                bench_dir, dir_name, bench_dir,
                                bench_dir, dir_name, bench_dir,
                                bench_dir, dir_name, bench_dir,
                                bench_dir, dir_name, bench_dir,
                                bench_dir, dir_name, bench_dir,
                                bench_dir, dir_name, bench_dir,
                                bench_dir, dir_name, bench_dir)
        exp = exp.replace("\"","").splitlines(True)
        self.assertEqual(obs, exp)

    def test_make_pbs_file_smultiple(self):
        """Tests make_pbs_file using a command with multiple inputs"""

        # Create bench files
        dir_names, files = self._create_bench_files_dir(multiple=True)
        bench_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        pbs_fp = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.pbs')

        self._dirs_to_clean_up = dir_names + [bench_dir]
        self._paths_to_clean_up = [pbs_fp]

        make_pbs_file(self.mult_input_command, ['-i', '-b'], dir_names, '-o',
            bench_dir, pbs_fp, "test", 2, False)

        # Check the benchmark output structure has been created
        exp_timing_dir = join(bench_dir, 'timing')
        self.assertTrue(exists(exp_timing_dir))

        exp_timing_dir_1 = join(exp_timing_dir, '1')
        self.assertTrue(exists(exp_timing_dir_1))

        exp_timing_dir_2 = join(exp_timing_dir, '2')
        self.assertTrue(exists(exp_timing_dir_2))

        exp_timing_dir_3 = join(exp_timing_dir, '3')
        self.assertTrue(exists(exp_timing_dir_3))

        exp_output_dir = join(bench_dir, 'command_outputs')
        self.assertTrue(exists(exp_output_dir))

        exp_output_dir_1 = join(exp_output_dir, '1')
        self.assertTrue(exists(exp_output_dir_1))

        exp_output_dir_2 = join(exp_output_dir, '2')
        self.assertTrue(exists(exp_output_dir_2))

        exp_output_dir_3 = join(exp_output_dir, '3')
        self.assertTrue(exists(exp_output_dir_3))

        # Check the pbs file has been created
        self.assertTrue(exists(pbs_fp))

        # Check the pbs file contents
        f = open(pbs_fp, 'U')
        obs = f.readlines()
        f.close()
        exp = exp_mult_pbs % (bench_dir, dir_names[0], dir_names[1], bench_dir,
                            bench_dir, dir_names[0], dir_names[1], bench_dir,
                            bench_dir, dir_names[0], dir_names[1], bench_dir,
                            bench_dir, dir_names[0], dir_names[1], bench_dir,
                            bench_dir, dir_names[0], dir_names[1], bench_dir,
                            bench_dir, dir_names[0], dir_names[1], bench_dir
                            )
        exp = exp.replace("\"","").splitlines(True)
        self.assertEqual(obs, exp)

    def test_make_pbs_file_error(self):
        """Tests make_pbs_file raises an error when the bench_dir exists"""
        bench_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        mkdir(bench_dir)
        self._dirs_to_clean_up = [bench_dir]
        self.assertRaises(ValueError, make_pbs_file, self.single_input_command,
            [], [], '', bench_dir, '', '', 1, False)


exp_single_pbs = """#!/bin/bash
#PBS -q memroute
#PBS -l pvmem=512gb
#PBS -N test
#PBS -k oe

# cd into the directory where 'qsub *.pbs' was run
cd $PBS_O_WORKDIR

# benchmarking commands:

timing_wrapper.sh %s/timing/1/0.txt pick_de_novo_otus.py  -i %s/1.txt -o %s/command_outputs/1/0
timing_wrapper.sh %s/timing/1/1.txt pick_de_novo_otus.py  -i %s/1.txt -o %s/command_outputs/1/1
timing_wrapper.sh %s/timing/1/2.txt pick_de_novo_otus.py  -i %s/1.txt -o %s/command_outputs/1/2
timing_wrapper.sh %s/timing/2/0.txt pick_de_novo_otus.py  -i %s/2.txt -o %s/command_outputs/2/0
timing_wrapper.sh %s/timing/2/1.txt pick_de_novo_otus.py  -i %s/2.txt -o %s/command_outputs/2/1
timing_wrapper.sh %s/timing/2/2.txt pick_de_novo_otus.py  -i %s/2.txt -o %s/command_outputs/2/2
timing_wrapper.sh %s/timing/3/0.txt pick_de_novo_otus.py  -i %s/3.txt -o %s/command_outputs/3/0
timing_wrapper.sh %s/timing/3/1.txt pick_de_novo_otus.py  -i %s/3.txt -o %s/command_outputs/3/1
timing_wrapper.sh %s/timing/3/2.txt pick_de_novo_otus.py  -i %s/3.txt -o %s/command_outputs/3/2
"""

exp_mult_pbs = """#!/bin/bash
#PBS -q memroute
#PBS -l pvmem=512gb
#PBS -N test
#PBS -k oe

# cd into the directory where 'qsub *.pbs' was run
cd $PBS_O_WORKDIR

# benchmarking commands:

timing_wrapper.sh %s/timing/1/0.txt split_libraries_fastq.py -m mapping.txt  -i %s/1.txt -b %s/1.txt -o %s/command_outputs/1/0
timing_wrapper.sh %s/timing/1/1.txt split_libraries_fastq.py -m mapping.txt  -i %s/1.txt -b %s/1.txt -o %s/command_outputs/1/1
timing_wrapper.sh %s/timing/2/0.txt split_libraries_fastq.py -m mapping.txt  -i %s/2.txt -b %s/2.txt -o %s/command_outputs/2/0
timing_wrapper.sh %s/timing/2/1.txt split_libraries_fastq.py -m mapping.txt  -i %s/2.txt -b %s/2.txt -o %s/command_outputs/2/1
timing_wrapper.sh %s/timing/3/0.txt split_libraries_fastq.py -m mapping.txt  -i %s/3.txt -b %s/3.txt -o %s/command_outputs/3/0
timing_wrapper.sh %s/timing/3/1.txt split_libraries_fastq.py -m mapping.txt  -i %s/3.txt -b %s/3.txt -o %s/command_outputs/3/1
"""

if __name__ == '__main__':
    main()