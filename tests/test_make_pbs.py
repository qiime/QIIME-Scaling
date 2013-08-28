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
from scaling.make_pbs import (get_bench_files, get_bench_params,
                              get_command_string, write_commands_files,
                              write_commands_parameters, make_pbs)

class TestMakePbs(TestCase):
    def setUp(self):
        # Get QIIME's temp dir
        self.qiime_config = load_qiime_config()
        self.tmp_dir = self.qiime_config['temp_dir'] or '/tmp/'

        # Single input example command
        self.single_input_command = "pick_de_novo_otus.py"

        # Multiple input example command
        self.mult_input_command = "split_libraries_fastq.py -m mapping.txt"

        # Parameter example command
        self.parameter_command = "parallel_pick_otus_uclust_ref.py -r " + \
            "ref_file.fasta -i input_file.fna"

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

    def test_get_bench_params_single(self):
        """Tests get_bench_params parses a single line parameter file"""
        param_file = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.txt')
        pf = open(param_file, 'w')
        pf.write(parameters_file_1)
        pf.close()

        self._paths_to_clean_up = [param_file]
        
        obs = get_bench_params(param_file)
        exp = {'jobs_to_start' : [ '8', '16', '32', '64', '128', '256']}

        self.assertEqual(obs, exp)

    def test_get_bench_params_mult(self):
        """Tests get_bench_params parses a multiple line parameter file"""
        param_file = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.txt')
        pf = open(param_file, 'w')
        pf.write(parameters_file_2)
        pf.close()

        self._paths_to_clean_up = [param_file]
        
        obs = get_bench_params(param_file)
        exp = {'jobs_to_start' : [ '8', '16', '32', '64', '128', '256'],
            'similarity' : [ '0.70', '0.80', '0.90', '0.95', '0.97', '0.99']}

        self.assertEqual(obs, exp)

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

    def test_get_command_string_error(self):
        """Tests get_command_string raises an error if number of opts and files
            are different
        """
        self.assertRaises(ValueError, get_command_string,
            self.mult_input_command, ['-i', '-b'], ['seqs.fastq'], '-o',
            'output_dir', 'time_dir', 1)

    def test_write_commands_files_single(self):
        """Tests write_commands_files using a command with a single input"""
        # Create bench filess
        dir_name, files = self._create_bench_files_dir()
        base_out_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        base_time_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        pbs_fp = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.pbs')
        mkdir(base_out_dir)
        mkdir(base_time_dir)
        # Add clean up paths
        self._dirs_to_clean_up = [dir_name, base_out_dir, base_time_dir]
        self._paths_to_clean_up = [pbs_fp]
        # Call the function
        pbsf = open(pbs_fp, 'w')
        write_commands_files(self.single_input_command, ['-i'], [dir_name],
            '-o', base_out_dir, base_time_dir, pbsf, 3)
        pbsf.close()
        # Check written commands
        pbsf = open(pbs_fp, 'U')
        obs = pbsf.readlines()
        pbsf.close()
        exp = exp_commands_file_single % (base_time_dir, dir_name, base_out_dir,
                                        base_time_dir, dir_name, base_out_dir,
                                        base_time_dir, dir_name, base_out_dir,
                                        base_time_dir, dir_name, base_out_dir,
                                        base_time_dir, dir_name, base_out_dir,
                                        base_time_dir, dir_name, base_out_dir,
                                        base_time_dir, dir_name, base_out_dir,
                                        base_time_dir, dir_name, base_out_dir,
                                        base_time_dir, dir_name, base_out_dir)
        exp = exp.replace("\"","").splitlines(True)
        self.assertEqual(obs, exp)
        # Check output folders
        self.assertTrue(exists(join(base_out_dir, '1')))
        self.assertTrue(exists(join(base_out_dir, '2')))
        self.assertTrue(exists(join(base_out_dir, '3')))
        self.assertTrue(exists(join(base_time_dir, '1')))
        self.assertTrue(exists(join(base_time_dir, '2')))
        self.assertTrue(exists(join(base_time_dir, '3')))

    def test_write_commands_files_multiple(self):
        """Tests write_commands_files using a command with multiple inputs"""
        # Create bench files
        dir_names, files = self._create_bench_files_dir(multiple=True)
        base_out_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        base_time_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        pbs_fp = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.pbs')
        mkdir(base_out_dir)
        mkdir(base_time_dir)
        # Add clean up paths
        self._dirs_to_clean_up = [dir_names[0], dir_names[1], base_out_dir,
                                    base_time_dir]
        self._paths_to_clean_up = [pbs_fp]
        # Call the function
        pbsf = open(pbs_fp, 'w')
        write_commands_files(self.mult_input_command, ['-i', '-b'], dir_names,
            '-o', base_out_dir, base_time_dir, pbsf, 2)
        pbsf.close()
        # Check written commands
        pbsf = open(pbs_fp, 'U')
        obs = pbsf.readlines()
        pbsf.close()
        exp = exp_commands_file_mult % \
                    (base_time_dir, dir_names[0], dir_names[1], base_out_dir,
                    base_time_dir, dir_names[0], dir_names[1], base_out_dir,
                    base_time_dir, dir_names[0], dir_names[1], base_out_dir,
                    base_time_dir, dir_names[0], dir_names[1], base_out_dir,
                    base_time_dir, dir_names[0], dir_names[1], base_out_dir,
                    base_time_dir, dir_names[0], dir_names[1], base_out_dir)
        exp = exp.replace("\"","").splitlines(True)
        self.assertEqual(obs, exp)
        # Check output folders
        self.assertTrue(exists(join(base_out_dir, '1')))
        self.assertTrue(exists(join(base_out_dir, '2')))
        self.assertTrue(exists(join(base_out_dir, '3')))
        self.assertTrue(exists(join(base_time_dir, '1')))
        self.assertTrue(exists(join(base_time_dir, '2')))
        self.assertTrue(exists(join(base_time_dir, '3')))

    def test_write_commands_parameters_single(self):
        """Tests write_commands_parameters with a single parameter"""
        # Create parameters file
        parameters_fp = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.txt')
        pf = open(parameters_fp, 'w')
        pf.write(parameters_file_1)
        pf.close()
        base_out_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        base_time_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        pbs_fp = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.pbs')
        mkdir(base_out_dir)
        mkdir(base_time_dir)
        # Add clean up paths
        self._dirs_to_clean_up = [base_out_dir, base_time_dir]
        self._paths_to_clean_up = [parameters_fp, pbs_fp]
        # Call the function
        pbsf = open(pbs_fp, 'w')
        write_commands_parameters(self.parameter_command, parameters_fp, '-o',
            base_out_dir, base_time_dir, pbsf, 2)
        pbsf.close()
        # Check written commands
        pbsf = open(pbs_fp, 'U')
        obs = pbsf.readlines()
        pbsf.close()
        exp = exp_commands_param_single % (base_time_dir, base_out_dir,
                                            base_time_dir, base_out_dir,
                                            base_time_dir, base_out_dir,
                                            base_time_dir, base_out_dir,
                                            base_time_dir, base_out_dir,
                                            base_time_dir, base_out_dir,
                                            base_time_dir, base_out_dir,
                                            base_time_dir, base_out_dir,
                                            base_time_dir, base_out_dir,
                                            base_time_dir, base_out_dir,
                                            base_time_dir, base_out_dir,
                                            base_time_dir, base_out_dir)
        exp = exp.replace("\"","").splitlines(True)
        self.assertEqual(obs, exp)
        # Check output folders
        exp_param_out_dir = join(base_out_dir, 'jobs_to_start')
        self.assertTrue(exists(exp_param_out_dir))
        exp_param_time_dir = join(base_time_dir, 'jobs_to_start')
        self.assertTrue(exists(exp_param_time_dir))
        self.assertTrue(exists(join(exp_param_out_dir, '8')))
        self.assertTrue(exists(join(exp_param_out_dir, '16')))
        self.assertTrue(exists(join(exp_param_out_dir, '32')))
        self.assertTrue(exists(join(exp_param_out_dir, '64')))
        self.assertTrue(exists(join(exp_param_out_dir, '128')))
        self.assertTrue(exists(join(exp_param_out_dir, '256')))
        self.assertTrue(exists(join(exp_param_time_dir, '8')))
        self.assertTrue(exists(join(exp_param_time_dir, '16')))
        self.assertTrue(exists(join(exp_param_time_dir, '32')))
        self.assertTrue(exists(join(exp_param_time_dir, '64')))
        self.assertTrue(exists(join(exp_param_time_dir, '128')))
        self.assertTrue(exists(join(exp_param_time_dir, '256')))

    def test_write_commands_parameters_mult(self):
        """Tests write_commands_parameters with multiple parameters"""
        parameters_fp = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.txt')
        pf = open(parameters_fp, 'w')
        pf.write(parameters_file_2)
        pf.close()
        base_out_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        base_time_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        pbs_fp = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.pbs')
        mkdir(base_out_dir)
        mkdir(base_time_dir)
        # Add clean up paths
        self._dirs_to_clean_up = [base_out_dir, base_time_dir]
        self._paths_to_clean_up = [parameters_fp, pbs_fp]
        # Call the function
        pbsf = open(pbs_fp, 'w')
        write_commands_parameters(self.parameter_command, parameters_fp, '-o',
            base_out_dir, base_time_dir, pbsf, 2)
        pbsf.close()
        # Check written commands
        pbsf = open(pbs_fp, 'U')
        obs = pbsf.readlines()
        pbsf.close()
        exp = exp_commands_param_mult % (base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir,
                                        base_time_dir, base_out_dir)
        exp = exp.replace("\"","").splitlines(True)
        self.assertEqual(obs, exp)
        # Check output folders
        exp_param_out_dir = join(base_out_dir, 'jobs_to_start')
        self.assertTrue(exists(exp_param_out_dir))
        exp_param_time_dir = join(base_time_dir, 'jobs_to_start')
        self.assertTrue(exists(exp_param_time_dir))
        self.assertTrue(exists(join(exp_param_out_dir, '8')))
        self.assertTrue(exists(join(exp_param_out_dir, '16')))
        self.assertTrue(exists(join(exp_param_out_dir, '32')))
        self.assertTrue(exists(join(exp_param_out_dir, '64')))
        self.assertTrue(exists(join(exp_param_out_dir, '128')))
        self.assertTrue(exists(join(exp_param_out_dir, '256')))
        self.assertTrue(exists(join(exp_param_time_dir, '8')))
        self.assertTrue(exists(join(exp_param_time_dir, '16')))
        self.assertTrue(exists(join(exp_param_time_dir, '32')))
        self.assertTrue(exists(join(exp_param_time_dir, '64')))
        self.assertTrue(exists(join(exp_param_time_dir, '128')))
        self.assertTrue(exists(join(exp_param_time_dir, '256')))
        exp_param_out_dir = join(base_out_dir, 'similarity')
        self.assertTrue(exists(exp_param_out_dir))
        exp_param_time_dir = join(base_time_dir, 'similarity')
        self.assertTrue(exists(exp_param_time_dir))
        self.assertTrue(exists(join(exp_param_out_dir, '0.70')))
        self.assertTrue(exists(join(exp_param_out_dir, '0.80')))
        self.assertTrue(exists(join(exp_param_out_dir, '0.90')))
        self.assertTrue(exists(join(exp_param_out_dir, '0.95')))
        self.assertTrue(exists(join(exp_param_out_dir, '0.97')))
        self.assertTrue(exists(join(exp_param_out_dir, '0.99')))
        self.assertTrue(exists(join(exp_param_time_dir, '0.70')))
        self.assertTrue(exists(join(exp_param_time_dir, '0.80')))
        self.assertTrue(exists(join(exp_param_time_dir, '0.90')))
        self.assertTrue(exists(join(exp_param_time_dir, '0.95')))
        self.assertTrue(exists(join(exp_param_time_dir, '0.97')))
        self.assertTrue(exists(join(exp_param_time_dir, '0.99')))

    def test_make_pbs_files(self):
        """Tests make_pbs using a set of benchmark files"""
        # Create bench filess
        dir_name, files = self._create_bench_files_dir()
        output_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        pbs_fp = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.pbs')
        mkdir(output_dir)
        # Add clean up paths
        self._paths_to_clean_up = [pbs_fp]
        self._dirs_to_clean_up = [dir_name, output_dir]
        # Call the function
        make_pbs(self.single_input_command, ['-i'], [dir_name], None, '-o',
            output_dir, pbs_fp, 'Test', 3)
        # Check output directory structure
        exp_output_dir = join(output_dir, 'command_outputs')
        self.assertTrue(exists(exp_output_dir))
        exp_time_dir = join(output_dir, 'timing')
        self.assertTrue(exists(exp_time_dir))
        self.assertTrue(exists(pbs_fp))
        # Check output pbs file
        pbsf = open(pbs_fp, 'U')
        obs = pbsf.readlines()
        pbsf.close()
        exp = exp_make_pbs_files % (exp_time_dir, dir_name, exp_output_dir,
                                    exp_time_dir, dir_name, exp_output_dir,
                                    exp_time_dir, dir_name, exp_output_dir,
                                    exp_time_dir, dir_name, exp_output_dir,
                                    exp_time_dir, dir_name, exp_output_dir,
                                    exp_time_dir, dir_name, exp_output_dir,
                                    exp_time_dir, dir_name, exp_output_dir,
                                    exp_time_dir, dir_name, exp_output_dir,
                                    exp_time_dir, dir_name, exp_output_dir)
        exp = exp.replace("\"","").splitlines(True)
        self.assertEqual(obs, exp)

    def test_make_pbs_parameters(self):
        """Tests make_pbs using a benchmark parameter"""
        # Create parameters file
        parameters_fp = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.txt')
        pf = open(parameters_fp, 'w')
        pf.write(parameters_file_1)
        pf.close()
        output_dir = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='')
        pbs_fp = get_tmp_filename(tmp_dir=self.tmp_dir, suffix='.pbs')
        mkdir(output_dir)
        # Add clean up paths
        self._paths_to_clean_up = [pbs_fp]
        self._dirs_to_clean_up = [output_dir]
        # Call the function
        make_pbs(self.parameter_command, None, None, parameters_fp, '-o',
            output_dir, pbs_fp, "Test_par", 2)
        # Check output directory structure
        exp_output_dir = join(output_dir, 'command_outputs')
        self.assertTrue(exists(exp_output_dir))
        exp_time_dir = join(output_dir, 'timing')
        self.assertTrue(exists(exp_time_dir))
        self.assertTrue(exists(pbs_fp))
        # Check output pbs file
        pbsf = open(pbs_fp, 'U')
        obs = pbsf.readlines()
        pbsf.close()
        exp = exp_make_pbs_params % (exp_time_dir, exp_output_dir,
                                    exp_time_dir, exp_output_dir,
                                    exp_time_dir, exp_output_dir,
                                    exp_time_dir, exp_output_dir,
                                    exp_time_dir, exp_output_dir,
                                    exp_time_dir, exp_output_dir,
                                    exp_time_dir, exp_output_dir,
                                    exp_time_dir, exp_output_dir,
                                    exp_time_dir, exp_output_dir,
                                    exp_time_dir, exp_output_dir,
                                    exp_time_dir, exp_output_dir,
                                    exp_time_dir, exp_output_dir)
        exp = exp.replace("\"","").splitlines(True)
        self.assertEqual(obs, exp)


