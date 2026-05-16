#!/bin/bash
# Mac launcher. Double-click to start the web UI.
cd "$(dirname "$0")"

echo "Starting Check Splitter on http://127.0.0.1:8000 ..."
echo
echo "Leave this window open while using the tool."
echo "Close this window (or press Ctrl-C) to stop the server."
echo

# Open the browser after the server has a moment to bind
( sleep 2 && open "http://127.0.0.1:8000" ) &

python3 server.py
status=$?
if [ $status -ne 0 ]; then
    echo
    echo "[!] Server stopped with an error. If this is your first run,"
    echo "    double-click setup.command first."
    read -n 1 -s -r -p "Press any key to close..."
fi
