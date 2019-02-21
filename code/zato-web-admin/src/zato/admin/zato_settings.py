# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# Zato
from zato.common import SCHEDULER
from zato.common.crypto import resolve_secret_key, WebAdminCryptoManager
from zato.common.util.cli import read_stdin_data

# ################################################################################################################################

SSL_KEY_FILE = './config/repo/web-admin-priv-key.pem'
SSL_CERT_FILE = './config/repo/web-admin-cert.pem'
SSL_CA_CERTS = './config/repo/web-admin-ca-certs.pem'

LB_AGENT_CONNECT_TIMEOUT=500 # In milliseconds

# ################################################################################################################################

def update_globals(config, base_dir='.'):
    globals()['DATABASES'] = {'default': {}}

    for name in 'zato_secret_key', 'well_known_data', 'DATABASE_PASSWORD', 'SECRET_KEY', 'ADMIN_INVOKE_PASSWORD':
        config[name] = config[name].encode('utf8')

    # If secret key is not given directly in the config file, we will expect to find it
    # on command line.
    zato_secret_key = config['zato_secret_key']
    zato_secret_key = resolve_secret_key(zato_secret_key)
    config['zato_secret_key'] = zato_secret_key

    cm = WebAdminCryptoManager.from_secret_key(
        config['zato_secret_key'], config['well_known_data'], stdin_data=read_stdin_data())

    for k, v in config.items():
        if k.startswith('DATABASE_'):
            default = globals()['DATABASES']['default']
            k = k.replace('DATABASE_', '', 1)
            if k == 'PASSWORD' and config['db_type'] != 'sqlite':
                v = cm.decrypt(v)
            default[k] = str(v)
        else:
            if k == 'ADMIN_INVOKE_PASSWORD':
                v = cm.decrypt(v)
            elif k == 'log_config':
                v = os.path.join(base_dir, v)
            globals()[k] = v

# ################################################################################################################################

django_sqlalchemy_engine = {
    'postgresql': 'postgresql_psycopg2',
    'mysql':'mysql',
    'oracle':'oracle',
    'sqlite':'sqlite3',
    'dummy':'dummy'
}

# ################################################################################################################################

# Maps job types as they are used by servers into UI friendly names.
job_type_friendly_names = {
    SCHEDULER.JOB_TYPE.ONE_TIME: 'one-time',
    SCHEDULER.JOB_TYPE.INTERVAL_BASED: 'interval-based',
    SCHEDULER.JOB_TYPE.CRON_STYLE: 'cron-style',
}

# ################################################################################################################################

# Maps AMQP delivery modes to UI-friendly names
delivery_friendly_name = {
    1:'Non-persistent',
    2:'Persistent',
}

# ################################################################################################################################
