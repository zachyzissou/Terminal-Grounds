#!/usr/bin/env bash
PORT=${PORT:-7777}
QUERY=${QUERY:-27015}
CONFIG=${CONFIG:-ServerConfig/server.yaml}
EXE="$(dirname "$0")/../Build/LinuxServer/TerminalGroundsServer"
exec "$EXE" -log -unattended -Port=$PORT -QueryPort=$QUERY -Config=$CONFIG
