# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import Audit_Config, On_Prem_Gateway
from zato.common.audit_log.common import AuditEvent
from zato.server.config_audit import record_service_config_change
from zato.server.on_prem_gateway import get_public_address, HubRefused, OnPremGatewayManager, parse_hosts
from zato.server.service import Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import boolnone, strlist

    # Dummy assignments to satisfy type checkers
    boolnone = boolnone
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

_service_name_prefix = 'zato.on-prem-gateway.'

# The value used when the caller supplies no list of addresses.
_No_Hosts = ()

_Default_Is_Key_Reset_Required = On_Prem_Gateway.Default.Is_Key_Reset_Required

# ################################################################################################################################
# ################################################################################################################################

class _Base(AdminService):
    """ Provides every service in this module with the manager that performs the work.
    """

    def get_manager(self) -> 'OnPremGatewayManager':

        out = OnPremGatewayManager(self.server)

        return out

# ################################################################################################################################

    def get_is_key_reset_required(self, is_key_reset_required:'boolnone') -> 'bool':
        """ Applies the default when the caller does not state the setting.
        """
        if is_key_reset_required is None:
            is_key_reset_required = _Default_Is_Key_Reset_Required

        return is_key_reset_required

# ################################################################################################################################

    def get_hosts(self, hosts:'strlist') -> 'strlist':
        """ Validates the addresses on input, applying the same rules as the hub.
        """
        if not hosts:
            hosts = list(_No_Hosts)

        out = parse_hosts(hosts)

        return out

# ################################################################################################################################
# ################################################################################################################################

class GetList(_Base):
    """ Returns every on-premises gateway, each one with its runtime state from the hub.
    """
    name = _service_name_prefix + 'get-list'

    def handle(self) -> 'None':

        manager = self.get_manager()

        self.response.payload = manager.get_status_list()

# ################################################################################################################################
# ################################################################################################################################

class Get(_Base):
    """ Returns details of a single on-premises gateway.
    """
    name = _service_name_prefix + 'get'
    input = Int('id')

    def handle(self) -> 'None':

        # Extract the input ..
        id = self.request.input.id

        # .. look the gateway up ..
        manager = self.get_manager()
        gateway = manager.get_by_id(id)

        if not gateway:
            raise Exception(f'On-premises gateway with id `{id}` not found')

        # .. and return it to the caller.
        self.response.payload = gateway

# ################################################################################################################################
# ################################################################################################################################