parameters_file_1 = """jobs_to_start\t8,16,32,64,128,256"""

parameters_file_2 = """jobs_to_start\t8,16,32,64,128,256
similarity\t0.70,0.80,0.90,0.95,0.97,0.99"""

exp_commands_file_single = """timing_wrapper.sh %s/1/0.txt pick_de_novo_otus.py  -i %s/1.txt -o %s/1/0
timing_wrapper.sh %s/1/1.txt pick_de_novo_otus.py  -i %s/1.txt -o %s/1/1
timing_wrapper.sh %s/1/2.txt pick_de_novo_otus.py  -i %s/1.txt -o %s/1/2
timing_wrapper.sh %s/2/0.txt pick_de_novo_otus.py  -i %s/2.txt -o %s/2/0
timing_wrapper.sh %s/2/1.txt pick_de_novo_otus.py  -i %s/2.txt -o %s/2/1
timing_wrapper.sh %s/2/2.txt pick_de_novo_otus.py  -i %s/2.txt -o %s/2/2
timing_wrapper.sh %s/3/0.txt pick_de_novo_otus.py  -i %s/3.txt -o %s/3/0
timing_wrapper.sh %s/3/1.txt pick_de_novo_otus.py  -i %s/3.txt -o %s/3/1
timing_wrapper.sh %s/3/2.txt pick_de_novo_otus.py  -i %s/3.txt -o %s/3/2
"""

