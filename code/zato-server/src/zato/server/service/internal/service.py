# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime
from httplib import BAD_REQUEST, NOT_FOUND
from mimetypes import guess_type
from tempfile import NamedTemporaryFile
from traceback import format_exc
from urlparse import parse_qs

# anyjson
from anyjson import loads

# validate
from validate import is_boolean

# Zato
from zato.common import KVDB, ZatoException
from zato.common.broker_message import SERVICE
from zato.common.odb.model import Cluster, ChannelAMQP, ChannelWMQ, ChannelZMQ, \
     DeployedService, HTTPSOAP, Server, Service
from zato.common.odb.query import service, service_list
from zato.common.util import hot_deploy, payload_from_request
from zato.server.service import Boolean, Integer
from zato.server.service.internal import AdminService

class GetList(AdminService):
    """ Returns a list of services.
    """
    class SimpleIO:
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'impl_name', 'is_internal', Boolean('may_be_deleted'), 'usage',
                           Integer('slow_threshold'))
        output_repeated = True
        
    def get_data(self, session):
        out = []
        sl = service_list(session, self.request.input.cluster_id, False)
        
        internal_del = is_boolean(self.server.fs_server_config.misc.internal_services_may_be_deleted)
        
        for item in sl:
            item.may_be_deleted = internal_del if item.is_internal else True
            item.usage = self.server.kvdb.conn.get('{}{}'.format(KVDB.SERVICE_USAGE, item.name)) or 0
            
            out.append(item)
        
        return out
        
    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)
        