class Create(_Base):
    """ Creates a new on-premises gateway.
    """
    name = _service_name_prefix + 'create'
    input = 'name', 'is_active', '-hosts', '-is_key_reset_required'
    output = 'id', 'name'

    def handle(self) -> 'None':

        # Extract and validate the input ..
        input = self.request.input
        name = input.name.strip()
        hosts = self.get_hosts(input.hosts)
        is_key_reset_required = self.get_is_key_reset_required(input.is_key_reset_required)

        if not name:
            raise Exception('An on-premises gateway needs a name')

        manager = self.get_manager()

        # .. reject a duplicate ..
        if manager.get(name):
            raise Exception(f'An on-premises gateway named `{name}` already exists')

        # .. create the gateway ..
        id = manager.create(name, input.is_active, hosts, is_key_reset_required)

        # .. the hub translates the configuration into listeners and host names, and a
        # configuration it refuses is not retained ..
        try:
            manager.sync()
        except HubRefused:
            manager.delete(id)
            raise

        # .. the creation is recorded in the audit trail ..
        after = manager.get_by_id(id)

        record_service_config_change(
            self,
            action=AuditEvent.Config_Created,
            object_type=Audit_Config.Object_Type.On_Prem_Gateway,
            object_name=name,
            after=after,
        )

        # .. and the details are returned to the caller.
        self.response.payload.id = id
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class Edit(_Base):
    """ Updates an existing on-premises gateway.
    """
    name = _service_name_prefix + 'edit'
    input = Int('id'), 'name', 'is_active', '-hosts', '-is_key_reset_required'
    output = 'id', 'name'

    def handle(self) -> 'None':

        # Extract and validate the input ..
        input = self.request.input
        id = input.id
        name = input.name.strip()
        hosts = self.get_hosts(input.hosts)
        is_key_reset_required = self.get_is_key_reset_required(input.is_key_reset_required)

        if not name:
            raise Exception('An on-premises gateway needs a name')

        manager = self.get_manager()

        # .. the gateway is required to exist ..
        before = manager.get_by_id(id)

        if not before:
            raise Exception(f'On-premises gateway with id `{id}` not found')

        # .. a change of name must not conflict with an existing gateway ..
        if other := manager.get(name):
            if other['id'] != id:
                raise Exception(f'An on-premises gateway named `{name}` already exists')

        # .. store the changes ..
        manager.edit(id, name, input.is_active, hosts, is_key_reset_required)

        # .. the hub reconciles its runtime configuration, and changes it refuses are
        # reverted to the previous configuration ..
        try:
            manager.sync()
        except HubRefused:
            manager.edit(id, before['name'], before['is_active'], before['hosts'], before['is_key_reset_required'])
            raise

        # .. the update is recorded in the audit trail with its previous and current form ..
        after = manager.get_by_id(id)

        record_service_config_change(
            self,
            action=AuditEvent.Config_Edited,
            object_type=Audit_Config.Object_Type.On_Prem_Gateway,
            object_name=name,
            before=before,
            after=after,
        )

        # .. and the details are returned to the caller.
        self.response.payload.id = id
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Base):
    """ Deletes an on-premises gateway along with the key retained for it by the hub.
    """
    name = _service_name_prefix + 'delete'
    input = Int('id')

    def handle(self) -> 'None':

        # Extract the input ..
        id = self.request.input.id

        manager = self.get_manager()

        # .. the gateway is required to exist ..
        before = manager.get_by_id(id)

        if not before:
            raise Exception(f'On-premises gateway with id `{id}` not found')

        # .. delete the gateway ..
        manager.delete(id)

        # .. the hub closes its listeners and discards the key ..
        manager.sync()

        # .. and the deletion is recorded in the audit trail with the previous configuration.
        record_service_config_change(
            self,
            action=AuditEvent.Config_Deleted,
            object_type=Audit_Config.Object_Type.On_Prem_Gateway,
            object_name=before['name'],
            before=before,
        )

# ################################################################################################################################
# ################################################################################################################################

class GetEnrollmentToken(_Base):
    """ Issues a single-use enrollment token for one gateway.
    """
    name = _service_name_prefix + 'get-enrollment-token'
    input = Int('id'), '-dashboard_host'
    output = 'name', 'token', 'expires_at'

    def handle(self) -> 'None':

        # Extract the input ..
        input = self.request.input
        id = input.id

        manager = self.get_manager()

        # .. the gateway is required to exist ..
        gateway = manager.get_by_id(id)

        if not gateway:
            raise Exception(f'On-premises gateway with id `{id}` not found')

        # .. the hub recognizes only gateways that were published to it ..
        manager.sync()

        # .. the token conveys the address that the gateway connects to ..
        address = get_public_address(input.dashboard_host)

        # .. issue the token ..
        name = gateway['name']
        response = manager.hub.mint_token(name, address)

        # .. and return it to the caller.
        self.response.payload.name = name
        self.response.payload.token = response['token']
        self.response.payload.expires_at = response['expires_at']

# ################################################################################################################################
# ################################################################################################################################

class ResetKey(_Base):
    """ Revokes the key of a gateway, which requires the gateway to enroll again.
    """
    name = _service_name_prefix + 'reset-key'
    input = Int('id')

    def handle(self) -> 'None':

        # Extract the input ..
        id = self.request.input.id

        manager = self.get_manager()

        # .. the gateway is required to exist ..
        gateway = manager.get_by_id(id)

        if not gateway:
            raise Exception(f'On-premises gateway with id `{id}` not found')

        # .. and the key is retained by the hub.
        manager.hub.reset_key(gateway['name'])

# ################################################################################################################################
# ################################################################################################################################

class Sync(_Base):
    """ Publishes the complete configuration to the hub. Invoked on startup and after every
    change made anywhere else.
    """
    name = _service_name_prefix + 'sync'

    def handle(self) -> 'None':

        manager = self.get_manager()

        # No publication is required if no gateway has been configured ..
        gateways = manager.get_list()

        if not gateways:
            self.logger.info('No on-premises gateways are configured, nothing to push')
            return

        # .. otherwise the configuration is published, an unavailable hub being reported in the log.
        manager.sync()

# ################################################################################################################################
# ################################################################################################################################
