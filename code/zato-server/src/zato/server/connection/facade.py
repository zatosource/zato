# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
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
    from requests import Response
    from zato.common.typing_ import any_, callnone
    from zato.server.base.parallel import ParallelServer
    from zato.server.config import ConfigDict
    from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper
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

        # .. check if we shouldn't go further to extract the actual response ..
        if not 'id' in response:
            response = response['zato_scheduler_job_create_response']

        # .. and return its ID to the caller.
        return response['id'] # type: ignore

# ################################################################################################################################
# ################################################################################################################################

class RESTFacade:
    """ A facade through which self.rest calls can be made.
    """
    cid: 'str'
    _out_plain_http: 'ConfigDict'

    name_prefix: 'str' = ''
    needs_facade: 'bool' = True
    has_path_in_args: 'bool' = False

    before_call_func: 'callnone' = None
    after_call_func:  'callnone' = None

    def init(self, cid:'str', _out_plain_http:'ConfigDict') -> 'None':
        self.cid = cid
        self._out_plain_http = _out_plain_http

# ################################################################################################################################

    def _get(self, orig_name:'str', needs_prefix:'bool'=True) -> 'RESTInvoker':

        # Check if name may point to an environment variable ..
        if orig_name.startswith('$'):
            env_name = orig_name.replace('$', '', 1)
            name = os.environ[env_name]

        # .. otherwise, use it as is.
        else:
            name = orig_name

        # Use a potential prefix
        if needs_prefix:
            name = self.name_prefix + name

        # This will raise a KeyError if we have no such name ..
        item = self._out_plain_http[name]

        # .. now, we can return our own facade.
        invoker = RESTInvoker(item.conn, self)
        return invoker

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'RESTInvoker':
        result = self._get(name)
        return result

# ################################################################################################################################

    def __getattr__(self, attr_name:'str') -> 'RESTInvoker':

        # Use a potential prefix
        attr_name = self.name_prefix + attr_name

        try:
            # First, try and see if we do not have a connection of that exact name ..
            conn = self._get(attr_name, needs_prefix=False)
        except KeyError:
            # .. this is fine, there was no such connection
            pass
        else:
            # .. if there was, we can return it here ..
            return conn

        # .. otherwise, go through of the connections and check their filesystem-safe names ..
        for config in self._out_plain_http.get_config_list():
            if config['name_fs_safe'] == attr_name:
                name = config['name']
                break
        else:
            raise KeyError(f'No such connection `{attr_name}`')

        # If we are here, it means that we must have found the correct name
        return self._get(name, needs_prefix=False)

# ################################################################################################################################
# ################################################################################################################################

class RESTInvoker:
    conn: 'HTTPSOAPWrapper'
    container: 'RESTFacade'

    def __init__(self, conn:'HTTPSOAPWrapper', container:'RESTFacade') -> 'None':
        self.conn = conn
        self.container = container

# ################################################################################################################################

    def call_rest_func(self, func_name:'str', conn_name:'str', *args:'any_', **kwargs:'str') -> 'any_':

        # .. the actual method to invoke ..
        func = getattr(self.conn, func_name)

        # .. if we have a function to call before the actual method should be invoked, do it now ..
        if self.container.before_call_func:
            self.container.before_call_func(func_name, conn_name, self.conn, *args, **kwargs)

        # .. do invoke the actual function ..
        result = func(self.container.cid, *args, **kwargs)

        # .. if we have a function to call after the actual method was invoked, do it now ..
        if self.container.after_call_func:
            self.container.after_call_func(func_name, conn_name, self.conn, result, *args, **kwargs)

        # .. and return the result to our caller.
        return result

# ################################################################################################################################

    def call_wrapper(self, *args:'any_', **kwargs:'any_') -> 'any_':

        # This will be always the same
        conn_name = self.conn.config['name']
        func_name = args[0]
        args = args[1:]

        # If this is a pre-facade REST call, we do not need the CID in here
        if args:
            if args[0] == self.container.cid:
                args = args[1:]

        # Depending on what kind of an invoker this is, build the path that we actually want to access.
        if self.container.has_path_in_args:
            if args:
                _zato_path = args[0]
                args = args[1:]
            else:
                _zato_path = '/zato-no-path-given'

            # We know we will be always able to populate this key with some value
            kwargs_params = kwargs.setdefault('params', {})
            kwargs_params['_zato_path'] = _zato_path

        return self.call_rest_func(func_name, conn_name, *args, **kwargs)

# ################################################################################################################################

    def get(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('get', *args, **kwargs)

    def delete(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('delete', *args, **kwargs)

    def options(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('options', *args, **kwargs)

    def post(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('post', *args, **kwargs)

    send = post

    def put(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('put', *args, **kwargs)

    def patch(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('patch', *args, **kwargs)

    def ping(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('ping', *args, **kwargs)

    def upload(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('upload', *args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

class KeysightVisionFacade(RESTFacade):
    name_prefix = 'KeysightVision.'
    has_path_in_args = True

# ################################################################################################################################
# ################################################################################################################################

class KeysightHawkeyeFacade(RESTFacade):
    name_prefix = 'KeysightHawkeye.'
    has_path_in_args = True

# ################################################################################################################################

    def before_call_func(
        self,
        func_name, # type: str
        conn_name, # type: str
        conn,      # type: HTTPSOAPWrapper
        *args,     # type: any_
        **kwargs,  # type: str
    ) -> 'any_':
        pass

# ################################################################################################################################

    def after_call_func(
        self,
        func_name, # type: str
        conn_name, # type: str
        conn,      # type: HTTPSOAPWrapper
        result,    # type: Response
        *args,     # type: any_
        **kwargs,  # type: str
    ) -> 'any_':
        pass

# ################################################################################################################################
# ################################################################################################################################

class KeysightContainer:
    vision:  'KeysightVisionFacade'
    hawkeye: 'KeysightHawkeyeFacade'

    def init(self, cid:'str', _out_plain_http:'ConfigDict') -> 'None':

        self.vision = KeysightVisionFacade()
        self.vision.init(cid, _out_plain_http)

        self.hawkeye = KeysightHawkeyeFacade()
        self.hawkeye.init(cid, _out_plain_http)

# ################################################################################################################################
# ################################################################################################################################
