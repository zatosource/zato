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
from datetime import datetime, timedelta
from httplib import BAD_REQUEST, NOT_FOUND
from mimetypes import guess_type
from tempfile import NamedTemporaryFile
from traceback import format_exc
from urlparse import parse_qs

# validate
from validate import is_boolean

# Zato
from zato.common import KVDB, ZatoException
from zato.common.broker_message import MESSAGE_TYPE, SERVICE
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
        output_required = ('id', 'name', 'is_active', 'impl_name', 'is_internal', Boolean('may_be_deleted'), 'usage_count')
        output_repeated = True
        
    def get_data(self, session):
        out = []
        sl = service_list(session, self.request.input.cluster_id, False)
        
        internal_del = is_boolean(self.server.fs_server_config.misc.internal_services_may_be_deleted)
        
        for item in sl:
            item.may_be_deleted = internal_del if item.is_internal else True
            item.usage_count = self.server.kvdb.conn.get('{}{}'.format(KVDB.SERVICE_USAGE, item.name)) or 0
            
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
        output_required = ('id', 'name', 'is_active', 'impl_name', 'is_internal', 'usage_count', 
            'timer_last', 'timer_min_all_time', 'timer_max_all_time', 'timer_mean_all_time', 
            'timer_min_1h', 'timer_max_1h', 'timer_mean_1h', 'timer_rate_1h')
        
    def get_data(self, session):
        return session.query(Service.id, Service.name, Service.is_active,
            Service.impl_name, Service.is_internal).\
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
            self.response.payload.usage_count = self.server.kvdb.conn.get('{}{}'.format(KVDB.SERVICE_USAGE, service.name)) or 0

            timer_key = '{}{}'.format(KVDB.SERVICE_TIMER_BASIC, service.name)
            for name in('min_all_time', 'max_all_time', 'mean_all_time'):
                setattr(self.response.payload, 'timer_{}'.format(name), self.server.kvdb.conn.hget(timer_key, name) or 0)
                    
            self.response.payload.timer_last = self.server.kvdb.conn.hget(timer_key, 'last')
            self.response.payload.timer_min_1h = self.server.kvdb.conn.hget(timer_key, 'timer_min_1h') or 0
            self.response.payload.timer_max_1h = self.server.kvdb.conn.hget(timer_key, 'timer_max_1h') or 0
            self.response.payload.timer_mean_1h = self.server.kvdb.conn.hget(timer_key, 'timer_mean_1h') or 0
            self.response.payload.timer_rate_1h = self.server.kvdb.conn.hget(timer_key, 'timer_rate_1h') or 0

