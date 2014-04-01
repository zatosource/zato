# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from pprint import pprint
from traceback import format_exc

# Bunch
from bunch import Bunch, bunchify

# gevent
from gevent import sleep, spawn

# Zato
from zato.common import NOTIF as COMMON_NOTIF, ZATO_NONE
from zato.common.broker_message import MESSAGE_TYPE, NOTIF
from zato.common.odb.model import NotificationOpenStackSwift, Service
from zato.common.odb.query import notif_cloud_openstack_swift_list
from zato.server.service import Bool, ForceType, Int
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

common_required = ('name', 'is_active', 'def_id', 'containers', Int('interval'), 'name_pattern', Bool('name_pattern_neg'),
    Bool('get_data'), Bool('get_data_patt_neg'), 'service_name')

common_optional = ('get_data_patt',)

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of OpenStack Swift notification definitions.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_notif_cloud_openstack_swift_get_list_request'
        response_elem = 'zato_notif_cloud_openstack_swift_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'def_name') + common_required
        output_optional = common_optional

    def get_data(self, session):
        return notif_cloud_openstack_swift_list(session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class _CreateEdit(AdminService):
    source_service_type = ZATO_NONE

    def _get_item(self, session, input):
        raise NotImplementedError()

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:

            existing_one = session.query(NotificationOpenStackSwift.id).\
                filter(NotificationOpenStackSwift.cluster_id==input.cluster_id).\
                filter(NotificationOpenStackSwift.name==input.name).\
                first()

            if self.source_service_type == 'create' and existing_one:
                raise Exception('An OpenStack Swift notification definition [{0}] already exists on this cluster'.format(input.name))

            try:
                old_name = None
                item = self._get_item(session, input)

                if self.source_service_type == 'edit':
                    old_name = item.name

                for name in self.SimpleIO.input_required + self.SimpleIO.input_optional:
                    if isinstance(name, ForceType):
                        name = name.name
                    setattr(item, name, self.request.input.get(name))

                item.service_id = session.query(Service.id).\
                    filter(Service.name==input.service_name).\
                    filter(Service.cluster_id==self.server.cluster_id).\
                    one()

                session.add(item)
                session.commit()

                input.action = NOTIF.CLOUD_OPENSTACK_SWIFT_CREATE_EDIT
                input.notif_type = COMMON_NOTIF.TYPE.OPENSTACK_SWIFT
                input.source_service_type = self.source_service_type
                input.def_name = item.definition.name

                if self.source_service_type == 'edit':
                    input.old_name = old_name

                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name
                self.response.payload.def_name = item.definition.name

            except Exception, e:
                msg = 'Could not %s an OpenStack Swift notification definition, e:`%s`'
                self.logger.error(msg, self.source_service_type, format_exc(e))
                session.rollback()

                raise 

# ################################################################################################################################

class Create(_CreateEdit):
    """ Creates a new OpenStack Swift notification definition.
    """
    source_service_type = 'create'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_notif_cloud_openstack_swift_create_request'
        response_elem = 'zato_notif_cloud_openstack_swift_create_response'
        input_required = ('cluster_id',) + common_required
        input_optional = common_optional
        output_required = ('id', 'name', 'def_name')

    def _get_item(self, *ignored):
        return NotificationOpenStackSwift()

# ################################################################################################################################

class Edit(_CreateEdit):
    """ Updates an OpenStack Swift notification definition.
    """
    source_service_type = 'edit'

    class SimpleIO(Create.SimpleIO):
        request_elem = 'zato_notif_cloud_openstack_swift_edit_request'
        response_elem = 'zato_notif_cloud_openstack_swift_edit_response'
        input_required = ('id',) + Create.SimpleIO.input_required

    def _get_item(self, session, input):
        return session.query(NotificationOpenStackSwift).filter_by(id=input.id).one()

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an OpenStack Swift notification definition.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_notif_cloud_openstack_swift_delete_request'
        response_elem = 'zato_notif_cloud_openstack_swift_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(NotificationOpenStackSwift).\
                    filter(NotificationOpenStackSwift.id==self.request.input.id).\
                    one()

                session.delete(item)
                session.commit()

                msg = {'action': NOTIF.CLOUD_OPENSTACK_SWIFT_DELETE, 'name': item.name, 'id':item.id}
                self.broker_client.publish(msg)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the OpenStack Swift notification definition, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise

# ################################################################################################################################

class RunNotifier(AdminService):
    """ Runs a background gevent-based notifier of new data in OpenStack Swift containers.
    """
    def _run_notifier(self, data):
        """ Invoked as a greenlet - fetches data from a container(s) and invokes the target service.
        """
        # It's possible our config has changed since the last time we run so we need to check the current one.
        current_config = self.server.worker_store.worker_config.notif_cloud_openstack_swift.get(data.name)

        # The notification definition has been deleted in between the invocations of ours so we need to stop now.
        if not current_config:
            self.keep_running = False
            return

        # Ok, overwrite old config with current one.
        data.update(current_config)

        request = Bunch()
        request.raw = {}

        # Grab a distributed lock so we are sure it is only us who connect to pull newest data.
        with self.lock(data.name):
            conn = self.cloud.openstack.swift[data.def_name].conn
            with conn.client() as client:
                for container_name, path, full_name in data.containers:
                    result = client.get_container(container_name, path=path)
                    raw = request.raw.setdefault(full_name, [])
                    raw.append(result)
                    
                    for item in result:
                        # Metadata will not contain this key
                        if 'hash' in item:
                            pass

        self.logger.warn(request)

    def handle(self):
        self.keep_running = True
        data = bunchify(self.request.payload)

        while self.keep_running:
            spawn(self._run_notifier, data)
            sleep(data.interval)

        self.logger.info('Stopped OpenStack Swift notifier `%s`', data.name)
