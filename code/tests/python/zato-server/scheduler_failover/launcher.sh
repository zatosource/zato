#!/bin/sh

# Copyright (C) 2026, Zato Source s.r.o. https://zato.io
# Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

# The scheduler of the server runs in the background and the server replaces this shell in the foreground,
# so stopping, killing or pausing the container acts on both of them.

"$Zato_Test_Scheduler_Binary" >> "$Zato_Test_Scheduler_Log" 2>&1 &

exec "$Zato_Test_Zato_Binary" "$@"
