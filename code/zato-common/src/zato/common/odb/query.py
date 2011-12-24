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

from zato.common.odb.model import(ChannelAMQP, ChannelURLDefinition, ChannelWMQ,
    ChannelZMQ, Cluster, ConnDefAMQP, ConnDefWMQ, CronStyleJob, HTTPBasicAuth,
    HTTPSOAP, IntervalBasedJob, Job,  OutgoingAMQP,  OutgoingWMQ, OutgoingZMQ,
    Service, TechnicalAccount, WSSDefinition)

def job_list(session, cluster_id):
    """ All the scheduler's jobs defined in the ODB.
    """
    return session.query(Job.id, Job.name, Job.is_active,
        Job.job_type, Job.start_date,  Job.extra,
        Service.name.label('service_name'), Service.id.label('service_id'),
        IntervalBasedJob.weeks, IntervalBasedJob.days,
        IntervalBasedJob.hours, IntervalBasedJob.minutes,
        IntervalBasedJob.seconds, IntervalBasedJob.repeats,
        CronStyleJob.cron_definition).\
            outerjoin(IntervalBasedJob, Job.id==IntervalBasedJob.job_id).\
            outerjoin(CronStyleJob, Job.id==CronStyleJob.job_id).\
            filter(Cluster.id==cluster_id).\
            filter(Job.service_id==Service.id).\
            order_by('job.name').\
            all()

# ##############################################################################

def basic_auth_list(session, cluster_id):
    """ All the HTTP Basic Auth definitions.
    """
    return session.query(HTTPBasicAuth).\
        filter(Cluster.id==cluster_id).\
        order_by('http_basic_auth_def.name').\
        all()

def tech_acc_list(session, cluster_id):
    """ All the technical accounts.
    """
    return session.query(TechnicalAccount).\
        order_by(TechnicalAccount.name).\
        filter(Cluster.id==cluster_id).\
        all()

def wss_list(session, cluster_id):
    """ All the WS-Security definitions.
    """
    return session.query(WSSDefinition).\
        filter(Cluster.id==cluster_id).\
        order_by('wss_def.name').\
        all()

# ##############################################################################

def soap_channel_list(session, cluster_id):
    """ SOAP channels.
    """
    return session.query(ChannelURLDefinition).\
        filter(Cluster.id==cluster_id).\
        filter(ChannelURLDefinition.url_type=='soap').\
        order_by(ChannelURLDefinition.url_pattern).\
        all()

# ##############################################################################

def _def_amqp(session, cluster_id):
    return session.query(ConnDefAMQP.name, ConnDefAMQP.id, ConnDefAMQP.host,
            ConnDefAMQP.port, ConnDefAMQP.vhost, ConnDefAMQP.username,
            ConnDefAMQP.frame_max, ConnDefAMQP.heartbeat, ConnDefAMQP.password).\
        filter(Cluster.id==ConnDefAMQP.cluster_id).\
        filter(ConnDefAMQP.def_type=='amqp').\
        filter(Cluster.id==cluster_id).\
        order_by(ConnDefAMQP.name)

def def_amqp(session, cluster_id, def_id):
    """ A particular AMQP definition
    """
    return _def_amqp(session, cluster_id).\
           filter(ConnDefAMQP.id==def_id).\
           one()

def def_amqp_list(session, cluster_id):
    """ AMQP connection definitions.
    """
    return _def_amqp(session, cluster_id).all()

# ##############################################################################

