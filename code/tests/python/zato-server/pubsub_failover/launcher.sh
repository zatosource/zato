#!/bin/sh

# Copyright (C) 2026, Zato Source s.r.o. https://zato.io
# Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

# The first process of a server container. The server runs in the background and the signal that docker stop sends
# is passed to every process of the container, so the server stops when the signal arrives
# rather than when the stop timeout elapses.

shutdown() {
    kill -TERM -1 2>/dev/null
    wait
    exit 0
}

trap shutdown INT TERM

"$Zato_Test_Zato_Binary" "$@" &
server_pid=$!

# The container ends when the server ends.
wait "$server_pid"
