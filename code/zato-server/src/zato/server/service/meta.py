# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from inspect import getmodule, isclass
from itertools import chain
from json import dumps
from logging import getLogger
from time import time
from traceback import format_exc

# Bunch
from bunch import bunchify

# SQLAlchemy
from sqlalchemy import Boolean, Integer
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.api import ZATO_NOT_GIVEN
from zato.common.odb.model import Base, Cluster
from zato.common.util.api import parse_literal_dict
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.connection.http_soap import BadRequest
from zato.server.service import AsIs, Bool as BoolSIO, Int as IntSIO
from zato.server.service.internal import AdminSIO, GetListAdminSIO

# ################################################################################################################################

# Type checking
if 0:
    from zato.server.service import Service

    # For pyflakes
    Service = Service

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

singleton = object()

# ################################################################################################################################

sa_to_sio = {
    Boolean: BoolSIO,
    Integer: IntSIO
}

# ################################################################################################################################

req_resp = {
    'Create': 'create',
    'Edit': 'edit',
    'GetList': 'get_list',
    'Delete': 'delete',
    'Ping': 'ping',
}

# ################################################################################################################################

def _is_column_required(column):
    return not (bool(column.nullable) is True)

# ################################################################################################################################

def get_columns_to_visit(columns, is_required):
    out = []

    # Models with inheritance may have multiple attributes of the same name,
    # e.g. VaultConnection.id will have SecBase.id and we need to make sure only one of them is returned.
    names_seen = set()

    for elem in columns:
        if is_required:
            if not _is_column_required(elem):
                continue
        else:
            if _is_column_required(elem):
                continue

        if elem.name not in names_seen:
            names_seen.add(elem.name)
            out.append(elem)
        else:
            continue

    return out

# ################################################################################################################################

def get_io(attrs, elems_name, is_edit, is_required, is_output, is_get_list, has_cluster_id):

    # This can be either a list or an SQLAlchemy object
    elems = attrs.get(elems_name) or []
    columns = []

    # Generate elems out of SQLAlchemy tables, including calls to SIOElem's subclasses, such as Bool or Int.

    if elems and isclass(elems) and issubclass(elems, Base):

        columns_to_visit = [elem for elem in elems._sa_class_manager.mapper.mapped_table.columns]
        columns_to_visit = get_columns_to_visit(columns_to_visit, is_required)

        for column in columns_to_visit:

            # Each model has a cluster_id column but it's not really needed for anything on output
            if column.name == 'cluster_id' and is_output:
                continue

            # We already have cluster_id and don't need a SIOElem'd one.
            if column.name == 'cluster_id' and has_cluster_id:
                continue

            if column.name in attrs.skip_input_params:
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
                    if column.name in attrs.request_as_is:
                        wrapper = AsIs
                    else:
                        wrapper = v
                    columns.append(wrapper(column.name))
                    break
            else:
                if column.name in attrs.request_as_is:
                    columns.append(AsIs(column.name))
                else:
                    columns.append(column.name)

    return columns

# ################################################################################################################################

