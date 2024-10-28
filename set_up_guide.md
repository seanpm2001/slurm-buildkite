## Slurm-Buildkite Set Up Guide

This guide is based off of Buildkite's [Linux agent setup guide.](https://buildkite.com/docs/agent/v3/linux) . Review it for more information on Buildkite agents.

Clone slurm-buildkite and `cd` into the repository.

Either use an existing personal token or create one [here](https://buildkite.com/user/api-access-tokens/new). Copy this token into a new file `.buildkite_token`.

Use this token to install the Buildkite agent:
```
TOKEN=.buildkite_token bash -c "`curl -sL https://raw.githubusercontent.com/buildkite/agent/main/install.sh`
```

From the buildkite-agent install directory (probably `~/.buildkite_agent`), copy over:
- `bin/buildkite-agent`
	- `cp ~/.buildkite_agent/bin/buildkite-agent bin`
- `buildkite-agent.cfg`
	- `cp ~/.buildkite_agent/buildkite-agent.cfg .

Set up `buildkite-agent.cfg`:
1. Set the agent token. This is ideally done by creating a new token on [Buildkite](https://buildkite.com/docs/agent/v3/tokens#create-a-token).
2. Set `hooks-path="$BUILDKITE_PATH/hooks"` 
3. Set `plugins-path="$BUILDKITE_PATH/plugins"`
4. Set `build-path` to your slurm-buildkite folder
5. It may be useful to set `no-plugins=true` and `no-color=true`

There are several other files to add to:
- `bin/cron.sh`: Add a case entry for the hostname that sets `BUILDKITE_PATH`, `BUILDKITE_QUEUE`. Check if an exception is needed for `source /etc/bashrc`.
- `bin/job_schedulers.py`: Add entries to `DEFAULT_PARTITIONS`, `DEFAULT_GPU_PARTITIONS`, `DEFAULT_RESERVATIONS`
- `hooks/environment`: Add an entry  in the `case "$BUILDKITE_AGENT_META_DATA_QUEUE"`  statement with your `BUILDKITE_QUEUE`, creating a TMPDIR on all job nodes. If this requires a lot of code, you can tuck it away by `source`-ing a file in `cluster_environments`.
- `hooks/pre-exit`: Remove the previously created TMPDIRs. This can either be done with  `pdsh`, `srun` (with Slurm), or `pbsdsh` (with PBS).

Optional:
- `hooks/pre-command`:  Ensure that output folders have proper permissions

You can test this setup by setting the `BUILDKITE_QUEUE` to `test` and running the cronjob `bin/cron.sh`. 

Logs from the cron job will be written to `logs/YYYY-MM-DD/cron`. 

Once you have tested the system manually, you can use cron to run the polling script every minute:
On the proper node, run `crontab -e` to pull up your cron jobs.
On a new line, add `*/1 * * * * /bin/bash -l path/to/bin/cron.sh`. Be aware that a cron job will not have many of the typical startup environment variables.
If this does not work, you can debug by adding ` >> cron.log 2>&1` to the end of the line or by running the script manually. We have not tested concurrent database access and undefined behavior may occur if you run it concurrently.