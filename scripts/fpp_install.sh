#!/bin/bash
# Gift of Lights: nothing to build or fetch (Python standard library only). Safe to run again.
: "${FPPDIR:=/opt/fpp}"
. "${FPPDIR}/scripts/common"
mkdir -p "${MEDIADIR}/plugindata/fpp-plugin-GiftOfLights/queue"
chown -R fpp:fpp "${MEDIADIR}/plugindata/fpp-plugin-GiftOfLights" 2>/dev/null || true
# Start the sender now, so it runs without waiting for the next fppd restart (postStart.sh keeps it to one copy).
"$(cd "$(dirname "$0")" && pwd)/postStart.sh"
exit 0
