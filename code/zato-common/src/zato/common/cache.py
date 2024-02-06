'''# -*- coding: utf-8 -*-

# stdlib
import os
from json import loads

# Zato
from zato.common.api import ZATO_NOT_GIVEN
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_, anydict, callable_, dictlist, strlistdict
    from zato.server.base.parallel import ParallelServer
    from zato.server.connection.cache import Cache
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
    cache_key_suffix: 'str'
    server: 'ParallelServer'
    on_data_missing_func: 'callable_'
    use_json: 'bool' = False

# ################################################################################################################################
# ################################################################################################################################

class DictHolder:

    # Type hints
    cache: 'Cache'

    def __init__(self, config:'DictHolderConfig'):
        self.server = config.server
        self.cache_key_suffix = config.cache_key_suffix
        self.on_data_missing_func = config.on_data_missing_func
        self.cache_name = ModuleCtx.Cache_Name_Pattern.format(config.name)
        self.set_cache()

# ################################################################################################################################

    def set_cache(self):
        cache_api = self.server.worker_store.cache_api
        try:
            self.cache = cache_api.get_builtin_cache(self.cache_name)
        except KeyError:
            self.cache = None # type: ignore

# ################################################################################################################################

    def _get_cache_key(self) -> 'str':
        out = f'issue_fields.{self.cache_key_suffix}'
        return out

# ################################################################################################################################

    def _get_entry_from_cache(self) -> 'any_':

        # Local variables
        key = self._get_cache_key()

        if (out := self.cache.get(key)) != ZATO_NOT_GIVEN:
            return out

# ################################################################################################################################

    def _store_data_in_cache(self, data:'any_') -> 'int':

        # Local variables
        expiry = 300 # In seconds
        key = self._get_cache_key()

        self.cache.set(key, data, expiry=expiry)

        return expiry

# ################################################################################################################################

    def get_all(self) -> 'any_':

        # If we have anything in our cache, we can return it immediately ..
        if data := self._get_entry_from_cache():
            return data

        # .. we are here if the cache is empty ..
        else:

            # .. since we had nothing in the cache, we need to obtain it from our callback function ..
            data = self.on_data_missing_func()

            # .. then we can cache it ..
            _:'float' = self._store_data_in_cache(data)
            return data

# ################################################################################################################################
# ################################################################################################################################

class JiraDataBuilder:

    def __init__(self, service:'Service') -> 'None':
        self.service = service

        self.conn_name = os.environ['Zato_Test_Jira_Connection_Name']
        config_file    = os.environ['Zato_Test_Jira_Config_File']
        config_stanza  = os.environ['Zato_Test_Jira_Config_Stanza']

        self.config:'Bunch' = self.service.user_config[config_file][config_stanza]

# ################################################################################################################################

    def _get_jira_client(self) -> 'JiraClient':

        # Local variables


        # Create a reference to our connection definition ..
        jira = self.service.cloud.jira[self.conn_name]

        # .. obtain a client to Jira ..
        with jira.conn.client() as client:
            return client

# ################################################################################################################################

    def _get_data_dict(self) -> 'anydict':

        file_name = os.environ['Zato_Test_Jira_Test_Data']
        with open(file_name) as f:
            data = f.read()

        data = loads(data)
        return data

# ################################################################################################################################

    def _get_custom_fields_from_file(self) -> 'anydict':

        # Our response to produce
        out:'strlistdict' = {}

        data = self._get_data_dict()
        names = data['names']

        for key, value in names.items():
            keys = out.setdefault(value, [])
            keys.append(key)

        return out

# ################################################################################################################################

    def _get_custom_fields_from_jira(self) -> 'anydict':

        # Our response to produce
        out:'strlistdict' = {}

        client = self._get_jira_client()
        fields:'dictlist' = client.get_all_custom_fields()

        for field in fields:
            key = field['id']
            value = field['name']
            keys = out.setdefault(value, [])
            keys.append(key)

        return out

# ################################################################################################################################

    def _on_custom_fields_missing_in_cache(self) -> 'anydict':

        out = self._get_custom_fields_from_jira()
        return out

# ################################################################################################################################

    def get_custom_fields(self) -> 'anydict':

        config = DictHolderConfig()
        config.name = 'jira'
        config.cache_key_suffix = self.conn_name
        config.server = self.service.server
        config.on_data_missing_func = self._on_custom_fields_missing_in_cache

        holder = DictHolder(config)
        data = holder.get_all()

        return data

# ################################################################################################################################

    def get_tickets(self, status:'str') -> 'dictlist':

        client = self._get_jira_client()
        tickets:'dictlist' = client.jql_get_list_of_tickets(jql=None)
        tickets

# ################################################################################################################################
# ################################################################################################################################

class MyService(Service):

    def handle(self) -> 'None':

        builder = JiraDataBuilder(self)

        custom_fields = builder.get_custom_fields()
        custom_fields

        tickets = builder.get_tickets('')
        tickets

# ################################################################################################################################
# ################################################################################################################################
'''
