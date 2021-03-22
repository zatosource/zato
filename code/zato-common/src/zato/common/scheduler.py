# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

startup_jobs="""[zato.stats.process-raw-times]
seconds=90
service=zato.stats.process-raw-times
extra=max_batch_size=99999

[zato.stats.aggregate-by-minute]
seconds=60
service=zato.stats.aggregate-by-minute

[zato.stats.aggregate-by-hour]
minutes=10
service=zato.stats.aggregate-by-hour

[zato.stats.aggregate-by-day]
minutes=60
service=zato.stats.aggregate-by-day

[zato.stats.aggregate-by-month]
minutes=60
service=zato.stats.aggregate-by-month

[zato.stats.summary.create-summary-by-day]
minutes=10
service=zato.stats.summary.create-summary-by-day

[zato.stats.summary.create-summary-by-week]
minutes=10
service=zato.stats.summary.create-summary-by-week

[zato.stats.summary.create-summary-by-month]
minutes=60
service=zato.stats.summary.create-summary-by-month

[zato.stats.summary.create-summary-by-year]
minutes=60
service=zato.stats.summary.create-summary-by-year

[zato.outgoing.sql.auto-ping]
minutes=3
service=zato.outgoing.sql.auto-ping

[zato.wsx.cleanup.pub-sub]
minutes=30
service=pub.zato.channel.web-socket.cleanup-wsx-pub-sub
extra=
is_extra_list=True

[zato.wsx.cleanup]
minutes=30
service=pub.zato.channel.web-socket.cleanup-wsx

[zato.pubsub.cleanup]
minutes=5
service=zato.pubsub.cleanup-service
extra=
"""

# ################################################################################################################################
# ################################################################################################################################

def get_startup_job_services():
    # type: () -> list
    from zato.common.util.api import get_config_from_string

    config = get_config_from_string(startup_jobs)
    return sorted(value.service for value in config.values())

# ################################################################################################################################
# ################################################################################################################################
