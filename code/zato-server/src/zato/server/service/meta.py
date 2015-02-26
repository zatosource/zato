# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from inspect import getmodule, isclass
from itertools import chain
from logging import getLogger
from time import time
from traceback import format_exc

# Bunch
from bunch import bunchify

# SQLAlchemy
from sqlalchemy import Boolean, Integer

# Zato
from zato.common import NO_DEFAULT_VALUE, ZATO_NOT_GIVEN
from zato.common.odb.model import Base, Cluster
from zato.server.service import Bool as BoolSIO, Int as IntSIO
from zato.server.service.internal import AdminSIO

logger = getLogger(__name__)

singleton = object()

sa_to_sio = {
    Boolean: BoolSIO,
    Integer: IntSIO
}

req_resp = {
    'Create': 'create',
    'Edit': 'edit',
    'GetList': 'get_list',
    'Delete': 'delete',
    'Ping': 'ping',
}


def get_io(attrs, elems_name, is_edit, is_required, is_output, is_get_list, has_cluster_id):

    # This can be either a list or an SQLAlchemy object
    elems = attrs.get(elems_name) or []

    # Generate elems out of SQLAlchemy tables, including calls to ForceType's subclasses, such as Bool or Int.

    if elems and isclass(elems) and issubclass(elems, Base):
        columns = []
        for column in [elem for elem in elems._sa_class_manager.mapper.mapped_table.columns]:

            # Each model has a cluster_id column but it's not really needed for anything on output
            if column.name == 'cluster_id' and is_output:
                continue

            # We already have cluster_id and don't need a ForceType'd one.
            if column.name == 'cluster_id' and has_cluster_id:
                continue

            if column.name in attrs.skip_input_params:
                continue

            # We're building SimpleIO.input/output_required here so any nullable columns
            # should not be taken into account. They will be included the next time get_io
            # is called, i.e. to build SimpleIO.input/output_optional.
            if is_required and column.nullable:
                continue

            # We never return passwords
            if column.name == 'password' and is_get_list:
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
    attrs.initial_input = getattr(mod, 'initial_input', {})
    attrs.skip_input_params = getattr(mod, 'skip_input_params', [])
    attrs.skip_output_params = getattr(mod, 'skip_output_params', [])
    attrs.instance_hook = getattr(mod, 'instance_hook', None)
    attrs.response_hook = getattr(mod, 'response_hook', None)
    attrs.delete_hook = getattr(mod, 'delete_hook', None)
    attrs.broker_message_hook = getattr(mod, 'broker_message_hook', None)
    attrs.extra_delete_attrs = getattr(mod, 'extra_delete_attrs', [])
    attrs.input_required_extra = getattr(mod, 'input_required_extra', [])
    attrs.create_edit_input_required_extra = getattr(mod, 'create_edit_input_required_extra', [])
    attrs.create_edit_rewrite = getattr(mod, 'create_edit_rewrite', [])
    attrs.check_existing_one = getattr(mod, 'check_existing_one', True)

    default_value = getattr(mod, 'default_value', singleton)
    default_value = NO_DEFAULT_VALUE if default_value is singleton else default_value
    attrs.default_value = default_value

    attrs.is_edit = False
    attrs.is_create_edit = False

    if name == 'GetList':
        # get_sio sorts out what is required and what is optional.
        attrs.output_required = attrs.model
        attrs.output_optional = attrs.model
    else:

        attrs.broker_message = getattr(mod, 'broker_message')
        attrs.broker_message_prefix = getattr(mod, 'broker_message_prefix')

        if name in('Create', 'Edit'):
            attrs.input_required = attrs.model
            attrs.input_optional = attrs.model
            attrs.is_edit = name == 'Edit'
            attrs.is_create_edit = True

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
            input_required = sio['input_required'] + attrs['input_required_extra']

            for param in attrs['skip_input_params']:
                if param in input_required:
                    input_required.remove(param)

            input_optional = []
            output_required = sio['output_required'] + attrs['output_required_extra']
            output_optional = attrs['output_optional_extra']
            default_value = attrs.default_value

        for io in 'input', 'output':
            for req in 'required', 'optional':
                _name = '{}_{}'.format(io, req)

                is_required = 'required' in req
                is_output = 'output' in io
                is_get_list = name=='GetList'

                sio_elem = getattr(SimpleIO, _name)
                sio_elem.extend(get_io(attrs, _name, attrs.get('is_edit'), is_required, is_output, is_get_list, 'cluster_id' in sio_elem))

                if attrs.is_create_edit and is_required:
                    sio_elem.extend(attrs.create_edit_input_required_extra)

                # Sorts and removes duplicates
                setattr(SimpleIO, _name, sorted(list(set(sio_elem))))

        for skip_name in attrs.skip_output_params:
            for attr_names in chain([SimpleIO.output_required, SimpleIO.output_optional]):
                if skip_name in attr_names:
                    attr_names.remove(skip_name)

        return SimpleIO

