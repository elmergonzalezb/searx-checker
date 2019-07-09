#!/bin/sh
# Call every day the checker
while true
do
    BEFORE=$(date -u +%s)

    # Random delay
    DELAY=$(( RANDOM % 60 + 60 ))
    echo "Sleep $DELAY seconds"
    sleep $DELAY

    # Actual checking
    echo "$(date +"%Y/%m/%d %H:%M:%S") Check with the parameters : $@"
    python ./checker/checker.py $@

    # Wait 1 day
    AFTER=$(date -u +%s)
    DELAY=$(( 86400 - $AFTER + $BEFORE ))
    echo "Sleep $DELAY seconds"
    sleep $DELAY
done
