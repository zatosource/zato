# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from inspect import isclass
from logging import basicConfig, getLogger

# Bunch
from bunch import bunchify

# SQLAlchemy
from sqlalchemy import Boolean, Integer

# Zato
from zato.common.odb.model import Base
from zato.server.service import Bool as BoolSIO, Int as IntSIO
from zato.server.service.internal import AdminSIO

logger = getLogger(__name__)

sa_to_sio = {
    Boolean: BoolSIO,
    Integer: IntSIO
}

def get_io(attrs, elems_name, is_edit):

    # This can be either a list or an SQLAlchemy object
    elems = attrs.get(elems_name) or []

    # Generate elems out of SQLAlchemy tables,
    # including calls to ForceType's subclasses, such as Bool or Int.

    if elems and isclass(elems) and issubclass(elems, Base):
        columns = []
        for column in [elem for elem in elems._sa_class_manager.mapper.mapped_table.columns]:

            if column.name == 'id':
                if is_edit:
                    pass
                else:
                    continue # Create or GetList

            for k, v in sa_to_sio.items():
                if isinstance(column.type, k):
                    columns.append(v(column.name))
                    break
            else:
                columns.append(column.name)

        # Override whatever objects it used to be
        elems = columns

    return elems

class AdminServiceMeta(type):

    @staticmethod
    def get_sio(attrs):

        # Base SIO class to be populated in subsequent steps.

        class SimpleIO(AdminSIO):
            request_elem = 'zato_{}_get_list_request'.format(attrs.elem)
            response_elem = 'zato_{}_get_list_response'.format(attrs.elem)
            input_required = ['cluster_id',]
            input_optional = []
            output_required = ['id', 'name']
            output_optional = []

        for io in 'input', 'output':
            for req in 'required', 'optional':
                name = '{}_{}'.format(io, req)
                getattr(SimpleIO, name).extend(get_io(attrs, name, attrs.get('is_edit')))

        return SimpleIO

class GetListMeta(AdminServiceMeta):
    """ A metaclass customizing the creation of services returning lists of objects.
    """
    def __init__(cls, name, bases, attrs):

        # Dynamically assign all the methods/attributes the new class needs

        attrs = bunchify(attrs)
        cls.SimpleIO = GetListMeta.get_sio(attrs)
        cls.get_data = GetListMeta.get_data(attrs.get_data_func)
        cls.handle = GetListMeta.handle()

        service_name = cls.get_name()
        service_name = service_name.split('.')[:-1]
        cls.name = '.'.join(service_name) + cls.convert_impl_name(name)

        return super(GetListMeta, cls).__init__(cls)

    @staticmethod
    def get_data(get_data_func):
        def get_data_impl(self, session):
            return get_data_func(session, self.request.input.cluster_id, False)
        return get_data_impl

    @staticmethod
    def handle():
        def handle_impl(self):
            with closing(self.odb.session()) as session:
                self.response.payload[:] = self.get_data(session)
        return handle_impl