def update_attrs(cls, name, attrs):

    attrs = bunchify(attrs)
    mod = getmodule(cls)

    attrs.elem = mod.elem
    attrs.label = mod.label
    attrs.model = mod.model
    attrs.output_required_extra = getattr(mod, 'output_required_extra', [])
    attrs.output_optional_extra = getattr(mod, 'output_optional_extra', [])
    attrs.get_data_func = mod.list_func
    attrs.def_needed = getattr(mod, 'def_needed', False)
    attrs.initial_input = getattr(mod, 'initial_input', {})
    attrs.skip_input_params = getattr(mod, 'skip_input_params', [])
    attrs.skip_output_params = getattr(mod, 'skip_output_params', [])
    attrs.pre_opaque_attrs_hook = getattr(mod, 'pre_opaque_attrs_hook', None)
    attrs.instance_hook = getattr(mod, 'instance_hook', None)
    attrs.response_hook = getattr(mod, 'response_hook', None)
    attrs.delete_hook = getattr(mod, 'delete_hook', None)
    attrs.broker_message_hook = getattr(mod, 'broker_message_hook', None)
    attrs.extra_delete_attrs = getattr(mod, 'extra_delete_attrs', [])
    attrs.input_required_extra = getattr(mod, 'input_required_extra', [])
    attrs.input_optional_extra = getattr(mod, 'input_optional_extra', [])
    attrs.create_edit_input_required_extra = getattr(mod, 'create_edit_input_required_extra', [])
    attrs.create_edit_input_optional_extra = getattr(mod, 'create_edit_input_optional_extra', [])
    attrs.create_edit_rewrite = getattr(mod, 'create_edit_rewrite', [])
    attrs.create_edit_force_rewrite = getattr(mod, 'create_edit_force_rewrite', set())
    attrs.check_existing_one = getattr(mod, 'check_existing_one', True)
    attrs.request_as_is = getattr(mod, 'request_as_is', [])
    attrs.sio_default_value = getattr(mod, 'sio_default_value', None)
    attrs.get_list_docs = getattr(mod, 'get_list_docs', None)
    attrs.delete_require_instance = getattr(mod, 'delete_require_instance', True)
    attrs.skip_create_integrity_error = getattr(mod, 'skip_create_integrity_error', False)
    attrs.skip_if_exists = getattr(mod, 'skip_if_exists', False)
    attrs.skip_if_missing = getattr(mod, 'skip_if_missing', False)
    attrs._meta_session = None

    attrs.is_get_list = False
    attrs.is_create = False
    attrs.is_edit = False
    attrs.is_create_edit = False
    attrs.is_delete = False

    if name == 'GetList':
        attrs.is_get_list = True
        attrs.output_required = attrs.model
        attrs.output_optional = attrs.model
    else:

        attrs.broker_message = mod.broker_message
        attrs.broker_message_prefix = mod.broker_message_prefix

        if name in('Create', 'Edit'):

            attrs.input_required = attrs.model
            attrs.input_optional = attrs.model
            attrs.is_create = name == 'Create'
            attrs.is_edit = name == 'Edit'
            attrs.is_create_edit = True

        elif name == 'Delete':
            attrs.is_delete = True

    return attrs

# ################################################################################################################################
# ################################################################################################################################

class AdminServiceMeta(type):

    @staticmethod
    def get_sio(
        *,
        attrs,
        name,
        input_required=None,
        input_optional=None,
        output_required=None,
        is_list=True,
        class_=None,
        skip_input_required=False
    ):

        _BaseClass = GetListAdminSIO if is_list else AdminSIO

        if not input_optional:
            input_optional = list(_BaseClass.input_optional) if hasattr(_BaseClass, 'input_optional') else []

        if not input_required:
            if skip_input_required:
                input_required = []
            else:
                input_required = ['cluster_id']

        sio = {
            'input_required': input_required,
            'input_optional': input_optional,
            'output_required': output_required if output_required is not None else ['id', 'name'],
        }

        class SimpleIO(_BaseClass):
            request_elem = 'zato_{}_{}_request'.format(attrs.elem, req_resp[name])
            response_elem = 'zato_{}_{}_response'.format(attrs.elem, req_resp[name])
            default_value = attrs['sio_default_value']
            input_required = sio['input_required'] + attrs['input_required_extra']
            input_optional = sio['input_optional'] + attrs['input_optional_extra']

            for param in attrs['skip_input_params']:
                if param in input_required:
                    input_required.remove(param)

            output_required = sio['output_required'] + attrs['output_required_extra']
            output_optional = attrs['output_optional_extra']

        for io in 'input', 'output':
            for req in 'required', 'optional':
                _name = '{}_{}'.format(io, req)

                is_required = 'required' in req
                is_output = 'output' in io
                is_get_list = name=='GetList'

                sio_elem = getattr(SimpleIO, _name)
                has_cluster_id = 'cluster_id' in sio_elem
                sio_to_add = get_io(
                    attrs, _name, attrs.get('is_edit'), is_required, is_output, is_get_list, has_cluster_id)
                sio_elem.extend(sio_to_add)

                if attrs.is_create_edit and is_required:
                    sio_elem.extend(attrs.create_edit_input_required_extra)

                if attrs.is_create_edit and (not is_required):
                    sio_elem.extend(attrs.create_edit_input_optional_extra)

                # Sorts and removes duplicates
                setattr(SimpleIO, _name, list(set(sio_elem)))

        for skip_name in attrs.skip_output_params:
            for attr_names in chain([SimpleIO.output_required, SimpleIO.output_optional]):
                if skip_name in attr_names:
                    attr_names.remove(skip_name)

        SimpleIO.input_required = tuple(SimpleIO.input_required)
        SimpleIO.input_optional = tuple(SimpleIO.input_optional)
        SimpleIO.output_required = tuple(SimpleIO.output_required)
        SimpleIO.output_optional = tuple(SimpleIO.output_optional)

        return SimpleIO

# ################################################################################################################################
# ################################################################################################################################

