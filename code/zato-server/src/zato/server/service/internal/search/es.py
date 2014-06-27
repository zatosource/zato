# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# SQLAlchemy
from sqlalchemy import Boolean, Integer

# Zato
from zato.common.broker_message import SEARCH
from zato.common.odb.model import Base, Cluster, ElasticSearch
from zato.common.odb.query import search_es_list
from zato.server.service import Bool as BoolSIO, Int as IntSIO
from zato.server.service.internal import AdminService, AdminSIO

sa_to_sio = {
    Boolean: BoolSIO,
    Integer: IntSIO
}

class BaseGetList(type, AdminService):
    ZATO_DONT_DEPLOY = True

    def __new__(cls, name, bases, attrs):

        # Dynamically create a SimpleIO definition this service will use
        cls.SimpleIO = BaseGetList.get_sio(attrs)
        cls.get_data = BaseGetList.get_data(attrs['get_data_func'])

        service_name = cls.get_name()
        service_name = service_name.split('.')[:-1]
        cls.name = '.'.join(service_name) + cls.convert_impl_name(name)

        return super(BaseGetList, cls).__new__(cls, name, bases, attrs)

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

    @staticmethod
    def get_sio(attrs):

        # Base SIO class to be populated in subsequent steps.

        class SimpleIO(AdminSIO):
            input_required = ('cluster_id',)

        # This can be either a list or an SQLAlchemy object
        output_required = attrs.get('output_required') or []

        # Generate output_required out of SQLAlchemy tables,
        # including calls to ForceType's subclasses, such as Bool or Int.

        if output_required and issubclass(output_required, Base):
            columns = []
            for column in [elem for elem in output_required._sa_class_manager.mapper.mapped_table.columns]:
                for k, v in sa_to_sio.items():
                    if isinstance(column.type, k):
                        columns.append(v(column.name))
                        break
                else:
                    columns.append(column.name)

            # Override whatever objects it used to be
            output_required = columns

        # We know we have at least an empty list
        SimpleIO.output_required = output_required

        return SimpleIO

class BaseCreateEdit(type, AdminService):
    ZATO_DONT_DEPLOY = True
    is_create = False
    output_required = ('id', 'name')

class BaseDelete(type, AdminService):
    ZATO_DONT_DEPLOY = True

class GetList(object):
    __metaclass__ = BaseGetList
    elem = 'search_es'
    output_required = ElasticSearch
    get_data_func = search_es_list

class _CreateEdit(object):
    elem = 'search_es'
    model = ElasticSearch
    input_required = ('name', 'is_active', 'hosts', IntSIO('timeout'), 'body_as')
    label = 'an ElasticSearch connection'
    broker_message = SEARCH
    broker_message_prefix = 'ES_'

class Create(_CreateEdit):
    is_create = True

class Edit(_CreateEdit):
    is_create = False

class Delete(object):
    model = ElasticSearch
    label = 'an ElasticSearch connection'
    broker_message = SEARCH
    broker_message_prefix = 'ES_'

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.broker_message import MSG_NS
from zato.common.odb.model import Cluster, MsgNamespace
from zato.common.odb.query import namespace_list
from zato.server.service.internal import AdminService, AdminSIO

class GetList(AdminService):
    """ Returns a list of namespaces available.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_namespace_get_list_request'
        response_elem = 'zato_message_namespace_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'value')

    def get_data(self, session):
        return namespace_list(session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

class Create(AdminService):
    """ Creates a new namespace.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_namespace_create_request'
        response_elem = 'zato_message_namespace_create_response'
        input_required = ('cluster_id', 'name', 'value')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:
            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()

                # Let's see if we already have a definition of that name before committing
                # any stuff into the database.
                existing_one = session.query(MsgNamespace).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(MsgNamespace.name==input.name).first()

                if existing_one:
                    raise Exception('Namespace [{0}] already exists on this cluster'.format(input.name))

                definition = MsgNamespace(None, input.name, input.value, cluster.id)

                session.add(definition)
                session.commit()

            except Exception, e:
                msg = 'Could not create a namespace, e:[%s]'
                self.logger.error(msg, format_exc(e))
                session.rollback()

                raise
            else:
                input.action = MSG_NS.CREATE
                self.broker_client.publish(input)

            self.response.payload.id = definition.id
            self.response.payload.name = definition.name

class Edit(AdminService):
    """ Updates a namespace.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_namespace_edit_request'
        response_elem = 'zato_message_namespace_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'value')
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                existing_one = session.query(MsgNamespace).\
                    filter(Cluster.id==input.cluster_id).\
                    filter(MsgNamespace.name==input.name).\
                    filter(MsgNamespace.id!=input.id).\
                    first()

                if existing_one:
                    raise Exception('Namespace [{0}] already exists on this cluster'.format(input.name))

                definition = session.query(MsgNamespace).filter_by(id=input.id).one()
                old_name = definition.name

                definition.name = input.name
                definition.value = input.value

                session.add(definition)
                session.commit()

            except Exception, e:
                msg = 'Could not update the namespace, e:[%s]'
                self.logger.error(msg, format_exc(e))
                session.rollback()

                raise
            else:
                input.action = MSG_NS.EDIT
                input.old_name = old_name
                self.broker_client.publish(input)

                self.response.payload.id = definition.id
                self.response.payload.name = definition.name

class Delete(AdminService):
    """ Deletes a namespace.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_message_namespace_delete_request'
        response_elem = 'zato_message_namespace_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                auth = session.query(MsgNamespace).\
                    filter(MsgNamespace.id==self.request.input.id).\
                    one()

                session.delete(auth)
                session.commit()
            except Exception, e:
                msg = 'Could not delete the namespace, e:[%s]'
                self.logger.error(msg, format_exc(e))
                session.rollback()

                raise
            else:
                self.request.input.action = MSG_NS.DELETE
                self.request.input.name = auth.name
                self.broker_client.publish(self.request.input)
'''