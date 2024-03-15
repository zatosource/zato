# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from copy import deepcopy
from dataclasses import dataclass

# gevent
from gevent import sleep

# SQLAlchemy
from sqlalchemy import delete

# Zato
from zato.common.api import CommonObject
from zato.common.odb.model.base import Base as BaseTable
from zato.common.odb.query.common import get_object_list_by_id_list, get_object_list_by_name_list, \
    get_object_list_by_name_contains
from zato.common.test.config import TestConfig
from zato.common.typing_ import any_, anylist, callable_, intlistnone, intnone, strdict, strlistnone, strnone, type_
from zato.server.connection.http_soap import BadRequest
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from sqlalchemy.orm import Session as SASession
    from zato.common.typing_ import strlist
    Bunch = Bunch
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BaseDeleteObjectsRequest(Model):
    id: intnone
    id_list: intlistnone
    name: strnone
    name_list: strlistnone
    pattern: strnone

@dataclass(init=False)
class BaseDeleteObjectsResponse(Model):
    objects: anylist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeleteObjectsImplRequest(BaseDeleteObjectsRequest):
    table: BaseTable
    delete_class: type_[Service]

@dataclass(init=False)
class DeleteObjectsImplResponse(BaseDeleteObjectsResponse):
    pass

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeleteObjectsRequest(BaseDeleteObjectsRequest):
    object_type: str

@dataclass(init=False)
class DeleteObjectsResponse(BaseDeleteObjectsResponse):
    pass

# ################################################################################################################################
# ################################################################################################################################

class DeleteObjectsImpl(Service):

    class SimpleIO:
        input = DeleteObjectsImplRequest
        output = DeleteObjectsImplResponse

    def _get_object_data(self, query:'any_', table:'BaseTable', where:'any_') -> 'anylist':

        with closing(self.odb.session()) as session:
            object_data = query(session, table, where)

        object_data = [dict(elem) for elem in object_data]
        return object_data

# ################################################################################################################################

    def _delete_object_list(self, table:'BaseTable', object_id_list:'anylist') -> 'anylist':

        # Make sure we have a list of integers on input
        object_id_list = [int(elem) for elem in object_id_list]

        # We want to return a list of their IDs along with names so that the API users can easily understand what was deleted
        # which means that we need to construct the list upfront as otherwise, once we delete an object,
        # such information will be no longer available.
        object_data = self._get_object_data(get_object_list_by_id_list, table, object_id_list)

        # Our response to produce
        out:'anylist' = []

        # A list of object IDs that we were able to delete
        objects = []

        # Go through each of the input object IDs ..
        for object_id in object_id_list:

            # .. invoke the service that will delete the object ..
            try:
                self.invoke(self.request.input.delete_class.get_name(), {
                    'id': object_id
                })
            except Exception as e:
                self.logger.warn('Exception while deleting object `%s` -> `%s`', object_id, e)
            else:
                # If we are here, it means that the object was deleted
                # in which case we add its ID for later use ..
                objects.append(object_id)

                # .. sleep for a while in case to make sure there is no sudden surge of deletions ..
                sleep(0.01)

        # Go through each of the IDs given on input and return it on output too
        # as long as we actually did delete such an object.
        for elem in object_data:
            if elem['id'] in objects:
                out.append(elem)

        # Return the response to our caller
        return out

# ################################################################################################################################

    def _get_object_id_list(self, query:'any_', table:'BaseTable', where:'any_') -> 'anylist':
        object_data = self._get_object_data(query, table, where)
        out = [elem['id'] for elem in object_data]
        return out

