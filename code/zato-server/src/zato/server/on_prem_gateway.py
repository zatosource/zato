# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import closing
from logging import getLogger

# requests
import requests

# Zato
from zato.common.api import On_Prem_Gateway
from zato.common.json_internal import dumps
from zato.common.odb.model import GenericObject as ModelGenericObject
from zato.common.odb.query.generic import OnPremGatewayWrapper
from zato.common.typing_ import cast_
from zato.common.util.sql import get_dict_with_opaque

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict, strdictlist, strdictnone, strlist, strnone
    from zato.server.base.parallel import ParallelServer

    # Dummy assignments to satisfy type checkers
    strdictlist = strdictlist
    strdictnone = strdictnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# The time allowed for the hub to respond.
_Hub_Timeout = 10

# The host of the hub's administrative API.
_Hub_Host = '127.0.0.1'

# The port of the TLS load balancer that on-premises gateways connect to.
_Public_Port_Env = 'Zato_Port_Load_Balancer_SSL'

# The permitted range of port numbers.
_Port_Min = 1
_Port_Max = 65535

# Whether the hub responded to the previous call. An outage is reported once rather than
# on each subsequent call.
_hub_was_reachable = True

# ################################################################################################################################
# ################################################################################################################################

def _report_hub_outage(e:'Exception') -> 'None':
    """ Logs a hub outage once, at its onset.
    """
    global _hub_was_reachable

    if _hub_was_reachable:
        logger.warning('Could not reach the on-premises gateway hub: %s', e)
        _hub_was_reachable = False

# ################################################################################################################################

def _report_hub_available() -> 'None':
    """ Logs the conclusion of a hub outage once.
    """
    global _hub_was_reachable

    if not _hub_was_reachable:
        logger.info('The on-premises gateway hub is reachable again')
        _hub_was_reachable = True

# ################################################################################################################################
# ################################################################################################################################