class GetListMeta(AdminServiceMeta):
    """ A metaclass customizing the creation of services returning lists of objects.
    """
    def __init__(cls, name, bases, attrs):
        attrs = update_attrs(cls, name, attrs)
        cls.__doc__ = 'Returns a list of {}.'.format(attrs.get_list_docs)
        cls.SimpleIO = GetListMeta.get_sio(attrs=attrs, name=name, is_list=True)
        cls.handle = GetListMeta.handle(attrs)
        cls.get_data = GetListMeta.get_data(attrs.get_data_func)
        super(GetListMeta, cls).__init__(cls)

    @staticmethod
    def get_data(get_data_func):
        def get_data_impl(self, session):
            # type: (Service, object)
            return self._search(get_data_func, session, self.request.input.cluster_id, False)
        return get_data_impl

    @staticmethod
    def handle(attrs):
        def handle_impl(self:'Service') -> 'None':
            input = self.request.input
            input.cluster_id = input.get('cluster_id') or self.server.cluster_id

            with closing(self.odb.session()) as session:
                elems = elems_with_opaque(self.get_data(session))
                self.response.payload[:] = elems

            if attrs.response_hook:
                attrs.response_hook(self, self.request.input, None, attrs, 'get_list')

        return handle_impl

# ################################################################################################################################
# ################################################################################################################################

class CreateEditMeta(AdminServiceMeta):
    is_create = False
    output_required = ('id', 'name')

    def __init__(cls, name, bases, attrs):
        attrs = update_attrs(cls, name, attrs)
        verb = 'Creates' if attrs.is_create else 'Updates'
        cls.__doc__ = '{} {}.'.format(verb, attrs.label)
        cls.SimpleIO = CreateEditMeta.get_sio(attrs=attrs, name=name, is_list=False, class_=cls)
        cls.handle = CreateEditMeta.handle(attrs)
        super(CreateEditMeta, cls).__init__(cls)

    @staticmethod
    def handle(attrs):
        def handle_impl(self):
            # type: (Service)

            input = self.request.input
            input.cluster_id = input.get('cluster_id') or self.server.cluster_id
            input.update(attrs.initial_input)
            verb = 'edit' if attrs.is_edit else 'create'
            old_name = None
            has_integrity_error = False

            # Try to parse the opaque elements into a dict ..
            input.opaque1 = parse_literal_dict(input.opaque1)

            # .. only to turn it into a JSON string suitable for SQL storage ..
            input.opaque1 = dumps(input.opaque1)

            with closing(self.odb.session()) as session:
                try:
                    attrs._meta_session = session

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

                        if existing_one:
                            if attrs.is_create:
                                if attrs.skip_if_exists:
                                    pass # Ignore it explicitly
                                else:
                                    raise BadRequest(self.cid, '{} `{}` already exists in this cluster'.format(
                                        attrs.label[0].upper() + attrs.label[1:], input.name))
                            else:
                                if attrs.skip_if_missing:
                                    pass # Ignore it explicitly
                                else:
                                    raise BadRequest(self.cid, 'No such {} `{}` in this cluster'.format(
                                        attrs.label[0].upper() + attrs.label[1:], input.name))

                    if attrs.is_edit:
                        instance = session.query(attrs.model).filter_by(id=input.id).one()
                        old_name = instance.name
                    else:
                        instance = self._new_zato_instance_with_cluster(attrs.model)

                    # Update the instance with data received on input, however,
                    # note that this may overwrite some of existing attributes
                    # if they are empty on input. If it's not desired,
                    # set skip_input_params = ['...'] to ignore such input parameters.
                    instance.fromdict(input, exclude=['password'], allow_pk=True)

                    # Invoke a hook that will set any additional opaque attrs
                    # that are required but were possibly not given on input.
                    if attrs.pre_opaque_attrs_hook:
                        attrs.pre_opaque_attrs_hook(self, input, instance, attrs)

                    # Populate all the opaque attrs now
                    set_instance_opaque_attrs(instance, input)

                    # Now that we have an instance which is known not to be a duplicate
                    # we can possibly invoke a customization function before we commit
                    # anything to the database.
                    if attrs.instance_hook:
                        attrs.instance_hook(self, input, instance, attrs)

                    session.add(instance)

                    try:
                        session.commit()
                    except IntegrityError:
                        if not attrs.skip_create_integrity_error:
                            raise
                        else:
                            has_integrity_error = True

                except Exception:
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

                    if not has_integrity_error:
                        self.broker_client.publish(input)

                    to_rewrite = chain(
                        attrs.create_edit_rewrite,
                        attrs.create_edit_force_rewrite,
                        self.SimpleIO.output_required
                    )

                    for name in to_rewrite:
                        value = getattr(instance, name, singleton)
                        if value is singleton or name in attrs.create_edit_force_rewrite:
                            value = input[name]

                        setattr(self.response.payload, name, value)

                    if attrs.response_hook:
                        attrs.response_hook(self, input, instance, attrs, 'create_edit')

        return handle_impl