exp_commands_file_mult = """timing_wrapper.sh %s/1/0.txt split_libraries_fastq.py -m mapping.txt  -i %s/1.txt -b %s/1.txt -o %s/1/0
timing_wrapper.sh %s/1/1.txt split_libraries_fastq.py -m mapping.txt  -i %s/1.txt -b %s/1.txt -o %s/1/1
timing_wrapper.sh %s/2/0.txt split_libraries_fastq.py -m mapping.txt  -i %s/2.txt -b %s/2.txt -o %s/2/0
timing_wrapper.sh %s/2/1.txt split_libraries_fastq.py -m mapping.txt  -i %s/2.txt -b %s/2.txt -o %s/2/1
timing_wrapper.sh %s/3/0.txt split_libraries_fastq.py -m mapping.txt  -i %s/3.txt -b %s/3.txt -o %s/3/0
timing_wrapper.sh %s/3/1.txt split_libraries_fastq.py -m mapping.txt  -i %s/3.txt -b %s/3.txt -o %s/3/1
"""

exp_commands_param_single = """timing_wrapper.sh %s/jobs_to_start/8/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 8 -o %s/jobs_to_start/8/0
timing_wrapper.sh %s/jobs_to_start/8/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 8 -o %s/jobs_to_start/8/1
timing_wrapper.sh %s/jobs_to_start/16/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 16 -o %s/jobs_to_start/16/0
timing_wrapper.sh %s/jobs_to_start/16/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 16 -o %s/jobs_to_start/16/1
timing_wrapper.sh %s/jobs_to_start/32/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 32 -o %s/jobs_to_start/32/0
timing_wrapper.sh %s/jobs_to_start/32/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 32 -o %s/jobs_to_start/32/1
timing_wrapper.sh %s/jobs_to_start/64/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 64 -o %s/jobs_to_start/64/0
timing_wrapper.sh %s/jobs_to_start/64/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 64 -o %s/jobs_to_start/64/1
timing_wrapper.sh %s/jobs_to_start/128/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 128 -o %s/jobs_to_start/128/0
timing_wrapper.sh %s/jobs_to_start/128/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 128 -o %s/jobs_to_start/128/1
timing_wrapper.sh %s/jobs_to_start/256/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 256 -o %s/jobs_to_start/256/0
timing_wrapper.sh %s/jobs_to_start/256/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 256 -o %s/jobs_to_start/256/1
"""