def _get_unknown_state() -> 'strdict':
    """ The state reported for a gateway while the hub is unavailable, in which case its
    configuration is known and its runtime state is not.
    """
    out = {
        'is_connected': False,
        'has_key': False,
        'key_fingerprint': '',
        'connected_since': '',
        'remote_address': '',
        'gateway_version': '',
        'platform': '',
        'session_count': 0,
        'loopback': [],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_hub_admin_url() -> 'str':
    """ The base URL of the hub's admin API.
    """
    port = os.environ.get(On_Prem_Gateway.Env.Admin_Port)

    if not port:
        port = On_Prem_Gateway.Port.Admin

    out = f'http://{_Hub_Host}:{port}'

    return out

# ################################################################################################################################

def get_public_address(host:'strnone'=None) -> 'str':
    """ The address that an on-premises gateway connects to.
    """

    # An explicit setting takes precedence ..
    address = os.environ.get(On_Prem_Gateway.Env.Public_Address)

    if address:
        out = address.strip()
        return out

    # .. otherwise the address is derived from the request host ..
    if not host:
        raise Exception(f'Set {On_Prem_Gateway.Env.Public_Address} to the address gateways are to connect to')

    # .. the Dashboard uses a separate port, so only the host part is retained ..
    host = host.strip()

    if ':' in host:
        host = host.split(':')[0]

    # .. the Docker image always defines the port of its TLS load balancer, which forwards
    # .. gateway connections to the hub ..
    if port := os.environ.get(_Public_Port_Env):
        out = f'https://{host}:{port}'

    # .. whereas an environment without it has no load balancer, so gateways connect
    # .. to the hub directly.
    else:
        port = os.environ.get(On_Prem_Gateway.Env.Hub_Port)

        if not port:
            port = On_Prem_Gateway.Port.Hub

        out = f'http://{host}:{port}'

    return out

# ################################################################################################################################

def parse_hosts(hosts:'strlist') -> 'strlist':
    """ Validates the addresses supplied and returns them as a list of host:port entries.
    """

    # Local variables
    out:'strlist' = []
    seen = set()

    # Each entry is required to be the address of an on-premises system ..
    for item in hosts:

        item = item.strip()

        if not item:
            continue

        if ':' not in item:
            raise Exception(f'`{item}` is not in the host:port format')

        host, _, port = item.rpartition(':')
        host = host.strip()
        port = port.strip()

        if not host:
            raise Exception(f'`{item}` has no host')

        if not port.isdigit():
            raise Exception(f'`{item}` has no numeric port')

        port_number = int(port)

        is_port_too_low = port_number < _Port_Min
        is_port_too_high = port_number > _Port_Max

        if is_port_too_low or is_port_too_high:
            raise Exception(f'`{item}` has a port outside the {_Port_Min}-{_Port_Max} range')

        item = f'{host}:{port_number}'

        # .. each address designates a single endpoint, so duplicates are rejected ..
        if item in seen:
            raise Exception(f'`{item}` is listed more than once')

        seen.add(item)
        out.append(item)

    # .. and the result is sorted so that identical input yields an identical list.
    out = sorted(out)

    return out

# ################################################################################################################################
# ################################################################################################################################

class HubClient:
    """ The client of the gateway hub's administrative API.
    """

    def __init__(self, base_url:'str') -> 'None':
        self.base_url = base_url

# ################################################################################################################################

    def _invoke(self, method:'str', path:'str', data:'strdictnone'=None) -> 'strdict':
        """ Invokes the hub and reports any failure as a message suitable for display.
        """
        url = f'{self.base_url}{path}'

        try:
            response = requests.request(method, url, json=data, timeout=_Hub_Timeout)
        except requests.exceptions.RequestException as e:
            raise Exception(f'The on-premises gateway hub is not responding ({e})')

        try:
            payload = response.json()
        except ValueError:
            raise Exception(f'The on-premises gateway hub returned a response that is not JSON ({response.text})')

        if not response.ok:

            error = payload.get('error')

            if not error:
                error = response.text

            raise Exception(f'The on-premises gateway hub refused the request - {error}')

        out = cast_('strdict', payload)

        return out

# ################################################################################################################################

    def ping(self) -> 'bool':
        """ Indicates whether the hub is available.
        """
        try:
            _ = self._invoke('GET', '/ping')
        except Exception:
            return False

        return True

# ################################################################################################################################

    def get_gateways(self) -> 'strdictlist':
        """ The runtime state of every gateway registered with the hub.
        """
        response = self._invoke('GET', '/gateways')
        gateways = response['gateways']

        out = cast_('strdictlist', gateways)

        return out

# ################################################################################################################################

    def put_gateways(self, gateways:'strdictlist') -> 'None':
        """ Replaces the hub's configuration with the one supplied.
        """
        data = {'gateways': gateways}

        _ = self._invoke('PUT', '/gateways', data)

# ################################################################################################################################

    def mint_token(self, name:'str', address:'str') -> 'strdict':
        """ Issues a single-use enrollment token for one gateway.
        """
        path = f'/gateways/{name}/enrollment-token'
        data = {'address': address}

        out = self._invoke('POST', path, data)

        return out

# ################################################################################################################################

    def reset_key(self, name:'str') -> 'None':
        """ Revokes a gateway's key.
        """
        path = f'/gateways/{name}/key'

        _ = self._invoke('DELETE', path)

# ################################################################################################################################
# ################################################################################################################################

class OnPremGatewayManager:
    """ Stores on-premises gateways in the ODB and synchronizes the hub with them. The ODB
    stores the name, the flags and the list of addresses, the hub stores the key.
    """

    def __init__(self, server:'ParallelServer', session:'any_'=None) -> 'None':

        hub_admin_url = get_hub_admin_url()

        self.server = server
        self.cluster_id = server.cluster_id
        self.hub = HubClient(hub_admin_url)

        if session:
            self.session = session
        else:
            self.session = self.server.odb.session

# ################################################################################################################################

    def get_list(self) -> 'strdictlist':
        """ The configuration of every gateway, excluding its runtime state.
        """
        with closing(self.session()) as session:
            wrapper = OnPremGatewayWrapper(session, self.cluster_id)
            out = wrapper.get_list()

        return out

# ################################################################################################################################

    def get(self, name:'str') -> 'strdictnone':
        """ A single gateway by name, or None if no such gateway exists.
        """
        with closing(self.session()) as session:

            wrapper = OnPremGatewayWrapper(session, self.cluster_id)
            row = wrapper.get(name)

            if row is None:
                return None

            row = cast_('strdict', row)
            out = wrapper.build_list_item_from_sql_row(row)

        return out

# ################################################################################################################################

    def get_by_id(self, id:'int') -> 'strdictnone':
        """ A single gateway by ID, or None if no such gateway exists.
        """
        with closing(self.session()) as session:

            row = session.query(ModelGenericObject).\
                filter(ModelGenericObject.id==id).\
                filter(ModelGenericObject.type_==On_Prem_Gateway.Type.On_Prem_Gateway).\
                filter(ModelGenericObject.cluster_id==self.cluster_id).\
                first()

            if row is None:
                return None

            row_with_opaque = get_dict_with_opaque(row)
            row = cast_('strdict', row_with_opaque)

            wrapper = OnPremGatewayWrapper(session, self.cluster_id)
            out = wrapper.build_list_item_from_sql_row(row)

        return out

# ################################################################################################################################

    def create(self, name:'str', is_active:'bool', hosts:'strlist', is_key_reset_required:'bool') -> 'int':
        """ Creates a gateway and returns its ID.
        """
        data = {'is_active': is_active, 'hosts': hosts, 'is_key_reset_required': is_key_reset_required}
        opaque = dumps(data)

        with closing(self.session()) as session:

            wrapper = OnPremGatewayWrapper(session, self.cluster_id)

            insert = wrapper.create(name, opaque)
            session.execute(insert)
            session.commit()

            # The ID is assigned by the database, hence the row is read back to obtain it.
            created = wrapper.get(name)

        created = cast_('strdict', created)
        out = created['id']

        return cast_('int', out)

# ################################################################################################################################

    def edit(self, id:'int', name:'str', is_active:'bool', hosts:'strlist', is_key_reset_required:'bool') -> 'None':
        """ Updates a gateway, including a change of its name.
        """
        data = {'is_active': is_active, 'hosts': hosts, 'is_key_reset_required': is_key_reset_required}
        opaque = dumps(data)

        with closing(self.session()) as session:

            wrapper = OnPremGatewayWrapper(session, self.cluster_id)

            update = wrapper.update(name, opaque, id=id)
            session.execute(update)
            session.commit()

# ################################################################################################################################

    def delete(self, id:'int') -> 'None':
        """ Deletes a gateway by its ID.
        """
        with closing(self.session()) as session:

            wrapper = OnPremGatewayWrapper(session, self.cluster_id)

            delete = wrapper.delete_by_id(id)
            session.execute(delete)
            session.commit()

# ################################################################################################################################

    def sync(self) -> 'None':
        """ Publishes the complete configuration to the hub. An unavailable hub does not
        constitute an error because the configuration is retained in the ODB and the startup
        service publishes it when the hub becomes available.
        """
        gateways = []

        for item in self.get_list():
            gateways.append({
                'name': item['name'],
                'is_active': item['is_active'],
                'hosts': item['hosts'],
                'is_key_reset_required': item['is_key_reset_required'],
            })

        try:
            self.hub.put_gateways(gateways)
        except Exception as e:
            _report_hub_outage(e)
            return

        _report_hub_available()

        gateway_count = len(gateways)

        logger.info('Pushed %d on-premises gateway(s) to the hub', gateway_count)

# ################################################################################################################################

    def get_status_list(self) -> 'strdictlist':
        """ The configuration of every gateway, merged with its runtime state from the hub.
        The runtime state is reported as unknown while the hub is unavailable.
        """

        # Local variables
        out:'strdictlist' = []
        by_name:'strdict' = {}
        hub_error = ''

        # The runtime state from the hub, if it is available ..
        try:
            for item in self.hub.get_gateways():
                by_name[item['name']] = item
        except Exception as e:
            hub_error = str(e)
            _report_hub_outage(e)
        else:
            _report_hub_available()

        # .. merged with the ODB configuration, in which a gateway is defined before
        # it connects for the first time.
        for item in self.get_list():

            hosts = item['hosts']
            host_count = len(hosts)

            gateway = {
                'id': item['id'],
                'name': item['name'],
                'is_active': item['is_active'],
                'hosts': hosts,
                'host_count': host_count,
                'is_key_reset_required': item['is_key_reset_required'],
                'hub_error': hub_error,
            }

            state = by_name.get(item['name'])

            if state is None:
                gateway.update(_get_unknown_state())
            else:
                gateway['is_connected'] = state['is_connected']
                gateway['has_key'] = state['has_key']
                gateway['key_fingerprint'] = state['key_fingerprint']
                gateway['connected_since'] = state['connected_since']
                gateway['remote_address'] = state['remote_address']
                gateway['gateway_version'] = state['gateway_version']
                gateway['platform'] = state['platform']
                gateway['session_count'] = state['session_count']
                gateway['loopback'] = state['loopback']

            out.append(gateway)

        return out

# ################################################################################################################################
# ################################################################################################################################
