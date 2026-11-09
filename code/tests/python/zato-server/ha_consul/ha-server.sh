#!/bin/bash

# Copyright (C) 2026, Zato Source s.r.o. https://zato.io
# Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

# The command that the node runs while it is active. The scheduler runs in the background and the server replaces
# this shell in the foreground, both in the process group that the node stops when it ceases to be active.

set -euo pipefail

"${Zato_Test_Scheduler_Binary}" >> "${Zato_Test_Scheduler_Log}" 2>&1 &

exec "${Zato_Test_Zato_Binary}" "$@"
