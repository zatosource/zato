# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# Zato
from zato.common import SCHEDULER
from zato.common.util import decrypt

SSL_KEY_FILE = './config/repo/web-admin-priv-key.pem'
SSL_CERT_FILE = './config/repo/web-admin-cert.pem'
SSL_CA_CERTS = './config/repo/web-admin-ca-certs.pem'

LB_AGENT_CONNECT_TIMEOUT=500 # In milliseconds

def update_globals(config, base_dir='.'):
    globals()['DATABASES'] = {'default': {}}
    priv_key = open(os.path.abspath(os.path.join(base_dir, SSL_KEY_FILE))).read()
    for k, v in config.items():
        if k.startswith('DATABASE_'):
            default = globals()['DATABASES']['default']
            k = k.replace('DATABASE_', '', 1)
            if k == 'PASSWORD' and config['db_type'] != 'sqlite':
                v = decrypt(v, priv_key)
            default[k] = str(v)
        else:
            if k == 'ADMIN_INVOKE_PASSWORD':
                v = decrypt(v, priv_key)
            elif k == 'log_config':
                v = os.path.join(base_dir, v)
            globals()[k] = v

# ##############################################################################

# Maps SQLAlchemy engine's name to a UI-friendly one.
engine_friendly_name = {
    'postgresql+pg8000': 'PostgreSQL',
    'oracle': 'Oracle',
    'mysql+pymysql': 'MySQL',

    # These are not supported /yet/.
    'mssql': 'MS SQL Server',
    # 'access': 'MS Access',
    # 'firebird': 'Firebird',
    # 'db2': 'DB2',
    # 'informix':'Informix'
}

odb_engine_friendly_name = {
    'postgresql+pg8000': 'PostgreSQL',
    'oracle': 'Oracle',
    'mysql+pymysql': 'MySQL',
    'mssql': 'MS SQL Server',
}

django_sqlalchemy_engine = {
    'postgresql': 'postgresql_psycopg2',
    'mysql':'mysql',
    'oracle':'oracle',
    'sqlite':'sqlite3',
    'dummy':'dummy',
    'mssql':'mssql'
}

sqlalchemy_django_engine = dict((v,k) for k,v in django_sqlalchemy_engine.items())

# Maps job types as they are used by servers into UI friendly names.
job_type_friendly_names = {
    SCHEDULER.JOB_TYPE.ONE_TIME: 'one-time',
    SCHEDULER.JOB_TYPE.INTERVAL_BASED: 'interval-based',
    SCHEDULER.JOB_TYPE.CRON_STYLE: 'cron-style',
}


# Maps AMQP delivery modes to UI-friendly names
delivery_friendly_name = {
    1:'Non-persistent',
    2:'Persistent',
}
