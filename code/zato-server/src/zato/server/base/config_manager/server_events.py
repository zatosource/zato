# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.util.config import get_config_object
from zato.common.util.logging_ import set_logging_levels
from zato.server.base.config_manager.common import ConfigManagerImpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.server.base.config_manager import ConfigManager

    Bunch = Bunch
    ConfigManager = ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The entry of secrets.conf that holds the encrypted password of the Redis connection of the server
    Redis_Password_Key = 'server_conf.redis.password'

# ################################################################################################################################
# ################################################################################################################################

class ServerEvents(ConfigManagerImpl):
    """ Applies in each process the changes to the server that another process made and sent as events.
    """

# ################################################################################################################################

    def on_config_event_Server_Env_Variables_Apply(self:'ConfigManager', msg:'Bunch') -> 'None':
        """ Sets and deletes the environment variables of this process as another process did.
        """
        for key, value in msg.set_variables.items():
            os.environ[key] = value

        # A variable whose value is empty uses its built-in default, which it may have used already
        for key in msg.deleted_variables:
            _ = os.environ.pop(key, None)

# ################################################################################################################################

    def on_config_event_Server_Redis_Reload(self:'ConfigManager', msg:'Bunch') -> 'None':
        """ Reads the Redis configuration that another process saved and rebuilds the Redis client of the cache.
        """
        ram_section = self.server.fs_server_config.redis

        for key, value in msg.section.items():
            ram_section[key] = value

        # The password is not in the event, only the fact that secrets.conf holds a new one
        if msg.has_password:
            secrets = get_config_object(self.server.repo_location, 'secrets.conf')
            encrypted = secrets['zato'][ModuleCtx.Redis_Password_Key] # type: ignore
            ram_section['password'] = self.server.crypto_manager.decrypt(encrypted)

        self.reconfigure_redis_cache()

# ################################################################################################################################

    def on_config_event_Server_Logging_Set(self:'ConfigManager', msg:'Bunch') -> 'None':
        _ = set_logging_levels(msg.text)

# ################################################################################################################################

    def on_config_event_Server_File_Delete(self:'ConfigManager', msg:'Bunch') -> 'None':
        """ Removes from the service store of this process the objects of a file that another process deleted,
        which removed them from the ODB already.
        """
        self.server.service_store.delete_objects_by_file_path(msg.path, delete_from_odb=False)

# ################################################################################################################################

    def on_config_event_Server_Pubsub_Cleanup(self:'ConfigManager', msg:'Bunch') -> 'None':
        """ Removes the subscriptions of a deleted security definition or REST endpoint from this process.
        """
        for sub_key, username in msg.subscriptions:
            self.cleanup_subscription(sub_key, username)

        # The subscriptions of a REST endpoint belong to many clients, which remain in the pattern matcher
        if msg.client_username:
            self.server.pubsub_pattern_matcher.remove_client(msg.client_username)

# ################################################################################################################################
# ################################################################################################################################
