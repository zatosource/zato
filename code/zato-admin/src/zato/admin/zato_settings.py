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

# Zato
from zato.common.util import decrypt

SSL_KEY_FILE = './config/repo/zato-admin-priv-key.pem'
SSL_CERT_FILE = './config/repo/zato-admin-cert.pem'
SSL_CA_CERTS = './config/repo/zato-admin-ca-certs.pem'

LB_AGENT_CONNECT_TIMEOUT=500 # In milliseconds

def _update_globals(config):
    globals()['DATABASES'] = {'default': {}}
    for k, v in config.items():
        if not k.startswith('DATABASE_'):
            globals()[k] = v
        else:
            default = globals()['DATABASES']['default']
            k = k.replace('DATABASE_', '', 1)
            if k == 'PASSWORD':
                v = decrypt(v, open(SSL_KEY_FILE).read())
            default[k] = str(v)

# ##############################################################################

# Maps SQLAlchemy engine's name to a UI-friendly one.
engine_friendly_name = {
    'postgresql': 'PostgreSQL',
    'oracle': 'Oracle',
    
    # These are not supported /yet/.
    #'mysql': 'MySQL',
    #'mssql': 'MS SQL Server',
    #'access': 'MS Access',
    #'firebird': 'Firebird',
    #'db2': 'DB2',
    #'informix':'Informix'
}

odb_engine_friendly_name = {
    'postgresql': 'PostgreSQL',
    'oracle': 'Oracle',
    #'mysql': 'MySQL',
}

django_sqlalchemy_engine = {
    'postgresql': 'postgresql_psycopg2',
    #'mysql':'mysql',
    'oracle':'oracle',
    'dummy':'dummy'
}

sqlalchemy_django_engine = dict((v,k) for k,v in django_sqlalchemy_engine.items())

# Maps job types as they are used by servers into UI friendly names.
job_type_friendly_names = {
    'one_time': 'one-time',
    'interval_based': 'interval-based',
    'cron_style': 'cron-style',
}


# Maps AMQP delivery modes to UI-friendly names
delivery_friendly_name = {
    1:'Non-persistent',
    2:'Persistent',
}