class GetByName(AdminService):
    """ Returns a particular service.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'name')
        output_required = ('id', 'name', 'is_active', 'impl_name', 'is_internal', 'usage', 
            'time_last', 'time_min_all_time', 'time_max_all_time', 'time_mean_all_time',
            Integer('slow_threshold'))
        
    def get_data(self, session):
        return session.query(Service.id, Service.name, Service.is_active,
            Service.impl_name, Service.is_internal, Service.slow_threshold).\
            filter(Cluster.id==Service.cluster_id).\
            filter(Cluster.id==self.request.input.cluster_id).\
            filter(Service.name==self.request.input.name).\
            one()
        
    def handle(self):
        with closing(self.odb.session()) as session:
            service = self.get_data(session)
            self.response.payload.id = service.id
            self.response.payload.name = service.name
            self.response.payload.is_active = service.is_active
            self.response.payload.impl_name = service.impl_name
            self.response.payload.is_internal = service.is_internal
            self.response.payload.slow_threshold = service.slow_threshold
            self.response.payload.usage = self.server.kvdb.conn.get('{}{}'.format(KVDB.SERVICE_USAGE, service.name)) or 0

            time_key = '{}{}'.format(KVDB.SERVICE_TIME_BASIC, service.name)            
            self.response.payload.time_last = self.server.kvdb.conn.hget(time_key, 'last')
            
            for name in('min_all_time', 'max_all_time', 'mean_all_time'):
                setattr(self.response.payload, 'time_{}'.format(name), self.server.kvdb.conn.hget(time_key, name) or 0)

class Edit(AdminService):
    """ Updates a service.
    """
    class SimpleIO:
        input_required = ('id', 'is_active', Integer('slow_threshold'))
        output_required = ('id', 'name', 'impl_name', 'is_internal',)
        output_optional = ('usage',)

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                service = session.query(Service).filter_by(id=input.id).one()
                service.is_active = input.is_active
                service.slow_threshold = input.slow_threshold
                
                session.add(service)
                session.commit()
                
                input.action = SERVICE.EDIT
                input.impl_name = service.impl_name
                self.broker_client.publish(input)
                
                self.response.payload = service
                
            except Exception, e:
                msg = 'Could not update the service, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise         
            
class Delete(AdminService):
    """ Deletes a service
    """
    class SimpleIO:
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

                msg = {'action': SERVICE.DELETE, 'id': self.request.input.id, 'impl_name':service.impl_name, 
                       'is_internal':service.is_internal}
                self.broker_client.publish(msg)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the service, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise

class GetChannelList(AdminService):
    """ Returns a list of channels of a given type through which the service
    is being exposed.
    """
    class SimpleIO:
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
                q = q.filter(class_.soap_version != None)
            elif self.request.input.channel_type == 'plain_http':
                q = q.filter(class_.soap_version == None)
            
            self.response.payload[:] = q.all()
            
class Invoke(AdminService):
    """ Invokes the service directly, as though it was exposed through some channel
    which doesn't necessarily have to be true.
    """
    class SimpleIO:
        input_required = ('id', 'payload')
        input_optional = ('data_format', 'transport')
        output_required = ('response',)

    def handle(self):
        with closing(self.odb.session()) as session:
            service = session.query(Service).\
                filter(Service.id==self.request.input.id).\
                one()
            
        payload = payload_from_request(self.request.input.payload, self.request.input.data_format,
                        self.request.input.transport)
        
        service_instance = self.server.service_store.new_instance(service.impl_name)
        service_instance.update(service_instance, self.server, self.broker_client, 
            self.worker_store, self.cid, payload, self.request.input.payload, 
            self.request.input.transport, self.request.simple_io_config, 
            self.request.input.data_format, self.request.request_data)

        service_instance.pre_handle()
        service_instance.handle()
        
        response = service_instance.response.payload
        if not isinstance(response, basestring):
            response = response.getvalue()
            service_instance.response.payload = response
            
        service_instance.post_handle()
            
        self.response.payload.response = response

class GetDeploymentInfoList(AdminService):
    """ Returns detailed information regarding the service's deployment status
    on each of the servers it's been deployed to.
    """
    class SimpleIO:
        input_required = ('id',)
        output_required = ('server_id', 'server_name', 'details')
        
    def get_data(self, session):
        return session.query(DeployedService.details,
            Server.name.label('server_name'), 
            Server.id.label('server_id')).\
            outerjoin(Server, DeployedService.server_id==Server.id).\
            filter(DeployedService.service_id==self.request.input.id).\
            all()
        
    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)
            
class GetSourceInfo(AdminService):
    """ Returns information on the service's source code.
    """
    class SimpleIO:
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

class GetWSDL(AdminService):
    """ Returns a WSDL for the given service. Either uses a user-uploaded one,
    or, optionally generates one on fly if the service uses SimpleIO.
    """
    class SimpleIO:
        input_optional = ('service', 'cluster_id')
        output_optional = ('wsdl', 'wsdl_name', 'content_type')

    def handle(self):
        if self.request.request_data.query:
            use_sio = False
            query = parse_qs(self.request.request_data.query)
            service_name = query.get('service', (None,))[0]
            cluster_id = query.get('cluster_id', (None,))[0]
        else:
            use_sio = True
            service_name = self.request.input.service
            cluster_id = self.request.input.cluster_id
            
        if not(service_name and cluster_id):
            self.response.status_code = BAD_REQUEST
            self.response.payload = 'Both [service] and [cluster_id] parameters are required'
            return
        
        with closing(self.odb.session()) as session:
            service = session.query(Service).\
                filter_by(name=service_name, cluster_id=cluster_id).\
                first()
            
            if not service:
                self.response.status_code = NOT_FOUND
                self.response.payload = 'Service [{}] not found'.format(service_name)
                return
            
        content_type = guess_type(service.wsdl_name)[0] or 'application/octet-stream'
            
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
            
class SetWSDL(AdminService):
    """ Updates the service's WSDL.
    """
    class SimpleIO:
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
            
class HasWSDL(AdminService):
    """ Returns a boolean flag indicating whether the server has a WSDL attached.
    """
    class SimpleIO:
        input_required = ('name', 'cluster_id')
        output_required = ('service_id', 'has_wsdl',)
        
    def handle(self):
        with closing(self.odb.session()) as session:
            result = session.query(Service.id, Service.wsdl).\
                filter_by(name=self.request.input.name, cluster_id=self.request.input.cluster_id).\
                one()
            self.response.payload.service_id = result.id
            self.response.payload.has_wsdl = result.wsdl is not None

class GetRequestResponse(AdminService):
    """ Returns a sample request/response along with information on how often
    the pairs should be stored in the DB.
    """
    class SimpleIO:
        input_required = ('name', 'cluster_id')
        output_required = ('service_id', 'sample_cid', 'sample_req_ts', 'sample_resp_ts', 
            'sample_req', 'sample_resp', Integer('sample_req_resp_freq'))
        
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

class ConfigureRequestResponse(AdminService):
    """ Updates the request/response-related configuration.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'name', Integer('sample_req_resp_freq'))
        
    def handle(self):
        key = '{}{}'.format(KVDB.REQ_RESP_SAMPLE, self.request.input.name)
        self.kvdb.conn.hset(key, 'freq', self.request.input.sample_req_resp_freq)
            
class UploadPackage(AdminService):
    """ Returns a boolean flag indicating whether the server has a WSDL attached.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'payload_name', 'payload')
        
    def handle(self):
        with NamedTemporaryFile(prefix='zato-hd-', suffix=self.request.input.payload_name) as tf:
            tf.write(self.request.input.payload.decode('base64'))
            tf.flush()

            success = hot_deploy(self.server, self.request.input.payload_name, tf.name, False)
            
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
                    elem[name] = item.get(name, '').encode('base64')
                    
            data.append(elem)

        return data
            
class GetSlowResponseList(_SlowResponseService):
    """ Returns a list of basic information regarding slow responses of a given service.
    """
    class SimpleIO:
        input_required = ('name',)
        output_required = ('cid', 'req_ts', 'resp_ts', 'proc_time')
        
    def handle(self):
        self.response.payload[:] = self.get_data()    
        
class GetSlowResponse(_SlowResponseService):
    """ Returns information regading a particular slow response of a service.
    """
    class SimpleIO:
        input_required = ('cid', 'name')
        output_optional = ('cid', 'req_ts', 'resp_ts', 'proc_time', 'req', 'resp')
    
    def handle(self):
        data = self.get_data()
        if data:
            self.response.payload = data[0]

