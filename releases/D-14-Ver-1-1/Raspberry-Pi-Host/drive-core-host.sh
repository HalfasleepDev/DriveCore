#!/bin/bash

VENV_NAME="env"
PYTHON_VERSION="python3"

SCRIPT1="driveCoreHost.py"
SCRIPT2="webStream.py"

# Get the absolute path of the current directory
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the virtual environment
source "$DIR/$VENV_NAME/bin/activate"

echo "Running $SCRIPT1 and $SCRIPT2 in virtual environment: $VENV_NAME"

# Run both scripts in parallel and store PIDs
(
    $PYTHON_VERSION "$DIR/$SCRIPT1" & PID1=$!
    $PYTHON_VERSION "$DIR/$SCRIPT2" & PID2=$!

    # Wait for either script to finish
    wait -n $PID1 $PID2

    # If driveCoreHost.py exits first, stop Flask
    if ps -p $PID2 > /dev/null; then
        echo "Stopping Flask WebStream..."
        kill $PID2 2>/dev/null
        wait $PID2
    fi

    # If Flask exits first, stop driveCoreHost.py
    if ps -p $PID1 > /dev/null; then
        echo "Stopping driveCoreHost..."
        kill $PID1 2>/dev/null
        wait $PID1
    fi
) 

echo "Both scripts have finished execution."

# Deactivate virtual environment
deactivate
