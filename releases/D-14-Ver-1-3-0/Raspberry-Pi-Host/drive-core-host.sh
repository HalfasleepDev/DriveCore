# TODO: fix comments
#!/usr/bin/env bash
set -euo pipefail

VENV_NAME="env"
SCRIPT1="driveCoreHost.py"


DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_BIN="$DIR/$VENV_NAME/bin"
PYTHON="$VENV_BIN/python"

# Sanity checks
if [[ ! -x "$PYTHON" ]]; then
  echo "Error: $PYTHON not found or not executable. Did you create the venv at $VENV_BIN ?" >&2
  exit 1
fi
if [[ ! -f "$DIR/$SCRIPT1" ]]; then
  echo "Error: $DIR/$SCRIPT1 not found." >&2
  exit 1
fi

# Activate the venv and run
source "$VENV_BIN/activate"
echo "Running $SCRIPT1 in virtual environment: $VENV_NAME"

# Use the venv's python explicitly
"$PYTHON" "$DIR/$SCRIPT1"

# Deactivate when it exits
deactivate
