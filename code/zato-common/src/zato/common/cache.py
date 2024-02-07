'''
# -*- coding: utf-8 -*-

# stdlib
import os
from dataclasses import dataclass
from json import loads

# Zato
from zato.common.api import ZATO_NOT_GIVEN
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_, anydict, anylist, callable_, dictlist, strdict, strlistdict
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
        self.config

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

    def _get_all_field_types_from_file(self) -> 'anydict':

        # Our response to produce
        out:'strlistdict' = {}

        data = self._get_data_dict()
        names = data['names']

        for key, value in names.items():
            keys = out.setdefault(value, [])
            keys.append(key)

        return out

# ################################################################################################################################

    def _get_all_field_types_from_jira(self) -> 'anydict':

        # Our response to produce
        out:'strlistdict' = {}

        client = self._get_jira_client()
        fields:'any_' = client.get_all_fields() # type: ignore

        for field in fields:
            key = field['id']
            value = field['name']
            keys = out.setdefault(value, [])
            keys.append(key)

        # Sort the output
        _out:'anydict' = {}
        for key in sorted(out):
            _out[key] = out[key]

        return _out

# ################################################################################################################################

    def _on_field_types_missing_in_cache(self) -> 'anydict':

        out = self._get_all_field_types_from_jira()
        return out

# ################################################################################################################################

    def get_all_field_types(self) -> 'anydict':

        config = DictHolderConfig()
        config.name = 'jira'
        config.cache_key_suffix = self.conn_name
        config.server = self.service.server
        config.on_data_missing_func = self._on_field_types_missing_in_cache

        holder = DictHolder(config)
        data = holder.get_all()

        return data

# ################################################################################################################################

    def _get_map_by_ticket_type(self, ticket_type:'str') -> 'strdict':

        map_key = f'map_{ticket_type}'
        map:'strdict' = self.config[map_key]

        return map

# ################################################################################################################################

    def _extract_fields_from_ticket(self, ticket:'strdict') -> 'strdict':

        # Type hints
        fields:'any_'

        # Our response to produce
        out:'strdict' = {}
        field_types:'strdict' = self.get_all_field_types()

        # Local variables
        fields = ticket['fields']

        # Extract the ticket type ..
        ticket_type = fields['issuetype']
        ticket_type = ticket_type['name']

        # .. this can be pre-populated ..
        out['ticket_type'] = ticket_type

        # .. find the names of the fields that we need to read from the ticket ..
        fields_to_extract:'any_' = self._get_map_by_ticket_type(ticket_type)
        fields_to_extract = sorted(fields_to_extract)

        # .. go through all the fields to be extract ..
        for field_name in fields_to_extract:

            # .. get the list of IDs that this name maps to
            field_id_list = field_types[field_name]

            # .. find the first matching value from the potential IDs ..
            for field_id in field_id_list:

                # .. if there are multiple IDs for that field name, ..
                # .. the first one with a business value will be used ..
                value = fields[field_id]

                # .. status needs to be special-cased ..
                if field_name == 'Status':
                    value = value['name']

                # .. note that we can always set it ..
                out[field_name] = value

                # .. but if actually was a business value, we skip other IDs ..
                # .. the end effect being that we can always return something here ..
                # .. even if it is only None. Note also that we do not support ..
                # .. two different IDs with a business value in both ..
                if value:
                    continue

        # Now, we can return the response to our caller
        return out

# ################################################################################################################################

    def _extract_fields_from_tickets(self, tickets:'dictlist') -> 'dictlist':

        # Local variables
        item:'strdict'

        # Our response to produce
        out:'dictlist' = []

        for item in tickets:
            item = self._extract_fields_from_ticket(item)
            out.append(item)

        # Now, we can return the response to our caller
        return out

# ################################################################################################################################

    def _build_models_from_tickets(self, tickets:'dictlist', parent_model:'any_', child_model:'any_') -> 'anylist':

        # Our response to produce
        out:'anylist' = []

        # Local variables
        status_map:'strdict' = self.config.status_map

        # Go through all the tickets that we have on input ..
        for parent_ticket in tickets:

            # .. this can and should be removed before we actually proceed to mapping ..
            ticket_type = parent_ticket.pop('ticket_type')

            # .. build an empty model for that ticket for later use ..
            model = parent_model()

            # .. get a mapping matching this ticket type ..
            map = self._get_map_by_ticket_type(ticket_type)

            # .. go through each of the fields in this ticket ..
            for field_name, field_value in parent_ticket.items():

                # .. map the field's name to the model attribute's name ..
                model_attr_name = map[field_name]

                # .. status needs to be special-cased ..
                if field_name == 'Status':
                    field_value = status_map[field_value]

                # .. populate the model ..
                setattr(model, model_attr_name, field_value)

                # .. and append it to the result ..
                out.append(model)

        # Now, return the response to our caller
        return out

# ################################################################################################################################

    def get_tickets(
        self,
        *,
        parent_model:'any_',
        child_model:'any_'=None,
        board_name:'str'='',
        ticket_type:'str'='',
        status:'str'='',
    ) -> 'anylist':

        # Base query that will always match ..
        jql = 'votes >= 0'

        # .. board names (projects) are optional ..
        if board_name:
            jql += f' and project = {board_name}'

        # .. ticket types are optional ..
        if ticket_type:
            jql += f' and issuetype = "{ticket_type}"'

        # .. statuses are optional ..
        if status:
            jql = f' and status = "{status}"'

        # .. obtains a Jira client ..
        client = self._get_jira_client()

        # .. get a list of tickets matching input criteria ..
        tickets:'dictlist' = client.jql_get_list_of_tickets(jql=jql)

        # .. extract the business fields from tickets ..
        tickets = self._extract_fields_from_tickets(tickets)

        # .. turn them into model instances ..
        models = self._build_models_from_tickets(tickets, parent_model, child_model)

        # .. and return the result to our caller.
        return models

# ################################################################################################################################
# ################################################################################################################################

class MyService(Service):

    def handle(self) -> 'None':

        self.response.payload = models

# ################################################################################################################################
# ################################################################################################################################
'''