# ################################################################################################################################

    def handle(self) -> 'None':

        # Type checks
        object_id_list:'anylist'

        # Local aliases
        input = self.request.input # type: DeleteObjectsImplRequest

        # We can be given several types of input elements in the incoming request
        # and we always need to build a list of IDs out of them, unless we already
        # have a list of IDs on input.

        # This is a list - use it as-is
        if input.id_list:
            object_id_list = input.id_list

        # It is an individual object ID - we can turn it into a list as-is
        elif input.id:
            object_id_list = [input.id]

        # It is an individual object name - turn it into a list look it up in the database
        elif input.name:
            query:'callable_' = get_object_list_by_name_list
            where = [input.name]
            object_id_list = self._get_object_id_list(query, input.table, where)

        # It is a list of names - look up objects matching them now
        elif input.name_list:
            query:'callable_' = get_object_list_by_name_list
            where = input.name_list if isinstance(input.name_list, list) else [input.name_list] # type: ignore
            object_id_list = self._get_object_id_list(query, input.table, where)

        # This is a list of patterns but not necessarily full object names as above
        elif input.pattern:
            query:'callable_' = get_object_list_by_name_contains
            where = input.pattern
            object_id_list = self._get_object_id_list(query, input.table, where)

        else:
            raise BadRequest(self.cid, 'No deletion criteria were given on input')

        # No matter how we arrived at this result, we have a list of object IDs
        # and we can delete each of them now ..
        objects = self._delete_object_list(input.table, object_id_list)

        # .. now, we can produce a response for our caller ..
        response = DeleteObjectsImplResponse()
        response.objects = objects

        # .. and return it on output
        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################

class DeleteObjects(Service):

    name = 'zato.common.delete-objects'

    class SimpleIO:
        input = DeleteObjectsRequest
        output = DeleteObjectsResponse

    def handle(self) -> 'None':

        # Zato
        from zato.common.odb.model import PubSubTopic
        from zato.server.service.internal.pubsub.topic import Delete as DeleteTopic

        # Add type hints
        input:'DeleteObjectsRequest' = self.request.input

        # Maps incoming string names of objects to their actual ODB classes
        odb_map:'strdict' = {
            CommonObject.PubSub_Topic: PubSubTopic.__table__,
        }

        # Maps incoming string names of objects to services that actually delete them
        service_map = {
            CommonObject.PubSub_Topic: DeleteTopic,
        }

        # Get a class that represents the input object ..
        table = odb_map[input.object_type]

        # .. get a class that represents the service that actually handles input ..
        delete_class = service_map[input.object_type]

        # .. clone our input to form the basis of the request that the implementation will receive ..
        request:'strdict' = deepcopy(input.to_dict())

        # .. remove elements that the implementation does not need .
        _ = request.pop('object_type', None)

        # .. prepare extra parameters that the implementation expects ..
        extra = {
            'table':  table,
            'delete_class':  delete_class,
        }

        # .. build a request for the implementation service ..
        request_impl:'DeleteObjectsImplRequest' = DeleteObjectsImplRequest.from_dict(request, extra)

        # .. invoke the implementation service now ..
        result = self.invoke(DeleteObjectsImpl, request_impl)

        # .. and return the result to our caller.
        self.response.payload = result

# ################################################################################################################################
# ################################################################################################################################

class DeleteMany(Service):

    name = 'pub.zato.common.delete-many'
    input = '-name'

# ################################################################################################################################

    def _delete(self, session:'SASession', tables:'any_', pattern:'strlist') -> 'None':

        if not pattern:
            raise Exception('No pattersn were given on input')

        for table, columns in tables.items():
            for column in columns: # type: ignore
                for elem in pattern:
                    filter = column.contains(elem) # type: ignore
                    delete_query = delete(table).where(filter)
                    session.execute(delete_query)
                    session.commit()

# ################################################################################################################################

    def _delete_rest(self, session:'SASession', pattern:'strlist') -> 'None':

        # Zato
        from zato.common.odb.model import HTTPSOAP

        tables:'any_' = {
            HTTPSOAP.__table__: [HTTPSOAP.name],
        }

        self._delete(session, tables, pattern)

# ################################################################################################################################

    def _delete_security(self, session:'SASession', pattern:'strlist') -> 'None':

        # Zato
        from zato.common.odb.model import SecurityBase

        tables:'any_' = {
            SecurityBase.__table__: [SecurityBase.name],
        }

        self._delete(session, tables, pattern)

# ################################################################################################################################

    def _delete_pubsub(self, session:'SASession', pattern:'strlist') -> 'None':

        # Zato
        from zato.common.odb.model import PubSubEndpoint, PubSubTopic

        tables:'any_' = {
            PubSubEndpoint.__table__: [PubSubEndpoint.name],
            PubSubTopic.__table__: [PubSubTopic.name],
        }

        self._delete(session, tables, pattern)

