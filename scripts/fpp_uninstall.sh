#!/bin/bash
# Gift of Lights: stop the sender and remove the plugin's own data and settings. Safe to run again.
: "${FPPDIR:=/opt/fpp}"
. "${FPPDIR}/scripts/common"
DATA="${MEDIADIR}/plugindata/fpp-plugin-GiftOfLights"
if [ -f "${DATA}/sender.pid" ]; then
    kill "$(cat "${DATA}/sender.pid")" 2>/dev/null || true
fi
[ -e "${DATA}" ] && rm -rf "${DATA}"
rm -f "${CFGDIR}/plugin.fpp-plugin-GiftOfLights"
exit 0
