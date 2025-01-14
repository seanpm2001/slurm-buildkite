#!/bin/bash
#SBATCH --time=01:05:00
#SBATCH --job-name=buildkite

PATH="${BUILDKITE_PATH}/bin:$PATH"

# Modules loaded here work in buildkite, but it is best to load modules 
# within the agent once the cluster-specific script has been sourced

# queue and modules are used for the environment hook, the rest are unused
TAGS="jobid=${SLURM_JOB_ID},queue=${BUILDKITE_QUEUE}"
if [ $# -ge 2 ]; then
    TAGS="$TAGS,modules=$2"
fi

bin/buildkite-agent start \
  --name "$BUILDKITE_QUEUE-$1-%n" \
  --config "${BUILDKITE_PATH}/buildkite-agent.cfg" \
  --acquire-job "$1" \
  --tags "$TAGS"
