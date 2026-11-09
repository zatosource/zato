#!/bin/bash

# Copyright (C) 2026, Zato Source s.r.o. https://zato.io
# Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

# Starts one node of an active-standby pair in a container of the published Zato image. Redis serves this node only,
# and the node starts the Zato server whenever it becomes active and stops it whenever it ceases to be.

set -euo pipefail

redis-server --daemonize yes --dir /tmp --save '' --appendonly no --bind 127.0.0.1 --port 6379

exec "${Zato_Test_HA_Node_Binary}" -- "${Zato_Test_Zato_Binary}" start "${Zato_Test_Server_Directory}" --fg