def _def_jms_wmq(session, cluster_id):
    return session.query(ConnDefWMQ.id, ConnDefWMQ.name, ConnDefWMQ.host,
            ConnDefWMQ.port, ConnDefWMQ.queue_manager, ConnDefWMQ.channel,
            ConnDefWMQ.cache_open_send_queues, ConnDefWMQ.cache_open_receive_queues,
            ConnDefWMQ.use_shared_connections, ConnDefWMQ.ssl, ConnDefWMQ.ssl_cipher_spec,
            ConnDefWMQ.ssl_key_repository, ConnDefWMQ.needs_mcd, ConnDefWMQ.max_chars_printed).\
        filter(Cluster.id==ConnDefWMQ.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(ConnDefWMQ.name)

def def_jms_wmq(session, cluster_id, def_id):
    """ A particular JMS WebSphere MQ definition
    """
    return _def_jms_wmq(session, cluster_id).\
           filter(ConnDefWMQ.id==def_id).\
           one()

def def_jms_wmq_list(session, cluster_id):
    """ JMS WebSphere MQ connection definitions.
    """
    return _def_jms_wmq(session, cluster_id).all()

# ##############################################################################

def _out_amqp(session, cluster_id):
    return session.query(OutgoingAMQP.id, OutgoingAMQP.name, OutgoingAMQP.is_active,
            OutgoingAMQP.delivery_mode, OutgoingAMQP.priority, OutgoingAMQP.content_type,
            OutgoingAMQP.content_encoding, OutgoingAMQP.expiration, OutgoingAMQP.user_id,
            OutgoingAMQP.app_id, ConnDefAMQP.name.label('def_name'), OutgoingAMQP.def_id).\
        filter(OutgoingAMQP.def_id==ConnDefAMQP.id).\
        filter(ConnDefAMQP.id==OutgoingAMQP.def_id).\
        filter(Cluster.id==ConnDefAMQP.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(OutgoingAMQP.name)

def out_amqp(session, cluster_id, out_id):
    """ An outgoing AMQP connection.
    """
    return _out_amqp(session, cluster_id).\
           filter(OutgoingAMQP.id==out_id).\
           one()

def out_amqp_list(session, cluster_id):
    """ Outgoing AMQP connections.
    """
    return _out_amqp(session, cluster_id).all()

# ##############################################################################

def _out_jms_wmq(session, cluster_id):
    return session.query(OutgoingWMQ.id, OutgoingWMQ.name, OutgoingWMQ.is_active,
            OutgoingWMQ.delivery_mode, OutgoingWMQ.priority, OutgoingWMQ.expiration,
            ConnDefWMQ.name.label('def_name'), OutgoingWMQ.def_id).\
        filter(OutgoingWMQ.def_id==ConnDefWMQ.id).\
        filter(ConnDefWMQ.id==OutgoingWMQ.def_id).\
        filter(Cluster.id==ConnDefWMQ.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(OutgoingWMQ.name)

def out_jms_wmq(session, cluster_id, out_id):
    """ An outgoing JMS WebSphere MQ connection.
    """
    return _out_jms_wmq(session, cluster_id).\
           filter(OutgoingWMQ.id==out_id).\
           one()

def out_jms_wmq_list(session, cluster_id):
    """ Outgoing JMS WebSphere MQ connections.
    """
    return _out_jms_wmq(session, cluster_id).all()

# ##############################################################################

def _channel_amqp(session, cluster_id):
    return session.query(ChannelAMQP.id, ChannelAMQP.name, ChannelAMQP.is_active,
            ChannelAMQP.queue, ChannelAMQP.consumer_tag_prefix,
            ConnDefAMQP.name.label('def_name'), ChannelAMQP.def_id,
            Service.name.label('service_name')).\
        filter(ChannelAMQP.def_id==ConnDefAMQP.id).\
        filter(ChannelAMQP.service_id==Service.id).\
        filter(Cluster.id==ConnDefAMQP.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(ChannelAMQP.name)

def channel_amqp(session, cluster_id, channel_id):
    """ A particular AMQP channel.
    """
    return _channel_amqp(session, cluster_id).\
           filter(ChannelAMQP.id==channel_id).\
           one()

def channel_amqp_list(session, cluster_id):
    """ AMQP channels.
    """
    return _channel_amqp(session, cluster_id).all()

# ##############################################################################

def _channel_jms_wmq(session, cluster_id):
    return session.query(ChannelWMQ.id, ChannelWMQ.name, ChannelWMQ.is_active,
            ChannelWMQ.queue, ConnDefWMQ.name.label('def_name'), ChannelWMQ.def_id,
            Service.name.label('service_name')).\
        filter(ChannelWMQ.def_id==ConnDefWMQ.id).\
        filter(ChannelWMQ.service_id==Service.id).\
        filter(Cluster.id==ConnDefWMQ.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(ChannelWMQ.name)

def channel_jms_wmq(session, cluster_id, channel_id):
    """ A particular JMS WebSphere MQ channel.
    """
    return _channel_jms_wmq(session, cluster_id).\
           filter(ChannelWMQ.id==channel_id).\
           one()

def channel_jms_wmq_list(session, cluster_id):
    """ JMS WebSphere MQ channels.
    """
    return _channel_jms_wmq(session, cluster_id).all()

# ##############################################################################

def _out_zmq(session, cluster_id):
    return session.query(OutgoingZMQ.id, OutgoingZMQ.name, OutgoingZMQ.is_active,
            OutgoingZMQ.address, OutgoingZMQ.socket_type).\
        filter(Cluster.id==OutgoingZMQ.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(OutgoingZMQ.name)

def out_zmq(session, cluster_id, out_id):
    """ An outgoing ZeroMQ connection.
    """
    return _out_zmq(session, cluster_id).\
           filter(OutgoingZMQ.id==out_id).\
           one()

def out_zmq_list(session, cluster_id):
    """ Outgoing ZeroMQ connections.
    """
    return _out_zmq(session, cluster_id).all()

# ##############################################################################

def _channel_zmq(session, cluster_id):
    return session.query(ChannelZMQ.id, ChannelZMQ.name, ChannelZMQ.is_active,
            ChannelZMQ.address, ChannelZMQ.socket_type, ChannelZMQ.sub_key).\
        filter(Cluster.id==ChannelZMQ.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(ChannelZMQ.name)

def channel_zmq(session, cluster_id, out_id):
    """ An incoming ZeroMQ connection.
    """
    return _channel_zmq(session, cluster_id).\
           filter(ChannelZMQ.id==out_id).\
           one()

def channel_zmq_list(session, cluster_id):
    """ Incoming ZeroMQ connections.
    """
    return _channel_zmq(session, cluster_id).all()

# ##############################################################################

def _http_soap(session, cluster_id):
    return session.query(HTTPSOAP.id, HTTPSOAP.name, HTTPSOAP.is_active,
            HTTPSOAP.url_path, HTTPSOAP.method, HTTPSOAP.soap_action,
            HTTPSOAP.soap_version).\
        filter(Cluster.id==HTTPSOAP.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(HTTPSOAP.name)

def http_soap(session, cluster_id, out_id):
    """ An HTTP/SOAP connection.
    """
    return _http_soap(session, cluster_id).\
           filter(HTTPSOAP.id==out_id).\
           one()

def http_soap_list(session, cluster_id):
    """ HTTP/SOAP connections.
    """
    return _http_soap(session, cluster_id).all()

# ##############################################################################