exp_commands_param_mult = """timing_wrapper.sh %s/jobs_to_start/8/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 8 -o %s/jobs_to_start/8/0
timing_wrapper.sh %s/jobs_to_start/8/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 8 -o %s/jobs_to_start/8/1
timing_wrapper.sh %s/jobs_to_start/16/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 16 -o %s/jobs_to_start/16/0
timing_wrapper.sh %s/jobs_to_start/16/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 16 -o %s/jobs_to_start/16/1
timing_wrapper.sh %s/jobs_to_start/32/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 32 -o %s/jobs_to_start/32/0
timing_wrapper.sh %s/jobs_to_start/32/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 32 -o %s/jobs_to_start/32/1
timing_wrapper.sh %s/jobs_to_start/64/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 64 -o %s/jobs_to_start/64/0
timing_wrapper.sh %s/jobs_to_start/64/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 64 -o %s/jobs_to_start/64/1
timing_wrapper.sh %s/jobs_to_start/128/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 128 -o %s/jobs_to_start/128/0
timing_wrapper.sh %s/jobs_to_start/128/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 128 -o %s/jobs_to_start/128/1
timing_wrapper.sh %s/jobs_to_start/256/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 256 -o %s/jobs_to_start/256/0
timing_wrapper.sh %s/jobs_to_start/256/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 256 -o %s/jobs_to_start/256/1
timing_wrapper.sh %s/similarity/0.70/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --similarity 0.70 -o %s/similarity/0.70/0
timing_wrapper.sh %s/similarity/0.70/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --similarity 0.70 -o %s/similarity/0.70/1
timing_wrapper.sh %s/similarity/0.80/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --similarity 0.80 -o %s/similarity/0.80/0
timing_wrapper.sh %s/similarity/0.80/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --similarity 0.80 -o %s/similarity/0.80/1
timing_wrapper.sh %s/similarity/0.90/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --similarity 0.90 -o %s/similarity/0.90/0
timing_wrapper.sh %s/similarity/0.90/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --similarity 0.90 -o %s/similarity/0.90/1
timing_wrapper.sh %s/similarity/0.95/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --similarity 0.95 -o %s/similarity/0.95/0
timing_wrapper.sh %s/similarity/0.95/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --similarity 0.95 -o %s/similarity/0.95/1
timing_wrapper.sh %s/similarity/0.97/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --similarity 0.97 -o %s/similarity/0.97/0
timing_wrapper.sh %s/similarity/0.97/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --similarity 0.97 -o %s/similarity/0.97/1
timing_wrapper.sh %s/similarity/0.99/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --similarity 0.99 -o %s/similarity/0.99/0
timing_wrapper.sh %s/similarity/0.99/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --similarity 0.99 -o %s/similarity/0.99/1
"""

