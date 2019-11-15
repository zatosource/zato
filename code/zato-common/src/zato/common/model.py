# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Unlike zato.common.odb.model - this place is where DB-independent models are kept,
# regardless if they're backed by an SQL database or not.

'''
* Name
* Address (ftp:// or ftps://) = ftp://0.0.0.0:21021, if ftps:// use server's TLS certificate
* Is active = True
* Max connections = 300
* Max connections per IP = 20
* Command timeout = 300
* Banner = 'Welcome'
* Log prefix = '%(remote_ip)s:%(remote_port)s-[%(username)s]'
* Base directory = './work/ftp'
* Read throttle = 10
* Write throttle = 10
* Masquerade address
* Passive ports
* Log level - INFO / DEBUG = INFO
* Service
* Service invocation mode sync / async = async (not visible in web-admin)
'''

class FTPChannel(object):
    def __init__(self):
        self.id   = None            # type: int
        self.name = None            # type: str
        self.is_active = None       # type: bool
        self.max_connections = None # type: int
        self.max_conn_per_ip = None # type: int
        self.command_timeout = None # type: int
        self.banner = None          # type: str
        self.log_prefix = None      # type: str
        self.base_directory = None  # type: str
        self.read_throttle = None   # type: int
        self.write_throttle = None  # type: int
        self.masq_address = None    # type: str
        self.passive_ports = None   # type: str
        self.log_level = None       # type: str
        self.service_name = None    # type: str
        self.srv_invoke_mode = None # type: str
