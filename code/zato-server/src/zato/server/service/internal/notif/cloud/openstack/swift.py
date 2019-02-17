# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Bunch
from bunch import Bunch, bunchify

# globre
from globre import match as globre_match

# Zato
from zato.common import NOTIF as COMMON_NOTIF, ZATO_NONE
from zato.common.broker_message import NOTIF
from zato.common.odb.model import Cluster, NotificationOpenStackSwift, Service
from zato.common.odb.query import notif_cloud_openstack_swift_list
from zato.server.service import Bool, ForceType, Int
from zato.server.service.internal.notif import NotifierService
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

common_required = ('name', 'is_active', 'def_id', 'containers', Int('interval'), 'name_pattern', Bool('name_pattern_neg'),
    Bool('get_data'), Bool('get_data_patt_neg'), 'service_name')

common_optional = ('get_data_patt',)

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of OpenStack Swift notification definitions.
    """
    _filter_by = NotificationOpenStackSwift.name,

    class SimpleIO(AdminSIO):
        request_elem = 'zato_notif_cloud_openstack_swift_get_list_request'
        response_elem = 'zato_notif_cloud_openstack_swift_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'def_name') + common_required
        output_optional = common_optional

    def get_data(self, session):
        return self._search(notif_cloud_openstack_swift_list, session, self.request.input.cluster_id, False)

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
                    filter(Service.cluster_id==Cluster.id).\
                    filter(Service.cluster_id==self.server.cluster_id).\
                    one()[0]

                session.add(item)
                session.commit()

                input.action = NOTIF.CLOUD_OPENSTACK_SWIFT_CREATE_EDIT.value
                input.notif_type = COMMON_NOTIF.TYPE.OPENSTACK_SWIFT
                input.source_service_type = self.source_service_type
                input.def_name = item.definition.name

                if self.source_service_type == 'edit':
                    input.old_name = old_name

                self.broker_client.publish(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name
                self.response.payload.def_name = item.definition.name

            except Exception:
                msg = 'Could not %s an OpenStack Swift notification definition, e:`%s`'
                self.logger.error(msg, self.source_service_type, format_exc())
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

                msg = {'action': NOTIF.CLOUD_OPENSTACK_SWIFT_DELETE.value, 'name': item.name, 'id':item.id}
                self.broker_client.publish(msg)

            except Exception:
                session.rollback()
                self.logger.error('OpenStack Swift notification definition could not be deleted, e:`{}`', format_exc())

                raise

# ################################################################################################################################

class RunNotifier(NotifierService):
    """ Runs a background gevent-based notifier of new data in OpenStack Swift containers.
    """
    notif_type = COMMON_NOTIF.TYPE.OPENSTACK_SWIFT

    def _name_matches(self, pattern, string, negate):
        """ Matches a string against a pattern and returns True if it found it. 'negate' reverses the result,
        only those not matching the pattern will yield True.
        """
        result = bool(globre_match(pattern, string))
        return not result if negate else result

    def _get_data(self, client, config, container, name):
        try:
            return client.get_object(container, name)[1]
        except Exception:
            self.logger.warn('Could not get `%s` from `%s`, e:`%s`', container, name, format_exc())

    def _prepare_service_request(self, ext_result, item, container, path, full_name):

        req = Bunch(req_meta=Bunch(), item=Bunch(payload=None))
        req.req_meta.container = container
        req.req_meta.path = path
        req.req_meta.full_name = full_name
        req.result_meta = ext_result[0]
        req.item_meta = bunchify(item)

        return req

    def run_notifier_impl(self, config):
        conn = self.cloud.openstack.swift[config.def_name].conn
        with conn.client() as client:
            for container, path, full_name in config.containers:

                # Results of the call to an external resource - first element is result's metadata
                # and elements 1: are the actual data, if any.
                ext_result = client.get_container(container, path=path)

                # Iterate over elements skipping directories - we're interested only in files.
                for items in ext_result[1:]:
                    for item in items:
                        if item['content_type'] != 'application/directory':

                            if not self._name_matches(config.name_pattern, item['name'], config.name_pattern_neg):
                                continue

                            # Prepare a service request ..
                            req = self._prepare_service_request(ext_result, item, container, path, full_name)

                            # .. but don't necessarily pull data from the container.
                            if config.get_data and self._name_matches(config.get_data_patt, item['name'], config.get_data_patt_neg):
                                req.item.payload = self._get_data(client, config, container, item['name'])

                            # Invoke the target service and see what next to do with its response
                            srv_result = self.invoke(config.service_name, req)

                            # Ok, we are to delete the just pulled document. Note that 'srv_result' can be either
                            # an empty string or dict hence two conditions.
                            if 'delete' in srv_result and srv_result.get('delete'):
                                client.delete_object(container, req.item_meta.name)
