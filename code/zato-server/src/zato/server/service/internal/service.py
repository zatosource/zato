# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from httplib import BAD_REQUEST, NOT_FOUND
from json import dumps, loads
from mimetypes import guess_type
from tempfile import NamedTemporaryFile
from traceback import format_exc
from urlparse import parse_qs
from uuid import uuid4

# validate
from validate import is_boolean

# Zato
from zato.common import BROKER, KVDB, ZatoException
from zato.common.broker_message import SERVICE
from zato.common.odb.model import Cluster, ChannelAMQP, ChannelWMQ, ChannelZMQ, DeployedService, HTTPSOAP, Server, Service
from zato.common.odb.query import service_list
from zato.common.util import hot_deploy, payload_from_request
from zato.server.service import Boolean, Integer
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

_no_such_service_name = uuid4().hex

# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of services.
    """
    _filter_by = Service.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_service_get_list_request'
        response_elem = 'zato_service_get_list_response'
        input_required = ('cluster_id', 'query')
        output_required = ('id', 'name', 'is_active', 'impl_name', 'is_internal', Boolean('may_be_deleted'), Integer('usage'),
            Integer('slow_threshold'))
        output_repeated = True
        default_value = ''

    def get_data(self, session):

        return_internal = is_boolean(self.server.fs_server_config.misc.return_internal_objects)
        internal_del = is_boolean(self.server.fs_server_config.misc.internal_services_may_be_deleted)

        out = []
        for item in self._search(service_list, session, self.request.input.cluster_id, return_internal, False):
            item.may_be_deleted = internal_del if item.is_internal else True
            item.usage = self.server.kvdb.conn.get('{}{}'.format(KVDB.SERVICE_USAGE, item.name)) or 0

            out.append(item)

        return out

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class _Get(AdminService):

    class SimpleIO(AdminSIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'impl_name', 'is_internal', Boolean('may_be_deleted'),
            Integer('usage'), Integer('slow_threshold'), Integer('time_last'),
            Integer('time_min_all_time'), Integer('time_max_all_time'), 'time_mean_all_time',)

    def get_data(self, session):
        query = session.query(Service.id, Service.name, Service.is_active,
            Service.impl_name, Service.is_internal, Service.slow_threshold).\
            filter(Cluster.id==Service.cluster_id).\
            filter(Cluster.id==self.request.input.cluster_id)

        query = self.add_filter(query)
        return query.one()

    def handle(self):
        with closing(self.odb.session()) as session:
            service = self.get_data(session)
            internal_del = is_boolean(self.server.fs_server_config.misc.internal_services_may_be_deleted)

            self.response.payload.id = service.id
            self.response.payload.name = service.name
            self.response.payload.is_active = service.is_active
            self.response.payload.impl_name = service.impl_name
            self.response.payload.is_internal = service.is_internal
            self.response.payload.slow_threshold = service.slow_threshold
            self.response.payload.may_be_deleted = internal_del if service.is_internal else True
            self.response.payload.usage = self.server.kvdb.conn.get('{}{}'.format(KVDB.SERVICE_USAGE, service.name)) or 0

            time_key = '{}{}'.format(KVDB.SERVICE_TIME_BASIC, service.name)
            self.response.payload.time_last = self.server.kvdb.conn.hget(time_key, 'last')

            for name in('min_all_time', 'max_all_time', 'mean_all_time'):
                setattr(self.response.payload, 'time_{}'.format(name), float(
                    self.server.kvdb.conn.hget(time_key, name) or 0))

            self.response.payload.time_min_all_time = int(self.response.payload.time_min_all_time)
            self.response.payload.time_max_all_time = int(self.response.payload.time_max_all_time)
            self.response.payload.time_mean_all_time = round(self.response.payload.time_mean_all_time, 1)

# ################################################################################################################################

class GetByName(_Get):
    """ Returns a particular service by its name.
    """
    class SimpleIO(_Get.SimpleIO):
        request_elem = 'zato_service_get_by_name_request'
        response_elem = 'zato_service_get_by_name_response'
        input_required = _Get.SimpleIO.input_required + ('name',)

    def add_filter(self, query):
        return query.\
               filter(Service.name==self.request.input.name)

# ################################################################################################################################

class GetByID(_Get):
    """ Returns a particular service by its ID.
    """
    class SimpleIO(_Get.SimpleIO):
        request_elem = 'zato_service_get_by_name_request'
        response_elem = 'zato_service_get_by_name_response'
        input_required = _Get.SimpleIO.input_required + ('id',)

    def add_filter(self, query):
        return query.\
               filter(Service.id==self.request.input.id)

# ################################################################################################################################

class Edit(AdminService):
    """ Updates a service.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_edit_request'
        response_elem = 'zato_service_edit_response'
        input_required = ('id', 'is_active', Integer('slow_threshold'))
        output_required = ('id', 'name', 'impl_name', 'is_internal', Boolean('may_be_deleted'))

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                service = session.query(Service).filter_by(id=input.id).one()
                service.is_active = input.is_active
                service.slow_threshold = input.slow_threshold

                session.add(service)
                session.commit()

                input.action = SERVICE.EDIT.value
                input.impl_name = service.impl_name
                self.broker_client.publish(input)

                self.response.payload = service

                internal_del = is_boolean(self.server.fs_server_config.misc.internal_services_may_be_deleted)
                self.response.payload.may_be_deleted = internal_del if service.is_internal else True

            except Exception, e:
                msg = 'Could not update the service, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a service
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_delete_request'
        response_elem = 'zato_service_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                service = session.query(Service).\
                    filter(Service.id==self.request.input.id).\
                    one()

                internal_del = is_boolean(self.server.fs_server_config.misc.internal_services_may_be_deleted)

                if service.is_internal and not internal_del:
                    msg = "Can't delete service:[{}], it's an internal one and internal_services_may_be_deleted is not True".format(
                        service.name)
                    raise ZatoException(self.cid, msg)

                # This will also cascade to delete the related DeployedService objects
                session.delete(service)
                session.commit()

                msg = {'action': SERVICE.DELETE.value, 'id': self.request.input.id, 'impl_name':service.impl_name,
                       'is_internal':service.is_internal}
                self.broker_client.publish(msg)

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the service, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise

# ################################################################################################################################

class GetChannelList(AdminService):
    """ Returns a list of channels of a given type through which the service
    is being exposed.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_get_channel_list_request'
        response_elem = 'zato_service_get_channel_list_response'
        input_required = ('id', 'channel_type')
        output_required = ('id', 'name')

    def handle(self):
        channel_type_class = {
            'plain_http': HTTPSOAP,
            'soap': HTTPSOAP,
            'amqp': ChannelAMQP,
            'jms-wmq': ChannelWMQ,
            'zmq': ChannelZMQ,
        }

        class_ = channel_type_class[self.request.input.channel_type]
        q_attrs = (class_.id, class_.name)

        with closing(self.odb.session()) as session:
            q = session.query(*q_attrs).\
                filter(class_.service_id == self.request.input.id)

            if self.request.input.channel_type == 'soap':
                q = q.filter(class_.soap_version != None) # noqa
            elif self.request.input.channel_type == 'plain_http':
                q = q.filter(class_.soap_version == None) # noqa

            self.response.payload[:] = q.all()

# ################################################################################################################################

class Invoke(AdminService):
    """ Invokes the service directly, as though it was exposed through some channel defined in web-admin.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_invoke_request'
        response_elem = 'zato_service_invoke_response'
        input_optional = ('id', 'name', 'payload', 'channel', 'data_format', 'transport', Boolean('async'),
            Integer('expiration'), Integer('pid'), Boolean('all_pids'), Integer('timeout'))
        output_optional = ('response',)

    def handle(self):
        payload = self.request.input.get('payload')
        if payload:
            payload = payload_from_request(self.cid, payload.decode('base64'),
                self.request.input.data_format, self.request.input.transport)

        id = self.request.input.get('id')
        name = self.request.input.get('name')
        pid = self.request.input.get('pid') or 0
        all_pids = self.request.input.get('all_pids')
        timeout = self.request.input.get('timeout') or None

        channel = self.request.input.get('channel')
        data_format = self.request.input.get('data_format')
        transport = self.request.input.get('transport')
        expiration = self.request.input.get('expiration') or BROKER.DEFAULT_EXPIRATION

        if name and id:
            raise ZatoException('Cannot accept both id:`{}` and name:`{}`'.format(id, name))

        if self.request.input.get('async'):

            if id:
                impl_name = self.server.service_store.id_to_impl_name[id]
                name = self.server.service_store.service_data(impl_name)['name']

            # If PID is given on input it means we must invoke this particular server process by it ID
            if pid and pid != self.server.pid:
                response = self.server.invoke_by_pid(name, payload, pid)
            else:
                response = self.invoke_async(name, payload, channel, data_format, transport, expiration)

        else:

            # Same as above in async branch, except in async there was no all_pids
            if all_pids:
                args = (name, payload, timeout) if timeout else (name, payload)
                response = dumps(self.server.invoke_all_pids(*args))
            else:
                if pid and pid != self.server.pid:
                    response = self.server.invoke(name, payload, pid=pid, data_format=data_format)
                else:
                    func, id_ = (self.invoke, name) if name else (self.invoke_by_id, id)
                    response = func(id_, payload, channel, data_format, transport, serialize=True)

        if isinstance(response, basestring):
            if response:
                self.response.payload.response = response.encode('base64') if response else ''

# ################################################################################################################################

