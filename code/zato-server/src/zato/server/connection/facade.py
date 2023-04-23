# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# Arrow
from arrow import Arrow

# datetutil
from dateutil.parser import parse as dt_parse
from dateutil.tz.tz import tzutc

# Zato
from zato.common.api import SCHEDULER
from zato.common.json_internal import dumps

################################################################################################################################
################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.server.base.parallel import ParallelServer
    from zato.server.service import Service

################################################################################################################################
################################################################################################################################

_utz_utc = timezone.utc

################################################################################################################################
################################################################################################################################

class SchedulerFacade:
    """ The API through which jobs can be scheduled.
    """
    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server

################################################################################################################################

    def onetime(
        self,
        invoking_service, # type: Service
        target_service,   # type: any_
        name='',          # type: str
        *,
        prefix='',        # type: str
        start_date='',    # type: any_
        after_seconds=0,  # type: int
        after_minutes=0,  # type: int
        data=''           # type: any_
        ) -> 'int':
        """ Schedules a service to run at a specific date and time or aftern N minutes or seconds.
        """

        # This is reusable
        now = self.server.time_util.utcnow(needs_format=False)

        # We are given a start date on input ..
        if start_date:
            if not isinstance(start_date, datetime):

                # This gives us a datetime object but we need to ensure
                # that it is in UTC because this what the scheduler expects.
                start_date = dt_parse(start_date)

                if not isinstance(start_date.tzinfo, tzutc):
                    _as_arrow = Arrow.fromdatetime(start_date)
                    start_date = _as_arrow.to(_utz_utc)

        # .. or we need to compute one ourselves.
        else:
            start_date = now + timedelta(seconds=after_seconds, minutes=after_minutes)

        # This is the service that is scheduling a job ..
        invoking_name = invoking_service.get_name()

        # .. and this is the service that is being scheduled.
        target_name   = target_service if isinstance(target_service, str) else target_service.get_name()

        # Construct a name for the job
        name = name or '{}{} -> {} {} {}'.format(
            '{} '.format(prefix) if prefix else '',
            invoking_name,
            target_name,
            now.isoformat(),
            invoking_service.cid,
        )

        # This is what the service being invoked will receive on input
        if data:
            data = dumps({
                SCHEDULER.EmbeddedIndicator: True,
                'data': data
            })

        # Now, we are ready to create a new job ..
        response = self.server.invoke(
            'zato.scheduler.job.create', {
                'cluster_id': self.server.cluster_id,
                'name': name,
                'is_active': True,
                'job_type': SCHEDULER.JOB_TYPE.ONE_TIME,
                'service': target_name,
                'start_date': start_date,
                'extra': data
            }
        )

        # .. and return its ID to the caller.
        return response['id'] # type: ignore

################################################################################################################################
################################################################################################################################
