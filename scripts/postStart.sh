#!/bin/bash
# Start the Gift of Lights sender (one copy). Returns at once: the sender runs in the background.
: "${FPPDIR:=/opt/fpp}"
. "${FPPDIR}/scripts/common"
PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA="${MEDIADIR}/plugindata/fpp-plugin-GiftOfLights"
mkdir -p "${DATA}/queue"
if [ -f "${DATA}/sender.pid" ] && kill -0 "$(cat "${DATA}/sender.pid")" 2>/dev/null; then
    exit 0
fi
MEDIADIR="${MEDIADIR}" CFGDIR="${CFGDIR}" LOGDIR="${LOGDIR}" \
    nohup /usr/bin/python3 "${PLUGIN_DIR}/gol_sender.py" >/dev/null 2>&1 &
exit 0
