#!/bin/sh

BASE_DIR="$(dirname -- "`readlink -f -- "$0"`")"

cd -- "$BASE_DIR"
set -e

if [ "$1" = "-cron" ]; then
    shift
    USERNAME=$(id -nu ${SEARXCHECKER_UID})
    chown -R $USERNAME html/data
    exec su-exec $USERNAME ./loop.sh $@
else
    python ./checker/checker.py $@
fi
