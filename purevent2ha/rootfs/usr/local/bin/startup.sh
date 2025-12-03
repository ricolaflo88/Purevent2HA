#!/bin/bash
set -e

# Configuration logging
export PYTHONUNBUFFERED=1

# Get config from addon config
CONFIG_PATH=/data/options.json

# Extract values
PORT=$(jq -r '.port' $CONFIG_PATH)
LOG_LEVEL=$(jq -r '.log_level' $CONFIG_PATH)
BAUDRATE=$(jq -r '.baudrate' $CONFIG_PATH)
TIMEOUT=$(jq -r '.timeout' $CONFIG_PATH)
MAX_RETRY=$(jq -r '.max_retry' $CONFIG_PATH)

# Export for Python
export PUREVENT_PORT="$PORT"
export PUREVENT_LOG_LEVEL="$LOG_LEVEL"
export PUREVENT_BAUDRATE="$BAUDRATE"
export PUREVENT_TIMEOUT="$TIMEOUT"
export PUREVENT_MAX_RETRY="$MAX_RETRY"

# Start the daemon
echo "Starting Purevent2HA daemon..."
exec python3 /app/purevent2ha_daemon.py
