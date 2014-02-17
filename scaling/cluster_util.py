#!/usr/bin/env python

__author__ = "Jose Antonio Navas Molina"
__copyright__ = "Copyright 2014, The QIIME-Scaling Project"
__credits__ = ["Jose Antonio Navas Molina", "Daniel McDonald"]
__license__ = "BSD"
__version__ = "0.0.1-dev"
__maintainer__ = "Jose Antonio Navas Molina"
__email__ = "josenavasmolina@gmail.com"
__status__ = "Development"

from subprocess import Popen
from os import environ
from time import sleep


def check_status(jobs_to_monitor):
    """Check the status of the passed list of jobs

    Inputs:
        jobs_to_monitor: list of job ids

    Returns:
        A subset of jobs_to_monitor containing those jobs that are still
            running
    """
    # Get all the commands running pf the current user
    user = environ['USER']
    qstat_cmd = "qstat | grep %s" % user
    proc = Popen(qstat_cmd, stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE, shell=True)
    (stdout, stderr) = proc.communicate()
    # Parse the qstat output
    lines = stdout.splitlines()
    running_jobs = []
    for l in lines:
        job_id, job_name, user, time, status, queue = l.split()
        job_id = job_id.split('.')[0]
        # Check if this job is one of the jobs that we have to
        # monitor and check if it is running or queued
        if job_id in jobs_to_monitor and status in ['R', 'Q']:
            running_jobs.append(job_id)
    # Return the list with the running jobs that we're still waiting for
    return running_jobs


def wait_on(jobs_to_monitor, poll_interval=5):
    """Block while jobs to monitor are running

    Inputs:
        jobs_to_monitor: list of job ids
        poll_interval: interval between checks, in seconds
    """
    # Get the jobs ids by up to the first '.' character
    jobs_to_monitor = [job.split('.')[0] for job in jobs_to_monitor]
    # Loop until there is some job to monitor
    while jobs_to_monitor:
        # Sleep before new job status check
        sleep(poll_interval)
        # Check job status and get new set of jobs to wait on
        jobs_to_monitor = check_status(jobs_to_monitor)
