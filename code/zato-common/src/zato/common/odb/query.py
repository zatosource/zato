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

from zato.common.odb.model import(ChannelURLDefinition, Cluster, ConnDef, 
    ConnDefAMQP, CronStyleJob, HTTPBasicAuth, IntervalBasedJob, Job,  Service,
    TechnicalAccount)

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

def soap_channel_list(session, cluster_id):
    """ SOAP channels.
    """
    return session.query(ChannelURLDefinition).\
        filter(Cluster.id==cluster_id).\
        filter(ChannelURLDefinition.url_type=='soap').\
        order_by(ChannelURLDefinition.url_pattern).\
        all()

def amqp_def_list(session, cluster_id):
    """ AMQP connection definitions.
    """
    return session.query(ConnDef.name, ConnDefAMQP.id, ConnDefAMQP.host,
                         ConnDefAMQP.port, ConnDefAMQP.vhost, ConnDefAMQP.username,
                         ConnDefAMQP.frame_max, ConnDefAMQP.heartbeat).\
        filter(Cluster.id==ConnDef.cluster_id).\
        filter(ConnDef.id==ConnDefAMQP.def_id).\
        filter(ConnDef.def_type=='amqp').\
        filter(Cluster.id==cluster_id).\
        order_by(ConnDef.name).\
        all()
