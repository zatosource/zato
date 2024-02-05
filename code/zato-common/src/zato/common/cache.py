'''
# -*- coding: utf-8 -*-

# stdlib
import os
from json import loads
from time import time

# Zato
from zato.common.typing_ import cast_
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_, anydict, callable_, strlistdict
    from zato.server.base.parallel import ParallelServer
    from zato.server.connection.jira_ import JiraClient

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Cache_Name_Pattern = 'zato.dictholder.{}'

# ################################################################################################################################
# ################################################################################################################################

class InfoResult:

    data: 'any_'
    is_cache_hit: 'bool'
    cache_expiry: 'float'
    cache_hits: 'int' = 0

# ################################################################################################################################
# ################################################################################################################################

class DictHolderConfig:

    name: 'str'
    server: 'ParallelServer'
    on_data_missing_func: 'callable_'
    use_json: 'bool' = False

# ################################################################################################################################
# ################################################################################################################################

class DictHolder:

    def __init__(self, config:'DictHolderConfig'):
        self.name = config.name
        self.server = config.server
        self.on_data_missing_func = config.on_data_missing_func

# ################################################################################################################################

    def _get_entry_from_cache(self) -> 'any_':
        return None

    def _store_data_in_cache(self, data:'any_') -> 'any_':
        return None

# ################################################################################################################################

    def get_all(self) -> 'InfoResult':

        # Local variables
        cache_entry:'any_'

        # Our response to produce
        out = InfoResult()

        # If we have anything in our cache, we can return it immediately ..
        if cache_entry := self._get_entry_from_cache():

            # .. assign the actual value ..
            out.data = cache_entry.value

            # .. indicate that it came from the cache ..
            out.is_cache_hit = True
            out.cache_hits = cache_entry.hits

            # .. build the remaining expiration time, in seconds ..
            # .. rounded down to make sure it does not take too much log space  ..
            expiry:'float' = cache_entry.expires_at - time()
            expiry = round(expiry, 2)

            # .. now, can assign the expiration time ..
            out.cache_expiry = expiry

            # .. and return the result to the caller.
            return out

        # .. we are here if the cache is empty ..
        else:

            # .. since we had nothing in the cache, we need to obtain it from our callback function ..
            data = self.on_data_missing_func()

            # .. then we can cache it ..
            expiry:'float' = self._store_data_in_cache(data)

            # .. build the result ..
            out.data = data
            out.is_cache_hit = False
            out.cache_expiry = expiry

            # .. and now, we can return it to our caller.
            return out

# ################################################################################################################################
# ################################################################################################################################

class JiraDataBuilder:

    def __init__(self, config:'Bunch', client:'JiraClient') -> 'None':
        self.config = config
        self.client = client

# ################################################################################################################################

    def _get_data_dict(self) -> 'anydict':

        file_name = os.environ['Zato_Test_Jira_Test_Data']
        with open(file_name) as f:
            data = f.read()

        data = loads(data)
        return data

# ################################################################################################################################

    def get_data(self) -> 'anydict':

        # Our response to produce
        out:'strlistdict' = {}

        data = self._get_data_dict()
        names = data['names']

        for key, value in names.items():
            keys = out.setdefault(value, [])
            keys.append(key)

        return out

# ################################################################################################################################
# ################################################################################################################################

class MyService(Service):

# ################################################################################################################################

    def on_key_missing(self) -> 'any_':

        # Local variables
        conn_name     = os.environ['Zato_Test_Jira_Connection_Name']
        config_file   = os.environ['Zato_Test_Jira_Config_File']
        config_stanza = os.environ['Zato_Test_Jira_Config_Stanza']

        config:'Bunch' = self.user_config[config_file][config_stanza]

        # Create a reference to our connection definition ..
        jira = self.cloud.jira[conn_name]

        # .. obtain a client to Jira ..
        with jira.conn.client() as client:

            # .. cast to enable code completion ..
            client = cast_('JiraClient', client)

            # .. create a business object to handle Jira connections ..
            builder = JiraDataBuilder(config, client)

            # .. obtain the result from Jira ..
            result:'anydict' = builder.get_data()

        # .. and return it to our caller.
        return result

# ################################################################################################################################

    def handle(self) -> 'None':

        config = DictHolderConfig()
        config.name = 'Testing'
        config.server = self.server
        config.on_data_missing_func = self.on_key_missing

        holder = DictHolder(config)
        data = holder.get_all()

        data

# ################################################################################################################################
# ################################################################################################################################
'''