class Edit(AdminService):
    """ Updates a service.
    """
    class SimpleIO:
        input_required = ('id', 'is_active')
        output_required = ('id', 'name', 'impl_name', 'is_internal',)
        output_optional = (Boolean('usage_count'),)

    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                service = session.query(Service).filter_by(id=input.id).one()
                service.is_active = input.is_active
                
                session.add(service)
                session.commit()
                
                input.action = SERVICE.EDIT
                input.impl_name = service.impl_name
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
                
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
                self.broker_client.send_json(msg, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
                
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

        service_instance._pre_handle()
        service_instance.handle()
        service_instance._post_handle()
        
        response = service_instance.response.payload
        if not isinstance(response, basestring):
            response = response.getvalue()

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
        output_required = ('service_id', 'sample_cid', 'sample_req_timestamp', 'sample_resp_timestamp', 
            'sample_request', 'sample_response', Integer('sample_req_resp_freq'))
        
    def get_data(self, session):
        return session.query(Service.id, Service.sample_cid, Service.sample_req_timestamp,
            Service.sample_resp_timestamp, Service.sample_request, Service.sample_response,
            Service.sample_req_resp_freq).\
            filter_by(name=self.request.input.name, cluster_id=self.request.input.cluster_id).\
            one()
        
    def handle(self):
        with closing(self.odb.session()) as session:
            result = self.get_data(session)
            self.response.payload.service_id = result.id
            self.response.payload.sample_cid = result.sample_cid
            self.response.payload.sample_req_timestamp = result.sample_req_timestamp
            self.response.payload.sample_resp_timestamp = result.sample_resp_timestamp
            self.response.payload.sample_request = (result.sample_request if result.sample_request else '').encode('base64')
            self.response.payload.sample_response = (result.sample_response if result.sample_response else '').encode('base64')
            self.response.payload.sample_req_resp_freq = result.sample_req_resp_freq

class ConfigureRequestResponse(AdminService):
    """ Updates the request/response-related configuration.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'name', 'sample_req_resp_freq')
        
    def handle(self):
        with closing(self.odb.session()) as session:
            service = session.query(Service).\
                filter_by(name=self.request.input.name, cluster_id=self.request.input.cluster_id).\
                one()
            
            service.sample_req_resp_freq = int(self.request.input.sample_req_resp_freq)
            
            session.add(service)
            session.commit()
            
class SetRequestResponse(AdminService):
    """ Stores a new request/response pair.
    """
    def handle(self):
        with closing(self.odb.session()) as session:
            service = session.query(Service).\
                filter_by(id=self.request.payload.service_id).\
                one()
            
            service.sample_cid = self.request.payload.cid
            service.sample_req_timestamp = datetime.strptime(self.request.payload.req_timestamp, '%Y-%m-%dT%H:%M:%S.%f')
            service.sample_resp_timestamp = datetime.strptime(self.request.payload.resp_timestamp, '%Y-%m-%dT%H:%M:%S.%f')
            service.sample_request = self.request.payload.request.encode('utf-8')
            service.sample_response = self.request.payload.response.encode('utf-8')

            session.add(service)
            session.commit()
            
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

class GetLastStats(AdminService):
    """ Returns basic statistics regarding a service, going back up to the period,
    expressed in minutes. The data returned is:
    - usage count
    - mean response time
    - a BASE64-encoded sparkline depicting the mean response time's trend during the given period
    """
    class SimpleIO:
        input_required = ('service_id', 'minutes')
        output_required = ('min', 'max', 'mean', 'rate', 'trend')
        
    def handle(self):
        with closing(self.odb.session()) as session:
            service = session.query(Service).\
                filter_by(id=self.request.input.service_id).\
                one()
            
            minutes = int(self.request.input.minutes)
            now = datetime.utcnow()
            suffixes = ((now - timedelta(minutes=minute)).strftime('%Y:%m:%d:%H:%M') for minute in range(minutes, 1, -1))
            
            min_ = None
            max_ = None
            mean = 0
            rate = 0
            trend = []
            
            for suffix in suffixes:
                key = '{}{}:{}'.format(KVDB.SERVICE_TIMER_AGGREGATED_BY_MINUTE, service.name, suffix)
                items = self.server.kvdb.conn.hgetall(key)
                
                if items:
                    if not min_:
                        min_ = float(items['min'])
                    else:
                        min_ = min(min_, float(items['min']))
                        
                    if not max_:
                        max_ = float(items['max'])
                    else:
                        max_ = max(max_, float(items['max']))

                    mean += float(items['mean'])
                    rate += float(items['rate'])
                    trend.append(items['mean'])
                else:
                    trend.append('0')
                    
            mean = mean / float(minutes)
            if mean and mean < 1:
                mean = '1'
            else:
                mean = '{:.0f}'.format(mean)
                
            rate = rate / float(minutes)
            if rate and rate < 0.01:
                rate = '<0.01'
            else:
                rate = '{:.2f}'.format(rate)
            
            self.response.payload.min = min_
            self.response.payload.max = max_
            self.response.payload.mean = mean
            self.response.payload.rate = rate
            self.response.payload.trend = ','.join(trend)