exp_make_pbs_files = """#!/bin/bash
#PBS -q memroute
#PBS -l pvmem=512gb
#PBS -N Test
#PBS -k oe

# cd into the directory where 'qsub *.pbs' was run
cd $PBS_O_WORKDIR

# benchmarking commands:

timing_wrapper.sh %s/1/0.txt pick_de_novo_otus.py  -i %s/1.txt -o %s/1/0
timing_wrapper.sh %s/1/1.txt pick_de_novo_otus.py  -i %s/1.txt -o %s/1/1
timing_wrapper.sh %s/1/2.txt pick_de_novo_otus.py  -i %s/1.txt -o %s/1/2
timing_wrapper.sh %s/2/0.txt pick_de_novo_otus.py  -i %s/2.txt -o %s/2/0
timing_wrapper.sh %s/2/1.txt pick_de_novo_otus.py  -i %s/2.txt -o %s/2/1
timing_wrapper.sh %s/2/2.txt pick_de_novo_otus.py  -i %s/2.txt -o %s/2/2
timing_wrapper.sh %s/3/0.txt pick_de_novo_otus.py  -i %s/3.txt -o %s/3/0
timing_wrapper.sh %s/3/1.txt pick_de_novo_otus.py  -i %s/3.txt -o %s/3/1
timing_wrapper.sh %s/3/2.txt pick_de_novo_otus.py  -i %s/3.txt -o %s/3/2
"""

