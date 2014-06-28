# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from inspect import isclass
from logging import getLogger
from traceback import format_exc

# Bunch
from bunch import bunchify

# SQLAlchemy
from sqlalchemy import Boolean, Integer

# Zato
from zato.common.odb.model import Base, Cluster
from zato.server.service import Bool as BoolSIO, Int as IntSIO
from zato.server.service.internal import AdminSIO

logger = getLogger(__name__)

sa_to_sio = {
    Boolean: BoolSIO,
    Integer: IntSIO
}

req_resp = {
    'Create': 'create',
    'Edit': 'edit',
    'GetList': 'get_list'
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
    def get_sio(attrs, name):

        # Base SIO class to be populated in subsequent steps.

        class SimpleIO(AdminSIO):
            request_elem = 'zato_{}_{}_request'.format(attrs.elem, req_resp[name])
            response_elem = 'zato_{}_{}_response'.format(attrs.elem, req_resp[name])
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
        cls.SimpleIO = GetListMeta.get_sio(attrs, name)
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

class CreateEditMeta(AdminServiceMeta):
    is_create = False
    output_required = ('id', 'name')

    def __init__(cls, name, bases, attrs):
        attrs = bunchify(attrs)
        cls.SimpleIO = CreateEditMeta.get_sio(attrs, name)
        cls.handle = CreateEditMeta.handle(attrs)

    @staticmethod
    def handle(attrs):
        def handle_impl(self):
            input = self.request.input
            verb = 'edit' if attrs.is_edit else 'create'

            with closing(self.odb.session()) as session:
                try:

                    # Let's see if we already have an instance of that name before committing
                    # any stuff to the database.

                    existing_one = session.query(attrs.model).\
                        filter(Cluster.id==input.cluster_id).\
                        filter(attrs.model.name==input.name)

                    if attrs.is_edit:
                        existing_one = existing_one.filter(attrs.model.id!=input.id)

                    existing_one = existing_one.first()

                    if existing_one and not attrs.is_edit:
                        raise Exception('{} [{}] already exists on this cluster'.format(
                            attrs.label[0].upper() + attrs.label[1:], input.name))

                    if attrs.is_edit:
                        instance = session.query(attrs.model).filter_by(id=input.id).one()
                    else:
                        instance = attrs.model()

                    instance.fromdict(input, allow_pk=True)

                    session.add(instance)
                    session.commit()

                except Exception, e:
                    msg = 'Could not {} a namespace, e:`%s`'.format(verb)
                    self.logger.error(msg, format_exc(e))
                    session.rollback()
                    raise
                else:
                    action = getattr(attrs.broker_message, attrs.broker_message_prefix + verb.upper())
                    input.action = action
                    self.broker_client.publish(input)

                    self.response.payload.id = instance.id
                    self.response.payload.name = instance.name

        return handle_impl