class GetListMeta(AdminServiceMeta):
    """ A metaclass customizing the creation of services returning lists of objects.
    """
    def __init__(cls, name, bases, attrs):
        attrs = update_attrs(cls, name, attrs)
        cls.SimpleIO = GetListMeta.get_sio(attrs, name)
        cls.handle = GetListMeta.handle(attrs)
        cls.get_data = GetListMeta.get_data(attrs.get_data_func)
        return super(GetListMeta, cls).__init__(cls)

    @staticmethod
    def get_data(get_data_func):
        def get_data_impl(self, session):
            return get_data_func(session, self.request.input.cluster_id, False)
        return get_data_impl

    @staticmethod
    def handle(attrs):
        def handle_impl(self):
            with closing(self.odb.session()) as session:
                self.response.payload[:] = self.get_data(session)

            if attrs.response_hook:
                attrs.response_hook(self, self.request.input, None, attrs, 'get_list')

        return handle_impl

class CreateEditMeta(AdminServiceMeta):
    is_create = False
    output_required = ('id', 'name')

    def __init__(cls, name, bases, attrs):
        attrs = update_attrs(cls, name, attrs)
        cls.SimpleIO = CreateEditMeta.get_sio(attrs, name)
        cls.handle = CreateEditMeta.handle(attrs)
        return super(CreateEditMeta, cls).__init__(cls)

    @staticmethod
    def handle(attrs):
        def handle_impl(self):
            input = self.request.input
            input.update(attrs.initial_input)
            verb = 'edit' if attrs.is_edit else 'create'
            old_name = None

            with closing(self.odb.session()) as session:
                try:

                    if attrs.check_existing_one:

                        # Let's see if we already have an instance of that name before committing
                        # any stuff to the database. However, this is wrapped in an if condition
                        # because certain models don't have the .name attribute.
    
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

                    instance.fromdict(input, exclude=['password'], allow_pk=True)

                    # Now that we have an instance which is known not to be a duplicate
                    # we can possibly invoke a customization function before we commit
                    # anything to the database.
                    if attrs.instance_hook:
                        attrs.instance_hook(self, input, instance, attrs)

                    session.add(instance)
                    session.commit()

                except Exception, e:
                    msg = 'Could not {} the object, e:`%s`'.format(verb)
                    logger.error(msg, format_exc(e))
                    session.rollback()
                    raise
                else:

                    if attrs.def_needed:
                        def_ = session.query(attrs.def_needed).filter_by(id=input.def_id).one()
                        input.def_name = def_.name

                    action = getattr(attrs.broker_message, attrs.broker_message_prefix + verb.upper()).value
                    input.id = instance.id
                    input.action = action
                    input.old_name = old_name

                    if attrs.broker_message_hook:
                        attrs.broker_message_hook(self, input, instance, attrs, 'create_edit')

                    self.broker_client.publish(input)

                    for name in chain(attrs.create_edit_rewrite, self.SimpleIO.output_required):
                        value = getattr(instance, name, singleton)
                        if value is singleton:
                            value = input[name]

                        setattr(self.response.payload, name, value)

                    if attrs.response_hook:
                        attrs.response_hook(self, input, instance, attrs, 'create_edit')

        return handle_impl

class DeleteMeta(AdminServiceMeta):
    def __init__(cls, name, bases, attrs):
        attrs = update_attrs(cls, name, attrs)
        cls.SimpleIO = DeleteMeta.get_sio(attrs, name, ['id'], [])
        cls.handle = DeleteMeta.handle(attrs)
        return super(DeleteMeta, cls).__init__(cls)

    @staticmethod
    def handle(attrs):
        def handle_impl(self):
            with closing(self.odb.session()) as session:
                try:
                    instance = session.query(attrs.model).\
                        filter(attrs.model.id==self.request.input.id).\
                        one()

                    session.delete(instance)
                    #session.commit()
                except Exception, e:
                    msg = 'Could not delete {}, e:`%s`'.format(attrs.label)
                    self.logger.error(msg, format_exc(e))
                    session.rollback()

                    raise
                else:
                    self.request.input.action = getattr(attrs.broker_message, attrs.broker_message_prefix + 'DELETE').value
                    self.request.input.name = getattr(instance, 'name', ZATO_NOT_GIVEN)

                    for name in attrs.extra_delete_attrs:
                        self.request.input[name] = getattr(instance, name)

                    if attrs.broker_message_hook:
                        attrs.broker_message_hook(self, self.request.input, instance, attrs, 'delete')

                    self.logger.warn('ppp')
                    self.broker_client.publish(self.request.input)
                    self.logger.warn('aaa')

                    if attrs.delete_hook:
                        attrs.delete_hook(self, input, instance, attrs)

        return handle_impl

class PingMeta(AdminServiceMeta):
    def __init__(cls, name, bases, attrs):
        attrs = update_attrs(cls, name, attrs)
        cls.SimpleIO = PingMeta.get_sio(attrs, name, ['id'], ['info'])
        cls.handle = PingMeta.handle(attrs)
        return super(PingMeta, cls).__init__(cls)

    @staticmethod
    def handle(attrs):
        def handle_impl(self):
            with closing(self.odb.session()) as session:
                config = session.query(attrs.model).\
                    filter(attrs.model.id==self.request.input.id).\
                    one()

                start_time = time()
                self.ping(config)
                response_time = time() - start_time

                self.response.payload.info = 'Ping issued in {0:03.4f} s, check server logs for details, if any.'.format(
                    response_time)

        return handle_impl
