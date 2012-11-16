#!/bin/bash

# Check if the user has provided a command to execute
if [[ $# -eq 0 ]]; then
	echo "USAGE: timing_wrapper.sh command [command args]"
	exit 1
fi

# Get the command to execute
cmd=$1
# Get the arguments of the command
args=${@:2}

# Get the basename of the command (without the file extension)
basename=`basename $cmd | cut -d. -f1`

# Get a string with current date in the following format:
#  _YYYYMMDD_HHMMSS
cdate=`date +_%Y%m%d_%H%M%S`

# Create a file name for the output of the time command
#   format:  basename_YYYYMMDD_HHMMSS.txt
# Thus, this wrapper can be used multiple times over the same
#  command keeping all the outputs
filename=$basename$cdate".txt"

# Launch the command through "time"
#  The output format is:
#    %e : elapsed real time "wall time" in seconds
#    %U : total number of CPU seconds in user space
#    %S : total number of CPU seconds in kernel space
#    %M : maximum resident size pf the process, in KB
#
#    separated by ';'
#
#    %U + %S is the total time spent by the command in the CPU
#    %e includes also the time of I/O operations and the time
#         that the process has been not running due to scheduling
#
#  We use this output format because it is easy to parse
/usr/bin/time -o $filename -f"%e;%U;%S;%M" $cmd $args > /dev/null 2> /dev/null

# Check if the command cmd has finished correctly
#  If cmd has finished on success, the time output file will
#    have only one line with the stats
#  Otherwise, the time output file will have two lines:
#    one with 'Command exited with non-zero status X'
#    and the second one with the status
lines=`cat $filename | wc -l`
if [[ $lines -ne 1 ]]; then
	echo "The command has not finished correctly."
fi