class GetDeploymentInfoList(AdminService):
    """ Returns detailed information regarding the service's deployment status
    on each of the servers it's been deployed to.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_get_deployment_info_list_request'
        response_elem = 'zato_service_get_deployment_info_list_response'
        input_required = ('id',)
        output_required = ('server_id', 'server_name', 'details')

    def get_data(self, session):
        items = session.query(DeployedService.details,
            Server.name.label('server_name'),
            Server.id.label('server_id')).\
            outerjoin(Server, DeployedService.server_id==Server.id).\
            filter(DeployedService.service_id==self.request.input.id).\
            all()

        for item in items:
            item.details = loads(loads(item.details))

        return items

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class GetSourceInfo(AdminService):
    """ Returns information on the service's source code.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_get_source_info_request'
        response_elem = 'zato_service_get_source_info_response'
        input_required = ('cluster_id', 'name')
        output_optional = ('service_id', 'server_name', 'source', 'source_path', 'source_hash', 'source_hash_method')

    def get_data(self, session):
        return session.query(Service.id.label('service_id'), Server.name.label('server_name'),
            DeployedService.source, DeployedService.source_path,
            DeployedService.source_hash, DeployedService.source_hash_method).\
            filter(Cluster.id==Service.cluster_id).\
            filter(Cluster.id==self.request.input.cluster_id).\
            filter(Service.name==self.request.input.name).\
            filter(Service.id==DeployedService.service_id).\
            filter(Server.id==DeployedService.server_id).\
            filter(Server.id==self.server.id).\
            one()

    def handle(self):
        with closing(self.odb.session()) as session:
            si = self.get_data(session)
            self.response.payload.service_id = si.service_id
            self.response.payload.server_name = si.server_name
            self.response.payload.source = si.source.encode('base64') if si.source else None
            self.response.payload.source_path = si.source_path
            self.response.payload.source_hash = si.source_hash
            self.response.payload.source_hash_method = si.source_hash_method

# ################################################################################################################################

class GetWSDL(AdminService):
    """ Returns a WSDL for the given service. Either uses a user-uploaded one,
    or, optionally generates one on fly if the service uses SimpleIO.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_get_wsdl_request'
        response_elem = 'zato_service_get_wsdl_response'
        input_optional = ('service', 'cluster_id')
        output_required = ('content_type',)
        output_optional = ('wsdl', 'wsdl_name',)

    def handle(self):
        if self.wsgi_environ['QUERY_STRING']:
            use_sio = False
            query = parse_qs(self.wsgi_environ['QUERY_STRING'])
            service_name = query.get('service', (None,))[0]
            cluster_id = query.get('cluster_id', (None,))[0]
        else:
            use_sio = True
            service_name = self.request.input.service
            cluster_id = self.request.input.cluster_id

        if not(service_name and cluster_id):
            msg = 'Both [service] and [cluster_id] parameters are required'
            if use_sio:
                raise ValueError(msg)
            else:
                self.response.status_code = BAD_REQUEST
                self.response.payload = msg
                return

        with closing(self.odb.session()) as session:
            service = session.query(Service).\
                filter_by(name=service_name, cluster_id=cluster_id).\
                first()

            if not service:
                self.response.status_code = NOT_FOUND
                self.response.payload = 'Service [{}] not found'.format(service_name)
                return

        if service.wsdl_name:
            content_type = guess_type(service.wsdl_name)[0] or 'application/octet-stream'
        else:
            content_type = 'text/plain'

        if use_sio:
            self.response.payload.wsdl = (service.wsdl or '').encode('base64')
            self.response.payload.wsdl_name = service.wsdl_name
            self.response.payload.content_type = content_type
        else:
            if service.wsdl:
                self.set_attachment(service.wsdl_name, service.wsdl, content_type)
            else:
                self.response.status_code = NOT_FOUND
                self.response.payload = 'No WSDL found'

    def set_attachment(self, attachment_name, payload, content_type):
        """ Sets the information that we're returning an attachment to the user.
        """
        self.response.content_type = content_type
        self.response.payload = payload
        self.response.headers['Content-Disposition'] = 'attachment; filename={}'.format(attachment_name)

# ################################################################################################################################

class SetWSDL(AdminService):
    """ Updates the service's WSDL.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_set_wsdl_request'
        response_elem = 'zato_service_set_wsdl_response'
        input_required = ('cluster_id', 'name', 'wsdl', 'wsdl_name')

    def handle(self):
        with closing(self.odb.session()) as session:
            service = session.query(Service).\
                filter_by(name=self.request.input.name, cluster_id=self.request.input.cluster_id).\
                one()
            service.wsdl = self.request.input.wsdl.decode('base64')
            service.wsdl_name = self.request.input.wsdl_name

            session.add(service)
            session.commit()

# ################################################################################################################################