exp_make_pbs_params = """#!/bin/bash
#PBS -q memroute
#PBS -l pvmem=512gb
#PBS -N Test_par
#PBS -k oe

# cd into the directory where 'qsub *.pbs' was run
cd $PBS_O_WORKDIR

# benchmarking commands:

timing_wrapper.sh %s/jobs_to_start/8/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 8 -o %s/jobs_to_start/8/0
timing_wrapper.sh %s/jobs_to_start/8/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 8 -o %s/jobs_to_start/8/1
timing_wrapper.sh %s/jobs_to_start/16/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 16 -o %s/jobs_to_start/16/0
timing_wrapper.sh %s/jobs_to_start/16/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 16 -o %s/jobs_to_start/16/1
timing_wrapper.sh %s/jobs_to_start/32/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 32 -o %s/jobs_to_start/32/0
timing_wrapper.sh %s/jobs_to_start/32/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 32 -o %s/jobs_to_start/32/1
timing_wrapper.sh %s/jobs_to_start/64/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 64 -o %s/jobs_to_start/64/0
timing_wrapper.sh %s/jobs_to_start/64/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 64 -o %s/jobs_to_start/64/1
timing_wrapper.sh %s/jobs_to_start/128/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 128 -o %s/jobs_to_start/128/0
timing_wrapper.sh %s/jobs_to_start/128/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 128 -o %s/jobs_to_start/128/1
timing_wrapper.sh %s/jobs_to_start/256/0.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 256 -o %s/jobs_to_start/256/0
timing_wrapper.sh %s/jobs_to_start/256/1.txt parallel_pick_otus_uclust_ref.py -r ref_file.fasta -i input_file.fna  --jobs_to_start 256 -o %s/jobs_to_start/256/1
"""

if __name__ == '__main__':
    main()