#!/bin/bash
# Stop the Gift of Lights sender started by postStart.sh.
: "${FPPDIR:=/opt/fpp}"
. "${FPPDIR}/scripts/common"
PID_FILE="${MEDIADIR}/plugindata/fpp-plugin-GiftOfLights/sender.pid"
if [ -f "${PID_FILE}" ]; then
    kill "$(cat "${PID_FILE}")" 2>/dev/null || true
fi
exit 0