class HasWSDL(AdminService):
    """ Returns a boolean flag indicating whether the server has a WSDL attached.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_has_wsdl_request'
        response_elem = 'zato_service_has_wsdl_response'
        input_required = ('name', 'cluster_id')
        output_required = ('service_id', 'has_wsdl',)

    def handle(self):
        with closing(self.odb.session()) as session:
            result = session.query(Service.id, Service.wsdl).\
                filter_by(name=self.request.input.name, cluster_id=self.request.input.cluster_id).\
                one()
            self.response.payload.service_id = result.id
            self.response.payload.has_wsdl = result.wsdl is not None

# ################################################################################################################################

class GetRequestResponse(AdminService):
    """ Returns a sample request/response along with information on how often
    the pairs should be stored in the DB.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_get_request_response_request'
        response_elem = 'zato_service_request_response_response'
        input_required = ('cluster_id', 'name')
        output_required = ('service_id', Integer('sample_req_resp_freq'))
        output_optional = ('sample_cid', 'sample_req_ts', 'sample_resp_ts', 'sample_req', 'sample_resp', )

    def get_data(self):
        result = {}

        with closing(self.odb.session()) as session:
            result['id'] = session.query(Service.id).\
                filter_by(name=self.request.input.name, cluster_id=self.request.input.cluster_id).\
                one()[0]

        result.update(**self.kvdb.conn.hgetall('{}{}'.format(KVDB.REQ_RESP_SAMPLE, self.request.input.name)))

        return result

    def handle(self):
        result = self.get_data()
        self.response.payload.service_id = result.get('id')
        self.response.payload.sample_cid = result.get('cid')
        self.response.payload.sample_req_ts = result.get('req_ts')
        self.response.payload.sample_resp_ts = result.get('resp_ts')
        self.response.payload.sample_req = result.get('req', '').encode('base64')
        self.response.payload.sample_resp = result.get('resp', '').encode('base64')
        self.response.payload.sample_req_resp_freq = result.get('freq', 0)

# ################################################################################################################################

class ConfigureRequestResponse(AdminService):
    """ Updates the request/response-related configuration.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_configure_request_response_request'
        response_elem = 'zato_service_configure_request_response_response'
        input_required = ('cluster_id', 'name', Integer('sample_req_resp_freq'))

    def handle(self):
        key = '{}{}'.format(KVDB.REQ_RESP_SAMPLE, self.request.input.name)
        self.kvdb.conn.hset(key, 'freq', self.request.input.sample_req_resp_freq)

# ################################################################################################################################

class UploadPackage(AdminService):
    """ Returns a boolean flag indicating whether the server has a WSDL attached.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_upload_package_request'
        response_elem = 'zato_service_upload_package_response'
        input_required = ('cluster_id', 'payload', 'payload_name')

    def handle(self):
        with NamedTemporaryFile(prefix='zato-hd-', suffix=self.request.input.payload_name) as tf:
            tf.write(self.request.input.payload.decode('base64'))
            tf.flush()

            package_id = hot_deploy(self.server, self.request.input.payload_name, tf.name, False)

        self.response.payload = {
            'package_id': package_id
        }

# ################################################################################################################################

class _SlowResponseService(AdminService):
    def get_data(self):
        data = []
        cid_needed = self.request.input.cid if 'cid' in self.SimpleIO.input_required else None
        key = '{}{}'.format(KVDB.RESP_SLOW, self.request.input.name)

        for item in self.kvdb.conn.lrange(key, 0, -1):
            item = loads(item)

            if cid_needed and cid_needed != item['cid']:
                continue

            elem = {}
            for name in('cid', 'req_ts', 'resp_ts', 'proc_time'):
                elem[name] = item[name]

            if cid_needed and cid_needed == item['cid']:
                for name in('req', 'resp'):
                    elem[name] = item.get(name, '')

            data.append(elem)

        return data

# ################################################################################################################################

class GetSlowResponseList(_SlowResponseService):
    """ Returns a list of basic information regarding slow responses of a given service.
    """
    @staticmethod
    def get_name():
        return 'zato.service.slow-response.get-list'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_slow_response_get_list_request'
        response_elem = 'zato_service_slow_response_get_list_response'
        input_required = ('name',)
        output_required = ('cid', 'req_ts', 'resp_ts', Integer('proc_time'))

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################

class GetSlowResponse(_SlowResponseService):
    """ Returns information regading a particular slow response of a service.
    """
    @staticmethod
    def get_name():
        return 'zato.service.slow-response.get'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_slow_response_get_request'
        response_elem = 'zato_service_slow_response_get_response'
        input_required = ('cid', 'name')
        output_optional = ('cid', 'req_ts', 'resp_ts', Integer('proc_time'), 'req', 'resp')

    def handle(self):
        data = self.get_data()
        if data:
            self.response.payload = data[0]

# ################################################################################################################################
