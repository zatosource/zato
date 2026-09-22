# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.cli.enmasse.client import get_server_client
from zato.cli.enmasse.util.secrets import Session_Key_Server_Dir
from zato.common.api import On_Prem_Gateway
from zato.common.json_internal import dumps
from zato.common.odb.query.generic import OnPremGatewayWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import anydict, anylist, listtuple, strlist

    # Add dummy assignments to satisfy type checkers
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The service that publishes the configuration to the hub.
_Sync_Service = 'zato.on-prem-gateway.sync'

# The permitted range of port numbers.
_Port_Min = 1
_Port_Max = 65535

# The value used for a gateway declared with no addresses.
_No_Hosts = ()

# Whether a gateway is active when the declaration does not state otherwise.
_Default_Is_Active = True

_Default_Is_Key_Reset_Required = On_Prem_Gateway.Default.Is_Key_Reset_Required

# ################################################################################################################################
# ################################################################################################################################

class OnPremGatewayImporter:
    """ Imports on-premises gateways from YAML.
    """

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer
        self.gateway_defs = {}

# ################################################################################################################################

    def get_gateways_from_db(self, session:'SASession') -> 'anydict':
        """ Returns all on-premises gateways from the database, keyed by name.
        """

        # Our response to produce
        out = {}

        wrapper = OnPremGatewayWrapper(session, self.importer.cluster_id)

        rows = wrapper.get_list()

        for row in rows:
            name = row['name']
            out[name] = {
                'id': row['id'],
                'name': name,
            }

        return out

# ################################################################################################################################

    def get_hosts(self, gateway:'anydict') -> 'strlist':
        """ Validates the addresses of one gateway, applying the same rules as the hub.
        """

        # Our response to produce
        out = []

        seen = set()
        name = gateway['name']
        hosts = gateway.get('hosts')

        if not hosts:
            hosts = _No_Hosts

        for item in hosts:

            item = item.strip()

            if not item:
                continue

            if ':' not in item:
                raise Exception(f'`{item}` of on-premises gateway `{name}` is not in the host:port format')

            host, _, port = item.rpartition(':')
            host = host.strip()
            port = port.strip()

            if not host:
                raise Exception(f'`{item}` of on-premises gateway `{name}` has no host')

            if not port.isdigit():
                raise Exception(f'`{item}` of on-premises gateway `{name}` has no numeric port')

            port_number = int(port)

            is_port_too_low = port_number < _Port_Min
            is_port_too_high = port_number > _Port_Max

            if is_port_too_low or is_port_too_high:
                raise Exception(
                    f'`{item}` of on-premises gateway `{name}` has a port outside the {_Port_Min}-{_Port_Max} range')

            item = f'{host}:{port_number}'

            if item in seen:
                raise Exception(f'`{item}` is listed more than once for on-premises gateway `{name}`')

            seen.add(item)
            out.append(item)

        out = sorted(out)

        return out

# ################################################################################################################################

    def sync_on_prem_gateways(self, gateway_list:'anylist', session:'SASession') -> 'listtuple':
        """ Synchronizes on-premises gateways from YAML with the database.

        Gateways are updated in place, never deleted and recreated, so that a gateway keeps
        the id and the name the hub bound its key to.
        """

        # Lists of created and updated gateways to report
        out_created = []
        out_updated = []

        db_gateways = self.get_gateways_from_db(session)

        wrapper = OnPremGatewayWrapper(session, self.importer.cluster_id)

        # A loopback listener serves a single endpoint, hence an address belongs to exactly
        # one gateway
        seen_hosts = {}

        for gateway in gateway_list:

            name = gateway['name']
            hosts = self.get_hosts(gateway)

            is_active = gateway.get('is_active')

            if is_active is None:
                is_active = _Default_Is_Active

            is_key_reset_required = gateway.get('is_key_reset_required')

            if is_key_reset_required is None:
                is_key_reset_required = _Default_Is_Key_Reset_Required

            for item in hosts:

                if owner := seen_hosts.get(item):
                    raise Exception(f'`{item}` is configured for both `{owner}` and `{name}`')

                seen_hosts[item] = name

            # Serialize the gateway body to its opaque form
            gateway_data = {'is_active': is_active, 'hosts': hosts, 'is_key_reset_required': is_key_reset_required}
            opaque = dumps(gateway_data)

            if db_gateway := db_gateways.get(name):

                # The gateway exists and is updated in place.
                gateway_id = db_gateway['id']

                update = wrapper.update(name, opaque, id=gateway_id)
                _ = session.execute(update)
                out_updated.append(gateway)

                logger.info('Updated on-premises gateway %s with id %s', name, gateway_id)

            else:

                # The gateway does not exist and is created ..
                insert = wrapper.create(name, opaque)
                _ = session.execute(insert)
                session.commit()

                # .. and read back to obtain its id.
                row = wrapper.get(name)
                gateway_id = row['id']
                out_created.append(gateway)

                logger.info('Created on-premises gateway %s with id %s', name, gateway_id)

            self.gateway_defs[name] = {
                'id': gateway_id,
                'name': name,
            }

        session.commit()

        # The database now reflects the declaration and the hub is updated accordingly.
        self.push_to_hub(session)

        return out_created, out_updated

# ################################################################################################################################

    def push_to_hub(self, session:'SASession') -> 'None':
        """ Requests the running server to publish the configuration to the hub. An unavailable
        server does not constitute an error because the startup service publishes the
        configuration when the server becomes available.
        """
        if not (server_dir := session.info.get(Session_Key_Server_Dir)):
            logger.info('No server directory in this session, not pushing to the on-premises gateway hub')
            return

        try:
            client = get_server_client(server_dir)
            response = client.invoke(_Sync_Service, {})

            if not response.ok:
                logger.warning('Could not push the on-premises gateways to the hub -> %s', response.details)

        except Exception as e:
            logger.warning('Could not push the on-premises gateways to the hub -> %s', e)

# ################################################################################################################################
# ################################################################################################################################
