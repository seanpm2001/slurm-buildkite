#!/bin/bash
touch /glade/campaign/univ/ucit0011/slurm-buildkite/working

case "$(hostname)" in
    "login3.cm.cluster"|"login4.cm.cluster")
        export BUILDKITE_PATH="/central/groups/esm/slurm-buildkite"
        export BUILDKITE_QUEUE='new-central'
        ;;
    "clima.gps.caltech.edu")
        export BUILDKITE_PATH="/clima/slurm-buildkite"
        export BUILDKITE_QUEUE='clima'
        ;;
    derecho[0-7]|"cron")
        export BUILDKITE_PATH="/glade/campaign/univ/ucit0011/slurm-buildkite"
        export BUILDKITE_QUEUE='derecho'
        ;;
    *)
        echo "Invalid hostname found, exiting..."
        exit 1
        ;;
esac

case "$(hostname)" in
    derecho[0-7]|"cron")
        source /etc/bash.bashrc
        ;;
    *)
        source /etc/bashrc
        ;;
esac


cd $BUILDKITE_PATH

DATE="$(date +\%Y-\%m-\%d)"
mkdir -p "logs/$DATE"

bin/poll.py &>> "logs/$DATE/cron"