# ################################################################################################################################
# ################################################################################################################################

class DeleteMeta(AdminServiceMeta):
    def __init__(cls, name, bases, attrs):
        attrs = update_attrs(cls, name, attrs)
        cls.__doc__ = 'Deletes {}.'.format(attrs.label)
        cls.SimpleIO = DeleteMeta.get_sio(
            attrs=attrs,
            name=name,
            input_required=[],
            input_optional=['id', 'name', 'should_raise_if_missing'],
            output_required=[],
            skip_input_required=True,
        )
        cls.handle = DeleteMeta.handle(attrs)
        super(DeleteMeta, cls).__init__(cls)

    @staticmethod
    def handle(attrs):
        def handle_impl(self):
            # type: (Service)

            input = self.request.input

            input_id = input.get('id')
            input_name = input.get('name')

            if not (input_id or input_name):
                raise BadRequest(self.cid, 'Either id or name is required on input')

            with closing(self.odb.session()) as session:
                attrs._meta_session = session
                try:
                    query = session.query(attrs.model)

                    if input_id:
                        query = query.\
                            filter(attrs.model.id==input_id)

                    else:
                        query = query.\
                            filter(attrs.model.name==input_name)

                    instance = query.first()

                    # We do not always require for input ID to actually exist - this is useful
                    # with enmasse which may attempt to delete objects that no longer exist.
                    # This may happen if it deletes an object that was an FK to another one.
                    # That other one will be always deleted but enmasse will not know it
                    # so it will try to delete it too, which will fail. This happens, for instance,
                    # when a WebSocket channel is deleted - it may cascade to a pub/sub endpoint
                    # but enmasse does not know about, hence delete_require_instance is True in pubsub_endpoint's endpoint.py.
                    if not instance:
                        if attrs.delete_require_instance:
                            if input_id:
                                attr_name = 'id'
                                attr_value = input_id
                            else:
                                attr_name = 'name'
                                attr_value = input_name

                            # We may have a test case that deletes a Basic Auth definition before it tries
                            # to delete a WebSocket channel related to it. In such circumstances, this flag
                            # will be set to False to ensure that no unneeded exception will be raised.
                            if input.get('should_raise_if_missing', True):
                                raise BadRequest(self.cid, 'Could not find {} instance with {} `{}`'.format(
                                    attrs.label, attr_name, attr_value))
                            else:
                                return
                        else:
                            return

                    if attrs.instance_hook:
                        attrs.instance_hook(self, input, instance, attrs)

                    session.delete(instance)
                    session.commit()
                except Exception:
                    msg = 'Could not delete {}, e:`%s`'.format(attrs.label)
                    self.logger.error(msg, format_exc())
                    session.rollback()

                    raise
                else:
                    input.action = getattr(attrs.broker_message, attrs.broker_message_prefix + 'DELETE').value
                    input.name = getattr(instance, 'name', ZATO_NOT_GIVEN)

                    for name in attrs.extra_delete_attrs:
                        input[name] = getattr(instance, name)

                    if attrs.broker_message_hook:
                        attrs.broker_message_hook(self, input, instance, attrs, 'delete')

                    self.broker_client.publish(input)

                    if attrs.delete_hook:
                        attrs.delete_hook(self, input, instance, attrs)

        return handle_impl

# ################################################################################################################################
# ################################################################################################################################

class PingMeta(AdminServiceMeta):
    def __init__(cls, name, bases, attrs):
        attrs = update_attrs(cls, name, attrs)
        cls.SimpleIO = PingMeta.get_sio(attrs=attrs, name=name, input_required=['id'], output_optional=['info', 'id'])
        cls.handle = PingMeta.handle(attrs)
        super(PingMeta, cls).__init__(cls)

    @staticmethod
    def handle(attrs):
        def handle_impl(self):
            # type: (Service)

            with closing(self.odb.session()) as session:
                config = session.query(attrs.model).\
                    filter(attrs.model.id==self.request.input.id).\
                    one()

                start_time = time()
                self.ping(config)
                response_time = time() - start_time

                # Always return ID of the object we pinged
                self.response.payload.id = self.request.input.id

                # Return ping details
                self.response.payload.info = 'Ping issued in {0:03.4f} s, check server logs for details, if any.'.format(
                    response_time)

        return handle_impl

# ################################################################################################################################
# ################################################################################################################################
