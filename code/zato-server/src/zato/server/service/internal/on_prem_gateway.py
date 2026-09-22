# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import Audit_Config
from zato.common.audit_log.common import AuditEvent
from zato.server.config_audit import record_service_config_change
from zato.server.on_prem_gateway import get_public_address, OnPremGatewayManager, parse_hosts
from zato.server.service import Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

    # Dummy assignment to satisfy type checkers
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

_service_name_prefix = 'zato.on-prem-gateway.'

# What an optional list of addresses amounts to when the caller sent none.
_No_Hosts = ()

# ################################################################################################################################
# ################################################################################################################################

class _Base(AdminService):
    """ Gives every service in this module the manager that does the actual work.
    """

    def get_manager(self) -> 'OnPremGatewayManager':

        out = OnPremGatewayManager(self.server)

        return out

# ################################################################################################################################

    def get_hosts(self, hosts:'strlist') -> 'strlist':
        """ Validates the addresses on input, which is the same check the hub makes.
        """
        if not hosts:
            hosts = _No_Hosts

        out = parse_hosts(hosts)

        return out

# ################################################################################################################################
# ################################################################################################################################

class GetList(_Base):
    """ Returns every on-premises gateway, each one with whatever the hub knows about it.
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

        # .. and return it to our caller.
        self.response.payload = gateway

# ################################################################################################################################
# ################################################################################################################################

class Create(_Base):
    """ Creates a new on-premises gateway.
    """
    name = _service_name_prefix + 'create'
    input = 'name', 'is_active', '-hosts'
    output = 'id', 'name'

    def handle(self) -> 'None':

        # Extract and validate the input ..
        input = self.request.input
        name = input.name.strip()
        hosts = self.get_hosts(input.hosts)

        if not name:
            raise Exception('An on-premises gateway needs a name')

        manager = self.get_manager()

        # .. refuse to create a duplicate ..
        if manager.get(name):
            raise Exception(f'An on-premises gateway named `{name}` already exists')

        # .. create it now ..
        id = manager.create(name, input.is_active, hosts)

        # .. the hub is what turns the configuration into listeners and host names ..
        manager.sync()

        # .. the creation lands in the audit trail ..
        after = manager.get_by_id(id)

        record_service_config_change(
            self,
            action=AuditEvent.Config_Created,
            object_type=Audit_Config.Object_Type.On_Prem_Gateway,
            object_name=name,
            after=after,
        )

        # .. and the details go back to our caller.
        self.response.payload.id = id
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class Edit(_Base):
    """ Updates an existing on-premises gateway.
    """
    name = _service_name_prefix + 'edit'
    input = Int('id'), 'name', 'is_active', '-hosts'
    output = 'id', 'name'

    def handle(self) -> 'None':

        # Extract and validate the input ..
        input = self.request.input
        id = input.id
        name = input.name.strip()
        hosts = self.get_hosts(input.hosts)

        if not name:
            raise Exception('An on-premises gateway needs a name')

        manager = self.get_manager()

        # .. the gateway has to exist ..
        before = manager.get_by_id(id)

        if not before:
            raise Exception(f'On-premises gateway with id `{id}` not found')

        # .. a rename must not clash with another one ..
        if other := manager.get(name):
            if other['id'] != id:
                raise Exception(f'An on-premises gateway named `{name}` already exists')

        # .. save the changes ..
        manager.edit(id, name, input.is_active, hosts)

        # .. let the hub reconcile what it is running ..
        manager.sync()

        # .. the edit lands in the audit trail with a before and after ..
        after = manager.get_by_id(id)

        record_service_config_change(
            self,
            action=AuditEvent.Config_Edited,
            object_type=Audit_Config.Object_Type.On_Prem_Gateway,
            object_name=name,
            before=before,
            after=after,
        )

        # .. and the details go back to our caller.
        self.response.payload.id = id
        self.response.payload.name = name

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Base):
    """ Deletes an on-premises gateway, along with the key the hub held for it.
    """
    name = _service_name_prefix + 'delete'
    input = Int('id')

    def handle(self) -> 'None':

        # Extract the input ..
        id = self.request.input.id

        manager = self.get_manager()

        # .. the gateway has to exist ..
        before = manager.get_by_id(id)

        if not before:
            raise Exception(f'On-premises gateway with id `{id}` not found')

        # .. delete it now ..
        manager.delete(id)

        # .. the hub closes its listeners and forgets the key ..
        manager.sync()

        # .. and the deletion lands in the audit trail with what the gateway looked like.
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

        # .. the gateway has to exist ..
        gateway = manager.get_by_id(id)

        if not gateway:
            raise Exception(f'On-premises gateway with id `{id}` not found')

        # .. the hub only knows about gateways that were pushed to it ..
        manager.sync()

        # .. the token carries the address the gateway is to connect back to ..
        address = get_public_address(input.dashboard_host)

        # .. mint it now ..
        name = gateway['name']
        response = manager.hub.mint_token(name, address)

        # .. and hand it to our caller.
        self.response.payload.name = name
        self.response.payload.token = response['token']
        self.response.payload.expires_at = response['expires_at']

# ################################################################################################################################
# ################################################################################################################################

class ResetKey(_Base):
    """ Unbinds the key of a gateway. Its next connection has to enroll again.
    """
    name = _service_name_prefix + 'reset-key'
    input = Int('id')

    def handle(self) -> 'None':

        # Extract the input ..
        id = self.request.input.id

        manager = self.get_manager()

        # .. the gateway has to exist ..
        gateway = manager.get_by_id(id)

        if not gateway:
            raise Exception(f'On-premises gateway with id `{id}` not found')

        # .. and the hub is what holds the key.
        manager.hub.reset_key(gateway['name'])

# ################################################################################################################################
# ################################################################################################################################

class Sync(_Base):
    """ Pushes the whole configuration to the hub. This runs on startup and after every
    change made anywhere else.
    """
    name = _service_name_prefix + 'sync'

    def handle(self) -> 'None':

        manager = self.get_manager()

        # There is nothing to push if no gateway was ever configured ..
        gateways = manager.get_list()

        if not gateways:
            self.logger.info('No on-premises gateways are configured, nothing to push')
            return

        # .. otherwise the hub has to be up for the push to land.
        manager.sync()

# ################################################################################################################################
# ################################################################################################################################
