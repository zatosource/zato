# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

"""A module for classes which don't really need a Django-backed database
yet it's useful to treat them sometimes like if they did.
"""

# Zato
from zato.common.util import make_repr

class SQLConnectionPool(object):
    def __init__(self, temp_id, original_pool_name, pool_name, engine,
                 engine_friendly, user, host, db_name, pool_size, extra):
        self.original_pool_name = original_pool_name
        self.temp_id = temp_id
        self.pool_name = pool_name
        self.engine = engine
        self.engine_friendly = engine_friendly
        self.user = user
        self.host = host
        self.db_name = db_name
        self.pool_size = pool_size
        self.extra = extra

    def __repr__(self):
        return make_repr(self)

class _SchedulerJob(object):
    def __init__(self, temp_id, original_job_name, job_name, job_type,
                 job_type_friendly, service, extra):
        self.temp_id = temp_id
        self.original_job_name = original_job_name
        self.job_name = job_name
        self.job_type = job_type
        self.job_type_friendly = job_type_friendly
        self.service = service
        self.extra = extra

    def __repr__(self):
        return make_repr(self)

class OneTimeSchedulerJob(_SchedulerJob):
    def __init__(self, temp_id=None, original_job_name=None, job_name=None,
                 job_type=None, job_type_friendly=None, service=None, extra=None,
                 date_time=None, date_time_raw=None):

        super(OneTimeSchedulerJob, self).__init__(temp_id, original_job_name,
                job_name, job_type, job_type_friendly, service, extra)

        self.date_time = date_time
        self.date_time_raw = date_time_raw
        self.definition = self.get_definition() # Prepare an initial definition.

    def __repr__(self):
        return make_repr(self)

    def get_definition(self):
        return "Execute once on %s, at %s." % (self.date_time.strftime("%Y-%m-%d"),
                    self.date_time.strftime("%H:%M:%S"))


class IntervalBasedSchedulerJob(_SchedulerJob):
    def __init__(self, temp_id=None, original_job_name=None, job_name=None,
                 job_type=None, job_type_friendly=None, service=None, extra=None,
                 start_date=None, start_date_raw=None, weeks=None, days=None,
                 hours=None, minutes=None, seconds=None, repeat=None, definition=None):

        super(IntervalBasedSchedulerJob, self).__init__(temp_id, original_job_name,
                job_name, job_type, job_type_friendly, service, extra)

        self.start_date = start_date
        self.start_date_raw = start_date_raw
        self.weeks = weeks
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.repeat = repeat
        self.definition = definition # We already have definition.

    def __repr__(self):
        return make_repr(self)

class Service(object):
    def __init__(self, name=None, egg_path=None, usage_count=None):
        self.name = name
        self.egg_path = egg_path
        self.usage_count = usage_count

    def __repr__(self):
        return make_repr(self)

    def __cmp__(self, other):
        return cmp(self.name, other.name)

class WSSUsernameTokenDefinition(object):
    def __init__(self, id=None, name=None, original_name=None, username=None, reject_empty_nonce_ts=None,
                 reject_stale_username=None, expiry_limit=None, nonce_freshness=None):
        self.id = id
        self.name = name
        self.original_name = original_name
        self.username = username
        self.reject_empty_nonce_ts = reject_empty_nonce_ts
        self.reject_stale_username = reject_stale_username
        self.expiry_limit = expiry_limit
        self.nonce_freshness = nonce_freshness

    def __repr__(self):
        return make_repr(self)

    def __cmp__(self, other):
        return cmp(self.name, other.name)

class LoadBalancer(object):
    def __init__(self, host=None, agent_port=None, ssl_certs_port=None, ssl_no_certs_port=None,
                 http_health_host=None, http_health_port=None, http_health_path=None,
                 tcp_ip_health_host=None, tcp_ip_health_port=None):
        self.host = host
        self.agent_port = agent_port
        self.ssl_certs_port = ssl_certs_port
        self.ssl_no_certs_port = ssl_no_certs_port
        self.http_health_host = http_health_host
        self.http_health_port = http_health_port
        self.http_health_path = http_health_path
        self.tcp_ip_health_host = tcp_ip_health_host
        self.tcp_ip_health_port = tcp_ip_health_port

    def __repr__(self):
        return make_repr(self)