# ################################################################################################################################

    def _delete_sql(self, session:'SASession', pattern:'strlist') -> 'None':

        # Zato
        from zato.common.odb.model import SQLConnectionPool

        tables:'any_' = {
            SQLConnectionPool.__table__: [SQLConnectionPool.name],
        }

        self._delete(session, tables, pattern)

# ################################################################################################################################

    def _delete_wsx(self, session:'SASession', pattern:'strlist') -> 'None':

        # Zato
        from zato.common.odb.model import ChannelWebSocket

        tables:'any_' = {
            ChannelWebSocket.__table__: [ChannelWebSocket.name],
        }

        self._delete(session, tables, pattern)

# ################################################################################################################################

    def _delete_scheduler(self, session:'SASession', pattern:'strlist') -> 'None':

        # Zato
        from zato.common.odb.model import Job

        tables:'any_' = {
            Job.__table__: [Job.name],
        }

        self._delete(session, tables, pattern)

# ################################################################################################################################

    def _delete_generic(self, session:'SASession', pattern:'strlist') -> 'None':

        # Zato
        from zato.common.odb.model import GenericConn, GenericConnDef, GenericObject

        tables:'any_' = {
            GenericConn.__table__: [GenericConn.name],
            GenericConnDef.__table__: [GenericConnDef.name],
            GenericObject.__table__: [GenericObject.name],
        }

        self._delete(session, tables, pattern)

# ################################################################################################################################

    def _delete_misc(self, session:'SASession', pattern:'strlist') -> 'None':

        # Zato
        from zato.common.odb.model import Cache, ChannelAMQP, ChannelWMQ, ConnDefAMQP, ConnDefWMQ, IMAP, OutgoingAMQP, \
            OutgoingFTP, OutgoingOdoo, OutgoingSAP, OutgoingWMQ, RBACClientRole, RBACPermission, RBACRole, TLSCACert, \
                Service, SMTP

        tables:'any_' = {
            Cache.__table__: [Cache.name],
            ChannelAMQP.__table__: [ChannelAMQP.name],
            ChannelWMQ.__table__: [ChannelWMQ.name],
            ConnDefAMQP.__table__: [ConnDefAMQP.name],
            ConnDefWMQ.__table__: [ConnDefWMQ.name],
            IMAP.__table__: [IMAP.name],
            OutgoingAMQP.__table__: [OutgoingAMQP.name],
            OutgoingFTP.__table__: [OutgoingFTP.name],
            OutgoingOdoo.__table__: [OutgoingOdoo.name],
            OutgoingSAP.__table__: [OutgoingSAP.name],
            OutgoingWMQ.__table__: [OutgoingWMQ.name],
            RBACClientRole.__table__: [RBACClientRole.name],
            RBACPermission.__table__: [RBACPermission.name],
            RBACRole.__table__: [RBACRole.name],
            TLSCACert.__table__: [TLSCACert.name],
            Service.__table__: [Service.name],
            SMTP.__table__: [SMTP.name],
        }

        self._delete(session, tables, pattern)

# ################################################################################################################################

    def handle(self) -> 'None':

        # Local variables
        name = self.request.input.get('name') or ''    # type: ignore
        name = [elem.strip() for elem in name.split()] # type: ignore

        if not name:
            name:'strlist' = [
                '.abc-123-',
                '.complex-',
                'Demo.',
                'Enmasse',
                'Enmasse',
                'enmasse',
                'enmasse1',
                '/test/api/complex',
                '/test/complex',
                'Test Basic Auth',
                'Test.Complex',
                '-test-cli-',
                'test.wsx',
                'zato-test',
                TestConfig.pubsub_topic_name_perf_auto_create,
                TestConfig.pubsub_topic_name_unique_auto_create,
            ]

        with closing(self.odb.session()) as session:

            self._delete_rest(session, name)
            self._delete_security(session, name)
            self._delete_pubsub(session, name)
            self._delete_sql(session, name)
            self._delete_wsx(session, name)
            self._delete_scheduler(session, name)
            self._delete_generic(session, name)
            self._delete_misc(session, name)

            session.commit()

# ################################################################################################################################
# ################################################################################################################################
