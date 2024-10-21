#!/usr/bin/env python3
import datetime
import logging
import os
import re
import subprocess
import job_schedulers
from buildkite import all_started_builds, all_canceled_builds, BUILDKITE_PATH, BUILDKITE_QUEUE, BUILDKITE_API_TOKEN

from datetime import datetime, date, timedelta
from os.path import join as joinpath, isfile

# debug flag, set this to true to get log output
# of state change transitions but do not actually
# submit the slurm commands on the cluster

# If DEBUG_SLURM_BUILDKITE is set, we are in the Debug mode

# Time window to query buildkite jobs
NHOURS = 96

# setup root logger
logger = logging.Logger('poll')
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

try:
    exclude_nodes_path = joinpath(BUILDKITE_PATH, '.exclude_nodes')
    # Check if the file exists and read its content, otherwise fallback to an empty string
    if isfile(exclude_nodes_path):
        exclude_nodes_from_file = open(exclude_nodes_path, 'r').read().rstrip()
    else:
        exclude_nodes_from_file = ''

    # Get the value from environment variable, or fallback to the file content or an empty string
    BUILDKITE_EXCLUDE_NODES = os.environ.get('BUILDKITE_EXCLUDE_NODES', exclude_nodes_from_file)

    scheduler = job_schedulers.get_job_scheduler('slurm')
    current_jobs = scheduler.current_jobs(logger)
    # poll the buildkite API to check if there are any scheduled/running builds
    builds = all_started_builds(NHOURS)

    # Accumulate jobs to be canceled in one batch 
    jobs_to_cancel = []
    # loop over all scheduled and running builds for all pipelines in the buildkite org
    for build in builds:

        pipeline = build['pipeline']
        pipeline_name = pipeline['name']

        # for all jobs in this build
        for job in build['jobs']:

            # jobid, jobtype are attributes in every job object
            jobid, jobtype = job['id'], job['type']

            # don't schedule non-script jobs on slurm
            if jobtype != 'script':
                continue

            # this job is a script job, check if it has a scheduled state
            # and not submitted as slurm job
            # valid states: running, scheduled, passed, failed, blocked,
            #               canceled, canceling, skipped, not_run, finished
            # https://buildkite.com/docs/pipelines/defining-steps#build-states
            jobstate = job['state']
            buildkite_url = job['web_url']

            # Cancel jobs marked by buildkite as 'canceled'
            if jobstate == 'canceled':
                if buildkite_url in current_jobs:
                    jobs_to_cancel.extend(current_jobs[buildkite_url])
                else:
                    logger.warning(f"Canceled job {buildkite_url} not found in current jobs.")
                continue

            # jobstate is not pending, or a scheduled job (but not running yet)
            # is already submitted to slurm
            if jobstate != 'scheduled' or buildkite_url in current_jobs:
                continue

            # Directory containing slurm logs for given build
            log_dir = joinpath(
                BUILDKITE_PATH,
                'logs',
                f'{date.today()}',
                f"build_{build['id']}",
            )
            # Create the directory prefix if it does not exist
            if not os.path.isdir(log_dir):
                build_link = build_url((pipeline_name, build['number']))
                logger.info(f"New build: {pipeline_name} - {build_link}")
                os.mkdir(log_dir)
            
            # The comment section is used to scan jobids and ensure we are not
            # submitting multiple copies of the same job. This happens at the
            # beginning of the try-catch, in the squeue command.
            job_tags = get_buildkite_job_tags(job)
            queue = job_tags.get('queue', None)

            # Only log jobs on current queue unless debugging or missing queue
            if queue is None:
                logger.error(f"New job missing queue. Pipeline: {pipeline_name}, {buildkite_url}")
                continue
            elif queue == BUILDKITE_QUEUE:
                logger.info(f"New job on `{queue}`. Pipeline: {pipeline_name}, {buildkite_url}")
                scheduler.submit_job(queue, log_dir, job)

    # Cancel jobs in canceled builds
    canceled_builds = all_canceled_builds()

    for build in canceled_builds:
        for job in build['jobs']:
            if job['type'] == 'script':
                buildkite_url = job['web_url']
                if buildkite_url in current_jobs:
                    jobs_to_cancel.extend(current_jobs[buildkite_url])

    # Cancel individually marked slurm jobs in one call
    if jobs_to_cancel:
        scheduler.cancel_jobs(logger, jobs_to_cancel)

except Exception:
    logger.error("Caught exception during poll",  exc_info=True)
