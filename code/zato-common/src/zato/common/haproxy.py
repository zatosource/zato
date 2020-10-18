# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from tempfile import NamedTemporaryFile
from traceback import format_exc

# Zato
from zato.common.util.api import make_repr, timeouting_popen

logger = getLogger(__name__)

# We'll wait up to that many seconds for HAProxy to validate the config file.
HAPROXY_VALIDATE_TIMEOUT = 0.6

# Statistics commands understood by HAproxy 1.3.x and newer. Note that the
# command numbers must be consecutively increasing across HAProxy versions.
haproxy_stats = {
    ("1", "3"): {

        # A special command interpreted by the agent as a request for
        # describing the commands available
        0: ("ZATO_DESCRIBE_COMMANDS", "Describe commands"),

        1: ("show info", "Show info"),
        2: ("show stat", "Show stats"),
        3: ("show errors", "Show errors"),
        4: ("show sess", "Show sessions"),
    },
    ("1", "4"): {
    }
}

# timeout_id -> name, value in milliseconds
timeouts = {
    1: (250, "250ms"),
    2: (500, "500ms"),
    3: (1000, "1s"),
    4: (3000, "3s"),
    5: (5000, "10s"),
    6: (30000, "30s")
}

http_log = {
    1: ("nolog", "No log"),
    2: ("httplog", "HTTP log"),
}

tcp_log = {
    1: ("nolog", "No log"),
    2: ("tcplog", "TCP log"),
}

reversed_http_log = dict((v[0],k) for k,v in http_log.items())
reversed_tcp_log = dict((v[0],k) for k,v in tcp_log.items())

class Config(object):
    """ An object for representing a HAProxy configuration file.
    """
    def __init__(self):
        self.global_ = {}
        self.defaults = {}
        self.backend = {'bck_http_plain': {}}
        self.frontend = {"front_http_plain": {}}

    def __repr__(self):
        return make_repr(self)

    def set_value(self, name, data):
        if name == 'global:log':
            host, port, facility, level = data
            self.global_['log'] = {}
            self.global_['log']['host'] = host
            self.global_['log']['port'] = port
            self.global_['log']['facility'] = facility
            self.global_['log']['level'] = level
        elif name == 'global:stats_socket':
            stats_socket = data[0]
            self.global_['stats_socket'] = stats_socket
        elif name == 'defaults:timeout connect':
            timeout = data[0]
            self.defaults['timeout_connect'] = timeout
        elif name == 'defaults:timeout client':
            timeout = data[0]
            self.defaults['timeout_client'] = timeout
        elif name == 'defaults:timeout server':
            timeout = data[0]
            self.defaults['timeout_server'] = timeout
        elif name == 'defaults:stats uri':
            stats_uri = data[0]
            self.defaults['stats_uri'] = stats_uri
        elif name.startswith('backend bck_http_plain:server'):
            backend_name, address, port, extra = data
            extra = extra.strip()
            backend_name = backend_name.split('http_plain--')[1]
            self.backend['bck_http_plain'][backend_name] = {}
            self.backend['bck_http_plain'][backend_name]['address'] = address
            self.backend['bck_http_plain'][backend_name]['port'] = port
            self.backend['bck_http_plain'][backend_name]['extra'] = extra
        elif name == 'backend bck_http_plain:option httpchk':
            method, path = data
            self.backend['bck_http_plain']['option_httpchk'] = {}
            self.backend['bck_http_plain']['option_httpchk']['method'] = method
            self.backend['bck_http_plain']['option_httpchk']['path'] = path
        elif name == 'frontend front_http_plain:monitor-uri':
            path = data[0]
            self.frontend['front_http_plain']['monitor_uri'] = path
        elif name == 'frontend front_http_plain:option log-http-requests':
            option = reversed_http_log[data[0]]
            self.frontend['front_http_plain']['log_http_requests'] = option
        elif name == 'frontend front_http_plain:bind':
            address, port = data
            self.frontend['front_http_plain']['bind'] = {}
            self.frontend['front_http_plain']['bind']['address'] = address
            self.frontend['front_http_plain']['bind']['port'] = port
        elif name == 'frontend front_http_plain:maxconn':
            maxconn = data[0]
            self.frontend['front_http_plain']['maxconn'] = maxconn
        else:
            msg = 'Could not parse config, name:[{name}], data:[{data}]'.format(name=name, data=data)
            logger.error(msg)
            raise Exception(msg)

def validate_haproxy_config(config_data, haproxy_command):
    """ Writes the config into a temporary file and validates it using the HAProxy's
    -c check mode.
    """
    try:
        with NamedTemporaryFile(prefix='zato-tmp') as tf:

            tf.write(config_data.encode('utf8'))
            tf.flush()

            common_msg = 'config_file:`{}`'
            common_msg = common_msg.format(open(tf.name).read())

            timeout_msg = 'HAProxy didn\'t respond in `{}` seconds. '
            rc_non_zero_msg = 'Failed to validate the config file using HAProxy. '

            command = [haproxy_command, '-c', '-f', tf.name]
            timeouting_popen(command, HAPROXY_VALIDATE_TIMEOUT, timeout_msg, rc_non_zero_msg, common_msg)

    except Exception:
        msg = 'Caught an exception, e:`{}`'.format(format_exc())
        logger.error(msg)
        raise Exception(msg)
