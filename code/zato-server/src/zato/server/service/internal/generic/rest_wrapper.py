# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.broker_message import OUTGOING
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

def _replace_suffix_from_dict_name(data:'stranydict', wrapper_type:'str') -> 'str':
    _prefix = wrapper_type + '.'
    _name = data['name'] # type: str
    _name = _name.replace(_prefix, '', 1)
    return _name

# ################################################################################################################################
# ################################################################################################################################

class GetList(Service):

    name = 'zato.generic.rest-wrapper.get-list'

    def handle(self) -> 'None':

        # Reusable
        wrapper_type = ''

        # Our response to produce
        out = []

        # Our service to invoke
        service_name = 'zato.http-soap.get-list'

        # Filter by this wrapper type from input
        if isinstance(self.request.raw_request, dict):
            wrapper_type = self.request.raw_request.get('wrapper_type', '') # type: str

        import logging
        logger = logging.getLogger(__name__)

        # This response has all the REST connections possible ..
        response = self.invoke(service_name, {
            'include_wrapper': True,
            'cluster_id': self.server.cluster_id,
            'connection': CONNECTION.OUTGOING,
            'transport': URL_TYPE.PLAIN_HTTP,
            'paginate': False,
        })

        logger.info('rest-wrapper.get-list -> response type:%s, value:%s', type(response).__name__, response)

        # .. extract the list of items ..
        items = response.get('data', response) if isinstance(response, dict) else response

        logger.info('rest-wrapper.get-list -> items type:%s, len:%s', type(items).__name__, len(items) if hasattr(items, '__len__') else '?')

        # .. iterate through each of them ..
        for item in items:

            logger.info('rest-wrapper.get-list -> item is_wrapper:%s, wrapper_type:%s, name:%s',
                item.get('is_wrapper'), item.get('wrapper_type'), item.get('name'))

            # .. ignore items that are not wrappers ..
            if not item.get('is_wrapper'):
                continue

            # .. reusable ..
            item_wrapper_type = item.get('wrapper_type') or ''

            # .. ignore wrappers of a type other than what was requested ..
            if wrapper_type:
                if wrapper_type != item_wrapper_type:
                    continue

            # .. enmasse will not send any wrapper type which is why we use the name from the item here ..
            suffix_wrapper_type = wrapper_type or item_wrapper_type

            # .. replace the name prefix ..
            item['name'] = _replace_suffix_from_dict_name(item, suffix_wrapper_type)

            # .. and append the item to the result ..
            out.append(item)

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class _WrapperBase(Service):

    _wrapper_impl_suffix = None
    _uses_name = False

    # SimpleIO
    output = '-id', '-name', '-info', '-is_success'

# ################################################################################################################################

    def _handle(self, initial:'stranydict') -> 'None':

        # Our service to invoke
        service_name = 'zato.http-soap.' + self._wrapper_impl_suffix # type: ignore

        # Base request to create a new wrapper ..
        request = {
            'is_wrapper': True,
            'cluster_id': self.server.cluster_id,
            'connection': CONNECTION.OUTGOING,
            'transport': URL_TYPE.PLAIN_HTTP,
            'url_path': r'{_zato_path}'
        }

        # .. extend it with our own extra input ..
        request.update(initial)

        # .. prepend a prefix to the name given that this is a wrapper ..
        # .. but note that the Delete action does not use a name so this block is optional ..
        if self._uses_name:
            _orig_name    = request['name']
            _name         = _orig_name
            _wrapper_type = request.get('wrapper_type')
            if _wrapper_type:
                name = f'{_wrapper_type}.{_name}'
            else:
                name = _name
            request['name'] = name

        # .. and send it to the service.
        response = self.invoke(service_name, request)

        # This is used by Create and Edit actions
        if self._uses_name:
            self.response.payload.name = _orig_name # type: ignore

        # These are optional as well
        self.response.payload.id   = response.get('id')
        self.response.payload.info = response.get('info')
        self.response.payload.is_success = response.get('is_success')

# ################################################################################################################################

    def handle(self):
        self._handle(self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################

class Create(_WrapperBase):
    name = 'zato.generic.rest-wrapper.create'
    _wrapper_impl_suffix = 'create'
    _uses_name = True

# ################################################################################################################################
# ################################################################################################################################

class Edit(_WrapperBase):
    name = 'zato.generic.rest-wrapper.edit'
    _wrapper_impl_suffix = 'edit'
    _uses_name = True

# ################################################################################################################################
# ################################################################################################################################

class Delete(_WrapperBase):
    name = 'zato.generic.rest-wrapper.delete'
    _wrapper_impl_suffix = 'delete'
    _uses_name = False

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(_WrapperBase):
    name = 'zato.generic.rest-wrapper.change-password'
    _wrapper_impl_suffix = 'edit'
    _uses_name = False

    def handle(self) -> 'None':

        request = self.request.raw_request
        id = request['id']

        password = request.get('password') or ''
        password = self.server.encrypt(password)

        # Update via the ConfigStore
        outconn_list = self.server.config_manager.get_list('outgoing_rest')
        for item in outconn_list:
            if item.get('id') == id:
                item['password'] = password
                self.server.config_manager.set('outgoing_rest', item['name'], item)
                break

        # Notify all the members of the cluster of the change
        self.broker_client.publish({
            'action': OUTGOING.REST_WRAPPER_CHANGE_PASSWORD.value,
            'id': id,
            'password': password,
        })

# ################################################################################################################################
# ################################################################################################################################

class Ping(_WrapperBase):
    name = 'zato.generic.rest-wrapper.ping'
    _wrapper_impl_suffix = 'ping'
    _uses_name = False

# ################################################################################################################################
# ################################################################################################################################
