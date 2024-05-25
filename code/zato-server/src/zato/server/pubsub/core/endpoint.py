# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import PUBSUB
from zato.common.typing_ import cast_
from zato.common.util.api import wait_for_dict_key
from zato.server.pubsub.model import Endpoint

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anytuple, callable_, dict_, intdict, intnone, strcalldict
    strcalldict = strcalldict

# ################################################################################################################################
# ################################################################################################################################

_pub_role = (PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id, PUBSUB.ROLE.PUBLISHER.id)
_sub_role = (PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id, PUBSUB.ROLE.SUBSCRIBER.id)

# ################################################################################################################################
# ################################################################################################################################

class EndpointAPI:

    endpoints:            'dict_[int, Endpoint]'
    endpoint_impl_getter: 'strcalldict'

    sec_id_to_endpoint_id:        'intdict'
    service_id_to_endpoint_id:    'intdict'
    ws_channel_id_to_endpoint_id: 'intdict'

    def __init__(self) -> 'None':

        # Endpoint ID -> Endpoint object
        self.endpoints = {}

        # Getter methods for each endpoint type that return actual endpoints,
        # e.g. REST outgoing connections. Values are set by worker store.
        self.endpoint_impl_getter = cast_('strcalldict', dict.fromkeys(PUBSUB.ENDPOINT_TYPE()))

        # Sec def ID -> Endpoint ID
        self.sec_id_to_endpoint_id = {}

        # Service ID -> Endpoint ID
        self.service_id_to_endpoint_id = {}

        # WS chan def ID -> Endpoint ID
        self.ws_channel_id_to_endpoint_id = {}

# ################################################################################################################################

    def get_by_id(self, endpoint_id:'int') -> 'Endpoint':
        return self.endpoints[endpoint_id]

# ################################################################################################################################

    def get_by_name(self, endpoint_name:'str') -> 'Endpoint':
        for endpoint in self.endpoints.values():
            if endpoint.name == endpoint_name:
                return endpoint
        else:
            raise KeyError('Could not find endpoint by name `{}` among `{}`'.format(endpoint_name, self.endpoints))

# ################################################################################################################################

    def get_by_ws_channel_id(self, ws_channel_id:'int') -> 'Endpoint':
        endpoint_id = self.ws_channel_id_to_endpoint_id[ws_channel_id]
        return self.endpoints[endpoint_id]

# ################################################################################################################################

    def get_id_by_sec_id(self, sec_id:'int') -> 'int':
        return self.sec_id_to_endpoint_id[sec_id]

# ################################################################################################################################

    def get_id_by_ws_channel_id(self, ws_channel_id:'int') -> 'intnone':
        wait_for_dict_key(self.ws_channel_id_to_endpoint_id, ws_channel_id, timeout=3)
        endpoint_id = self.ws_channel_id_to_endpoint_id.get(ws_channel_id)
        return endpoint_id

# ################################################################################################################################

    def get_id_by_service_id(self, service_id:'int') -> 'int':
        return self.service_id_to_endpoint_id[service_id]

# ################################################################################################################################

    def create(self, config:'anydict') -> 'None':

        endpoint_id   = config['id']
        security_id   = config['security_id']
        ws_channel_id = config.get('ws_channel_id')
        service_id    = config.get('service_id')

        self.endpoints[endpoint_id] = Endpoint(config)

        if security_id:
            self.sec_id_to_endpoint_id[security_id] = endpoint_id

        if ws_channel_id:
            self.ws_channel_id_to_endpoint_id[ws_channel_id] = endpoint_id

        if service_id:
            self.service_id_to_endpoint_id[service_id] = endpoint_id

# ################################################################################################################################

    def delete(self, endpoint_id:'int') -> 'None':

        del self.endpoints[endpoint_id]

        sec_id = None
        ws_chan_id = None
        service_id = None

        for key, value in self.sec_id_to_endpoint_id.items():
            if value == endpoint_id:
                sec_id = key
                break

        for key, value in self.ws_channel_id_to_endpoint_id.items():
            if value == endpoint_id:
                ws_chan_id = key
                break

        for key, value in self.service_id_to_endpoint_id.items():
            if value == endpoint_id:
                service_id = key
                break

        if sec_id:
            del self.sec_id_to_endpoint_id[sec_id]

        if ws_chan_id:
            del self.ws_channel_id_to_endpoint_id[ws_chan_id]

        if service_id:
            del self.service_id_to_endpoint_id[service_id]

# ################################################################################################################################

    def _is_allowed(
        self,
        *,
        target,        # type: str
        name,          # type: str
        is_pub,        # type: bool
        security_id,   # type: int
        ws_channel_id, # type: int
        endpoint_id=0, # type: int
        _pub_role=_pub_role, # type: anytuple
        _sub_role=_sub_role  # type: anytuple
    ) -> 'str | bool':
        """ An internal function that decides whether an endpoint, a security definition,
        or a WSX channel are allowed to publish or subscribe to topics.
        """

        if not endpoint_id:

            if not(security_id or ws_channel_id):
                raise ValueError(
                    'Either security_id or ws_channel_id must be given on input instead of `{}` `{}`'.format(
                    security_id, ws_channel_id))

            if security_id:
                source, id = self.sec_id_to_endpoint_id, security_id
            else:
                source, id = self.ws_channel_id_to_endpoint_id, ws_channel_id

            endpoint_id = source[id]

        # One way or another, we have an endpoint object now ..
        endpoint = self.endpoints[endpoint_id]

        # .. make sure this endpoint may publish or subscribe, depending on what is needed.
        if is_pub:
            if not endpoint.role in _pub_role:
                return False
        else:
            if not endpoint.role in _sub_role:
                return False

        # Alright, this endpoint has the correct role, but are there are any matching patterns for this topic?
        for orig, matcher in getattr(endpoint, target):
            if matcher.match(name):
                return orig
        else:
            return False

# ################################################################################################################################

    def is_allowed_pub_topic(self, *, name:'str', security_id:'int'=0, ws_channel_id:'int'=0) -> 'str | bool':
        return self._is_allowed(
            target='pub_topic_patterns',
            name=name,
            is_pub=True,
            security_id=security_id,
            ws_channel_id=ws_channel_id
        )

# ################################################################################################################################

    def is_allowed_pub_topic_by_endpoint_id(self, *, name:'str', endpoint_id:'int') -> 'str | bool':
        return self._is_allowed(
            target='pub_topic_patterns',
            name=name,
            is_pub=True,
            security_id=0,
            ws_channel_id=0,
            endpoint_id=endpoint_id
        )

# ################################################################################################################################

    def is_allowed_sub_topic(self, *, name:'str', security_id:'int'=0, ws_channel_id:'int'=0) -> 'str | bool':
        return self._is_allowed(
            target='sub_topic_patterns',
            name=name,
            is_pub=False,
            security_id=security_id,
            ws_channel_id=ws_channel_id
        )

# ################################################################################################################################

    def is_allowed_sub_topic_by_endpoint_id(self, name:'str', endpoint_id:'int') -> 'str | bool':
        return self._is_allowed(
            target='sub_topic_patterns',
            name=name,
            is_pub=False,
            security_id=0,
            ws_channel_id=0,
            endpoint_id=endpoint_id
        )

# ################################################################################################################################

    def get_impl_getter(self, endpoint_type:'str') -> 'callable_':
        return self.endpoint_impl_getter[endpoint_type]

# ################################################################################################################################

    def set_impl_getter(self, endpoint_type:'str', impl_getter:'callable_') -> 'None':
        self.endpoint_impl_getter[endpoint_type] = impl_getter

# ################################################################################################################################
# ################################################################################################################################
