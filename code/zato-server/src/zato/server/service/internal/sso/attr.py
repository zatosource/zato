# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.server.service import AsIs, Bool, Int, Opaque
from zato.server.service.internal.sso import BaseRESTService, BaseSIO
from zato.sso.api import status_code, ValidationError

# ################################################################################################################################

_invalid = 'invalid.{}'.format(uuid4().hex)

# ################################################################################################################################

class _DataElem:
    def __init__(self, func, elem_name, elem_value):
        self.func = func
        self.elem_name = elem_name
        self.elem_value = elem_value

# ################################################################################################################################

class _AttrBase:
    """ Utility base class for attribute-related services.
    """
    _api_entity = None

    class SimpleIO(BaseSIO):
        input_required = 'current_app',
        input_optional = 'ust', 'current_ust', AsIs('user_id'), 'name', 'value', Opaque('data'), Bool('decrypt'), \
            Bool('serialize_dt'), Int('expiration'), Bool('encrypt'), 'target_ust'
        output_optional = BaseSIO.output_optional + (Bool('found'), 'result', 'name', 'value', 'creation_time',
            'last_modified', 'expiration_time', 'is_encrypted')
        default_value = _invalid

# ################################################################################################################################

    def get_api_call_data(self, cid, ctx, api_name, logger, needs_input):

        if needs_input:
            if ctx.input.name != _invalid:
                func_name = api_name
                data_elem_name = 'name'
                data_elem_value = ctx.input.name
            elif ctx.input.data != _invalid:
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

        if self._api_entity == 'user':
            entity = self.sso.user.get_user_by_id(cid, ctx.input.user_id, ctx.input.ust, ctx.input.current_app,
                ctx.remote_addr)
        elif self._api_entity == 'session':
            entity = self.sso.user.session.get(self.cid, ctx.input.target_ust, ctx.input.current_ust,
                ctx.input.current_app, ctx.remote_addr, user_agent=None)
        else:
            logger.warning('Could not establish API entity to use out of `%s`', self._api_entity)
            raise ValidationError(status_code.common.internal_error)

        func = getattr(entity.attr, func_name)
        return _DataElem(func, data_elem_name, data_elem_value)

# ################################################################################################################################

    def _access_sso_attr(self, ctx, api_name, needs_encrypt=True, needs_expiration=True, needs_result=False, needs_input=True,
        force_elem_name_data=False):
        """ A common function for most calls accessing attributes.
        """
        call_data = self.get_api_call_data(self.cid, ctx, api_name, self.logger, needs_input)

        if force_elem_name_data:
            elem_name = 'data'
        else:
            elem_name = call_data.elem_name

        kwargs = {
            elem_name: call_data.elem_value,
        }

        if needs_expiration:
            kwargs['expiration'] = ctx.input.expiration if ctx.input.expiration != _invalid else None

        if needs_encrypt:
            kwargs['encrypt'] = ctx.input.encrypt if ctx.input.encrypt != _invalid else False

        if elem_name == 'name':
            kwargs['value'] = ctx.input.value

        try:
            result = call_data.func(**(kwargs if needs_input else {}))
        except Exception as e:
            self.logger.warning(format_exc())
            if isinstance(e, ValidationError):
                raise
            else:
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
        self._access_sso_attr(ctx, 'delete', False, False, force_elem_name_data=True)

# ################################################################################################################################

    def _handle_sso_GET(self, ctx):
        """ Returns data of and metadata about an attribute.
        """
        call_data = self.get_api_call_data(self.cid, ctx, 'get', self.logger, True)
        decrypt = ctx.input.decrypt
        decrypt = True if (decrypt == _invalid or decrypt == '') else ctx.input.decrypt

        kwargs = {
            'decrypt': decrypt,
            'serialize_dt':True,
            'data': call_data.elem_value,
        }

        try:
            result = call_data.func(**kwargs)
        except Exception:
            self.logger.warning(format_exc())
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
        self._access_sso_attr(ctx, 'exists', False, False, True, force_elem_name_data=True)

# ################################################################################################################################

class _AttrNames(_AttrBase, BaseRESTService):
    """ Returns names of all attributes defined.
    """
    def _handle_sso_GET(self, ctx):
        self._access_sso_attr(ctx, 'names', False, False, True, False, force_elem_name_data=True)

# ################################################################################################################################
