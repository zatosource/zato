# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from json import dumps

# Zato
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import HTTPSOAP
from zato.common.util.sql import parse_instance_opaque_attr, set_instance_opaque_attrs
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

        # This response has all the REST connections possible ..
        response = self.invoke(service_name, {
            'cluster_id': self.server.cluster_id,
            'connection': CONNECTION.OUTGOING,
            'transport': URL_TYPE.PLAIN_HTTP,
            'paginate': False,
        }, skip_response_elem=True)

        # .. iterate through each of them ..
        for item in response:

            if wrapper_type:
                if item.get('wrapper_type') != wrapper_type:
                    continue

            # .. replace the name prefix ..
            item['name'] = _replace_suffix_from_dict_name(item, wrapper_type)

            # .. and append the item to the result ..
            out.append(item)

        self.response.payload = dumps(out)

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
            _wrapper_type = request['wrapper_type']
            request['name'] = f'{_wrapper_type }.{_name}'

        # .. and send it to the service.
        response = self.invoke(service_name, request, skip_response_elem=True)

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
    response_elem = None
    _wrapper_impl_suffix = 'create'
    _uses_name = True

# ################################################################################################################################
# ################################################################################################################################

class Edit(_WrapperBase):
    name = 'zato.generic.rest-wrapper.edit'
    response_elem = None
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

    def handle(self):

        # Reusable
        request = self.request.raw_request

        # This must always exist
        id = request['id']

        # This is optional
        password = request.get('password') or request.get('password1') or ''
        password = self.server.encrypt(password)

        with closing(self.odb.session()) as session:

            item = session.query(HTTPSOAP).filter_by(id=id).one()

            opaque = parse_instance_opaque_attr(item)
            opaque['password'] = password

            set_instance_opaque_attrs(item, opaque)

            session.add(item)
            session.commit()

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
