# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from inspect import getmodule, isclass
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
    'GetList': 'get_list',
    'Delete': 'delete'
}

def get_io(attrs, elems_name, is_edit, is_required):

    # This can be either a list or an SQLAlchemy object
    elems = attrs.get(elems_name) or []

    # Generate elems out of SQLAlchemy tables,
    # including calls to ForceType's subclasses, such as Bool or Int.

    if elems and isclass(elems) and issubclass(elems, Base):
        columns = []
        for column in [elem for elem in elems._sa_class_manager.mapper.mapped_table.columns]:

            # We're building SimpleIO.input/output_required here so any nullable columns
            # should not be taken into account. They will be included the next time get_io
            # is called, i.e. to build SimpleIO.input/output_optional.
            if is_required and column.nullable:
                continue

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

def update_attrs(cls, name, attrs):

    attrs = bunchify(attrs)
    mod = getmodule(cls)

    attrs.elem = getattr(mod, 'elem')
    attrs.label = getattr(mod, 'label')
    attrs.model = getattr(mod, 'model')
    attrs.output_required_extra = getattr(mod, 'output_required_extra', [])
    attrs.output_optional_extra = getattr(mod, 'output_optional_extra', [])
    attrs.get_data_func = getattr(mod, 'list_func')
    attrs.def_needed = getattr(mod, 'def_needed', False)

    if name == 'GetList':
        attrs.output_required = attrs.model
    else:

        attrs.broker_message = getattr(mod, 'broker_message')
        attrs.broker_message_prefix = getattr(mod, 'broker_message_prefix')

        if name in('Create', 'Edit'):
            attrs.input_required = attrs.model
            attrs.input_optional = attrs.model
            attrs.is_create_edit = True
            attrs.is_edit = name == 'Edit'

    return attrs

class AdminServiceMeta(type):

    @staticmethod
    def get_sio(attrs, name, input_required=None, output_required=None):

        sio = {
            'input_required': input_required or ['cluster_id'],
            'output_required': output_required if output_required is not None else ['id', 'name']
        }

        class SimpleIO(AdminSIO):
            request_elem = 'zato_{}_{}_request'.format(attrs.elem, req_resp[name])
            response_elem = 'zato_{}_{}_response'.format(attrs.elem, req_resp[name])
            input_required = sio['input_required']
            input_optional = []
            output_required = sio['output_required'] + attrs['output_required_extra']
            output_optional = attrs['output_optional_extra']

        for io in 'input', 'output':
            for req in 'required', 'optional':
                _name = '{}_{}'.format(io, req)
                getattr(SimpleIO, _name).extend(get_io(attrs, _name, attrs.get('is_edit'), 'required' in _name))

        return SimpleIO

    def init(cls, cls_meta, attrs, name):
        attrs = update_attrs(cls, name, attrs)
        cls.SimpleIO = cls_meta.get_sio(attrs, name)
        cls.get_data = cls_meta.get_data(attrs.get_data_func)
        cls.handle = cls_meta.handle()

        return cls

class GetListMeta(AdminServiceMeta):
    """ A metaclass customizing the creation of services returning lists of objects.
    """
    def __init__(cls, name, bases, attrs):
        cls = AdminServiceMeta.init(cls, GetListMeta, attrs, name)
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
        attrs = update_attrs(cls, name, attrs)
        cls.SimpleIO = CreateEditMeta.get_sio(attrs, name)
        cls.handle = CreateEditMeta.handle(attrs)

    @staticmethod
    def handle(attrs):
        def handle_impl(self):
            input = self.request.input
            verb = 'edit' if attrs.is_edit else 'create'
            old_name = None

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
                        old_name = instance.name
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

                    if attrs.def_needed:
                        def_ = session.query(attrs.def_needed).filter_by(id=input.def_id).one()
                        input.def_name = def_.name

                    action = getattr(attrs.broker_message, attrs.broker_message_prefix + verb.upper()).value
                    input.action = action
                    input.old_name = old_name
                    self.broker_client.publish(input)

                    self.response.payload.id = instance.id
                    self.response.payload.name = instance.name

        return handle_impl

class DeleteMeta(AdminServiceMeta):
    def __init__(cls, name, bases, attrs):
        attrs = update_attrs(cls, name, attrs)
        cls.SimpleIO = GetListMeta.get_sio(attrs, name, ['id'], [])
        cls.handle = DeleteMeta.handle(attrs)

        return super(DeleteMeta, cls).__init__(cls)

    @staticmethod
    def handle(attrs):
        def handle_impl(self):
            with closing(self.odb.session()) as session:
                try:
                    auth = session.query(attrs.model).\
                        filter(attrs.model.id==self.request.input.id).\
                        one()

                    session.delete(auth)
                    session.commit()
                except Exception, e:
                    msg = 'Could not delete {}, e:`%s`'.format(attrs.label)
                    self.logger.error(msg, format_exc(e))
                    session.rollback()

                    raise
                else:
                    self.request.input.action = getattr(attrs.broker_message, attrs.broker_message_prefix + 'DELETE').value
                    self.request.input.name = auth.name
                    self.broker_client.publish(self.request.input)

        return handle_impl
