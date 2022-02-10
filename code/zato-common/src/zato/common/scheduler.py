# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import SCHEDULER

# ################################################################################################################################
# ################################################################################################################################

pubsub_cleanup_job = SCHEDULER.PubSubCleanupJob

# ################################################################################################################################
# ################################################################################################################################

startup_jobs=f"""
[zato.outgoing.sql.auto-ping]
minutes=3
service=zato.outgoing.sql.auto-ping

[zato.wsx.cleanup]
minutes=30
service=pub.zato.channel.web-socket.cleanup-wsx

[{pubsub_cleanup_job}]
minutes=60
service=zato.pubsub.cleanup-service
extra=
""".lstrip()

# ################################################################################################################################
# ################################################################################################################################

def get_startup_job_services():
    # type: () -> list
    from zato.common.util.api import get_config_from_string

    config = get_config_from_string(startup_jobs)
    return sorted(value.service for value in config.values())

# ################################################################################################################################
# ################################################################################################################################
