# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc

# Zato
from zato.server.service import AsIs, Bool, Int, Opaque
from zato.server.service.internal.sso import BaseRESTService, BaseSIO
from zato.sso.api import status_code, ValidationError

# ################################################################################################################################

_invalid = object()

# ################################################################################################################################

class _DataElem(object):
    def __init__(self, func, elem_name, elem_value):
        self.func = func
        self.elem_name = elem_name
        self.elem_value = elem_value

# ################################################################################################################################

class _AttrBase(object):
    """ Utility base class for attribute-related services.
    """
    _result_elem = None

    class SimpleIO(BaseSIO):
        input_required = ('ust', 'current_app')
        input_optional = (AsIs('user_id'), 'name', 'value', Opaque('data'), Bool('decrypt'), Bool('serialize_dt'),
            Int('expiration'), Bool('encrypt'))
        output_optional = BaseSIO.output_optional + (Bool('found'), 'result', 'name', 'value', 'creation_time',
            'last_modified', 'expiration_time', 'is_encrypted')
        default_value = _invalid

# ################################################################################################################################

    def get_api_call_data(self, cid, ctx, api_name, logger, needs_input):

        if needs_input:
            if ctx.input.name is not _invalid:
                func_name = api_name
                data_elem_name = 'name'
                data_elem_value = ctx.input.name
            elif ctx.input.data is not _invalid:
                func_name = '{}_many'.format(api_name)
                data_elem_name = 'data'
                data_elem_value = ctx.input.data
            else:
                logger.info('Could not find input in `name` nor `data`')
                raise ValidationError(status_code.common.invalid_input)
        else:
            func_name = api_name
            data_elem_name = None
            data_elem_value = None

        user = self.sso.user.get_user_by_id(cid, ctx.input.user_id, ctx.input.ust, ctx.input.current_app, ctx.remote_addr)
        func = getattr(user.attr, func_name)
        return _DataElem(func, data_elem_name, data_elem_value)

# ################################################################################################################################

    def _access_sso_attr(self, ctx, api_name, needs_encrypt=True, needs_expiration=True, needs_result=False, needs_input=True):
        """ A common function for most calls accessing attributes.
        """
        call_data = self.get_api_call_data(self.cid, ctx, api_name, self.logger, needs_input)

        kwargs = {
            call_data.elem_name: call_data.elem_value,
        }

        if needs_expiration:
            kwargs['expiration'] = ctx.input.expiration if ctx.input.expiration is not _invalid else None

        if needs_encrypt:
            kwargs['encrypt'] = ctx.input.encrypt if ctx.input.encrypt is not _invalid else False

        if call_data.elem_name == 'name':
            kwargs['value'] = ctx.input.value

        try:
            result = call_data.func(**(kwargs if needs_input else {}))
        except Exception:
            self.logger.warn(format_exc())
            raise ValidationError(status_code.common.invalid_input)
        else:
            if needs_result:
                self.response.payload.result = result

# ################################################################################################################################

class _Attr(_AttrBase, BaseRESTService):
    """ Handles access to most of attribute-related REST APIs.
    """

# ################################################################################################################################

    def _handle_sso_POST(self, ctx):
        """ Creates a new attribute.
        """
        self._access_sso_attr(ctx, 'create')

# ################################################################################################################################

    def _handle_sso_PATCH(self, ctx):
        """ Updates an existing attribute.
        """
        self._access_sso_attr(ctx, 'update')

# ################################################################################################################################

    def _handle_sso_PUT(self, ctx):
        """ Creates a new or updates an existing attribute.
        """
        self._access_sso_attr(ctx, 'set')

# ################################################################################################################################

    def _handle_sso_DELETE(self, ctx):
        """ Deletes an existing attribute.
        """
        self._access_sso_attr(ctx, 'delete', False, False)

# ################################################################################################################################

    def _handle_sso_GET(self, ctx):
        """ Returns data of and metadata about an attribute.
        """
        call_data = self.get_api_call_data(self.cid, ctx, 'get', self.logger, True)
        decrypt = ctx.input.decrypt
        decrypt = True if (decrypt is _invalid or decrypt == '') else ctx.input.decrypt

        kwargs = {
            'decrypt': decrypt,
            'serialize_dt':True,
            'data': call_data.elem_value,
        }

        try:
            result = call_data.func(**kwargs)
        except Exception:
            self.logger.warn(format_exc())
            raise ValidationError(status_code.common.invalid_input)
        else:
            if result:
                if isinstance(result, list):
                    self.response.payload.result = result
                else:
                    result = result.to_dict()
                    self.response.payload.found = True
                    self.response.payload.name = result['name']
                    self.response.payload.value = result['value']
                    self.response.payload.creation_time = result['creation_time']
                    self.response.payload.last_modified = result['last_modified']
                    self.response.payload.expiration_time = result['expiration_time']
                    self.response.payload.is_encrypted = result['is_encrypted']
            else:
                self.response.payload.found = False

# ################################################################################################################################

class _AttrExists(_AttrBase, BaseRESTService):
    """ Checks if an attribute or attributes given on input actually exist(s).
    """
    def _handle_sso_GET(self, ctx):
        self._access_sso_attr(ctx, 'exists', False, False, True)

# ################################################################################################################################

class _AttrNames(_AttrBase, BaseRESTService):
    """ Returns names of all attributes defined.
    """
    def _handle_sso_GET(self, ctx):
        self._access_sso_attr(ctx, 'names', False, False, True, False)

# ################################################################################################################################
