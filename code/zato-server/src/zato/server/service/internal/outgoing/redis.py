# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.util import get_config
from zato.server.service import AsIs, Bool, Int, SIOElem
from zato.server.service.internal import AdminService, ChangePasswordBase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.ext.configobj_ import ConfigObj

    Bunch = Bunch
    ConfigObj = ConfigObj

# ################################################################################################################################

def get_config_object(repo_location, conf_file):
    # type: (str) -> dict
    return get_config(repo_location, conf_file, bunchified=False)

# ################################################################################################################################

def set_kvdb_config(server_config, input_data, redis_sentinels):
    # type: (dict, Bunch, str) -> None

    server_config['kvdb']['host'] = input_data.host or ''
    server_config['kvdb']['port'] = int(input_data.port) if input_data.port else ''
    server_config['kvdb']['db'] = int(input_data.db) if input_data.db else ''
    server_config['kvdb']['use_redis_sentinels'] = input_data.use_redis_sentinels
    server_config['kvdb']['redis_sentinels'] = redis_sentinels
    server_config['kvdb']['redis_sentinels_master'] = input_data.redis_sentinels_master or ''

# ################################################################################################################################

def update_config_file(config, repo_location, conf_file):
    # type: (ConfigObj, str, str) -> None

    conf_path = os.path.join(repo_location, conf_file)
    with open(conf_path, 'wb') as f:
        config.write(f)

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):

    class SimpleIO:
        input_optional = 'id', 'name'
        output_optional = AsIs('id'), 'is_active', 'name', 'host', Int('port'), 'db', Bool('use_redis_sentinels'), \
            AsIs('redis_sentinels'), 'redis_sentinels_master'
        default_value = None

# ################################################################################################################################

    def get_data(self):

        # Response to produce
        out = []

        # For now, we only return one item containing data read from server.conf
        item = {
            'id': 123456,
            'name': 'default',
            'is_active': True,
        }

        config = get_config_object(self.server.repo_location, 'server.conf')
        config = config['kvdb']

        for elem in self.SimpleIO.output_optional:

            # Extract the embedded name or use it as is
            name = elem.name if isinstance(elem, SIOElem) else elem

            # These will not exist in server.conf
            if name in ('id', 'is_active', 'name'):
                continue

            value = config[name]

            if name == 'redis_sentinels':
                value = '\n'.join(value)

            # Add it to output
            item[name] = value

        # Add our only item to response
        out.append(item)

        return out

# ################################################################################################################################

    def handle(self):

        self.response.payload[:] = self.get_data()

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):

    class SimpleIO:
        input_optional = AsIs('id'), 'name', Bool('use_redis_sentinels')
        input_required = 'host', 'port', 'db', 'redis_sentinels', 'redis_sentinels_master'
        output_optional = 'name'

    def handle(self):

        # Local alias
        input = self.request.input

        # If provided, turn sentinels configuration into a format expected by the underlying KVDB object
        redis_sentinels = input.redis_sentinels or '' # type: str
        if redis_sentinels:

            redis_sentinels = redis_sentinels.splitlines()
            redis_sentinels = [str(elem).strip() for elem in redis_sentinels]

        # First, update the persistent configuration on disk ..
        config = get_config_object(self.server.repo_location, 'server.conf')
        set_kvdb_config(config, input, redis_sentinels)

        server_conf_path = os.path.join(self.server.repo_location, 'server.conf')
        with open(server_conf_path, 'wb') as f:
            config.write(f)

        # .. assign new in-RAM server-wide configuration ..
        set_kvdb_config(self.server.fs_server_config, input, redis_sentinels)

        # .. and rebuild the Redis connection object.
        self.server.kvdb.reconfigure(self.server.fs_server_config.kvdb)

        # Our callers expect it
        self.response.payload.name = self.request.input.name

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the password of a Redis connection
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        pass

    def handle(self):

        # Local alias
        input = self.request.input

        # Encryption requires bytes
        password = input.password1.encode('utf8')

        # Now, encrypt the input password
        password = self.crypto.encrypt(password)

        # Decode it back for later use
        password = password.decode('utf8')

        # Find our secrets config
        config = get_config_object(self.server.repo_location, 'secrets.conf')

        # Set the new secret
        config['zato']['server_conf.kvdb.password'] = password

        # Update the on-disk configuration
        update_config_file(config, self.server.repo_location, 'secrets.conf')

        # Change in-RAM password
        self.server.kvdb.set_password(password)

        self.response.payload.id = self.request.input.id

# ################################################################################################################################
# ################################################################################################################################
