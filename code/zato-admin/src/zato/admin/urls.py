# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

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

# Django
from django.conf.urls.defaults import *
from django.contrib.auth.views import login

# Zato
from zato.admin import settings
from zato.admin.web.views import cluster, load_balancer, main, scheduler, \
    service, servers
from zato.admin.web.views.channel import amqp as channel_amqp
from zato.admin.web.views.channel import jms_wmq as channel_jms_wmq
from zato.admin.web.views.channel import zmq as channel_zmq
from zato.admin.web.views.definition import amqp as def_amqp
from zato.admin.web.views.definition import jms_wmq as def_jms_wmq
from zato.admin.web.views import http_soap
from zato.admin.web.views.outgoing import amqp as out_amqp
from zato.admin.web.views.outgoing import ftp as out_ftp
from zato.admin.web.views.outgoing import jms_wmq as out_jms_wmq
from zato.admin.web.views.outgoing import sql as out_sql
from zato.admin.web.views.outgoing import zmq as out_zmq
from zato.admin.web.views.security import basic_auth, tech_account, wss


urlpatterns = patterns('',

    # Main URLs
    (r'^accounts/login/$', login, {'template_name': 'zato/login.html'}),
    (r'^$', main.index_redirect),
    url(r'^zato/$', main.index, name='main-page'),
    url(r'^logout/$', main.logout, name='logout'),
    url(r'^accounts/self$', main.my_account, name='accounts-self'),

    # Clusters
    url(r'^zato/cluster/$', cluster.index, name='cluster'),
    url(r'^zato/cluster/create/$', cluster.create, name='cluster-create'),
    url(r'^zato/cluster/edit/$', cluster.edit, name='cluster-edit'),
    url(r'^zato/cluster/delete/(?P<id>.*)/$', cluster.delete, name='cluster-delete'),
    url(r'^zato/cluster/servers-state/(?P<cluster_id>.*)$', cluster.get_servers_state, name='cluster-servers-state'),
    url(r'^zato/cluster/get/by-id/(?P<cluster_id>.*)$', cluster.get_by_id, name='cluster-get-by-id'),
    url(r'^zato/cluster/get/by-name/(?P<cluster_name>.*)/$', cluster.get_by_name, name='cluster-get-by-name'),

    # Load balancer
    url(r'^zato/load-balancer/get-addresses/cluster/(?P<cluster_id>.*)/$', load_balancer.get_addresses, name='lb-get-addresses'),
    url(r'^zato/load-balancer/manage/cluster/(?P<cluster_id>\d+)/validate-save/$', load_balancer.validate_save, name='lb-manage-validate-save'),
    url(r'^zato/load-balancer/manage/cluster/(?P<cluster_id>.*)/$', load_balancer.manage, name='lb-manage'),
    url(r'^zato/load-balancer/manage/source-code/cluster/(?P<cluster_id>.*)/validate-save$', load_balancer.validate_save_source_code, name='lb-manage-source-code-validate-save'),
    url(r'^zato/load-balancer/manage/source-code/cluster/(?P<cluster_id>.*)/$', load_balancer.manage_source_code, name='lb-manage-source-code'),
    url(r'^zato/load-balancer/remote-command/(?P<cluster_id>.*)/$', load_balancer.remote_command, name='lb-remote-command'),

    # TODO: 'servers' should be 'server'

    # Servers registry
    url(r'^zato/servers/$', servers.index, name='servers'),
    url(r'^zato/servers/status/(?P<server_id>.*)$', servers.status, name='server-status'),
    url(r'^zato/servers/ping/(?P<server_id>.*)$', servers.ping, name='server-ping'),
    url(r'^zato/servers/unregister/(?P<server_id>.*)$', servers.unregister, name='server-unregister'),

    # Services
    url(r'^zato/service/$', service.Index(), name=service.Index.url_name),
    url(r'^zato/service/soureces/$', service.sources, name='service-sources'),
    url(r'^zato/service/create/$', service.create, name='service-create'),
    url(r'^zato/service/edit/$', service.Edit(), name=service.Edit.url_name),
    url(r'^zato/service/invoke/(?P<service_id>.*)/cluster/(?P<cluster_id>.*)/$', service.invoke, name='service-invoke'),
    url(r'^zato/service/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', service.Delete(), name=service.Delete.url_name),
    url(r'^zato/service/details/(?P<service_name>.*)/$', service.details, name='service-details'),
    url(r'^zato/service/source-info/(?P<service_name>.*)/$', service.source_info, name='service-source-info'),
    url(r'^zato/service/wsdl/(?P<service_name>.*)/cluster/(?P<cluster_id>.*)/upload/$', service.wsdl_upload, name='service-wsdl-upload'),
    url(r'^zato/service/wsdl/(?P<service_name>.*)/cluster/(?P<cluster_id>.*)/download/$', service.wsdl_download, name='service-wsdl-download'),
    url(r'^zato/service/wsdl/(?P<service_name>.*)/$', service.wsdl, name='service-wsdl'),
    url(r'^zato/service/request-response/(?P<service_name>.*)/cluster/(?P<cluster_id>.*)/configure/$', service.request_response_configure, name='service-request-response-configure'),
    url(r'^zato/service/request-response/(?P<service_name>.*)/$', service.request_response, name='service-request-response'),

    # Security..

    # .. HTTP Basic Auth
    url(r'^zato/security/basic-auth/$', basic_auth.index, name='security-basic-auth'),
    url(r'^zato/security/basic-auth/create/$', basic_auth.create, name='security-basic-auth-create'),
    url(r'^zato/security/basic-auth/edit/$', basic_auth.edit, name='security-basic-auth-edit'),
    url(r'^zato/security/basic-auth/change-password/$', basic_auth.change_password, name='security-basic-auth-change-password'),
    url(r'^zato/security/basic-auth/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', basic_auth.delete, name='security-basic-auth-delete'),

    # .. Technical accounts
    url(r'^zato/security/tech-account/$', tech_account.index, name='security-tech-account'),
    url(r'^zato/security/tech-account/create/$', tech_account.create, name='security-tech-account-create'),
    url(r'^zato/security/tech-account/edit/$', tech_account.edit, name='security-tech-account-edit'),
    url(r'^zato/security/tech-account/change-password/$', tech_account.change_password, name='security-tech-account-change-password'),
    url(r'^zato/security/tech-account/get/by-id/(?P<tech_account_id>.*)/cluster/(?P<cluster_id>.*)/$', tech_account.get_by_id, name='security-tech-account-get-by-id'),
    url(r'^zato/security/tech-account/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', tech_account.delete, name='security-tech-account-delete'),

    # .. WS-Security
    url(r'^zato/security/wss/$', wss.index, name='security-wss'),
    url(r'^zato/security/wss/create/$', wss.create, name='security-wss-create'),
    url(r'^zato/security/wss/edit/$', wss.edit, name='security-wss-edit'),
    url(r'^zato/security/wss/change-password/$', wss.change_password, name='security-wss-change-password'),
    url(r'^zato/security/wss/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', wss.delete, name='security-wss-delete'),

    # Scheduler
    url(r'^zato/scheduler/$', scheduler.index, name='scheduler'),
    url(r'^zato/scheduler/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', scheduler.Delete(), name=scheduler.Delete.url_name),
    url(r'^zato/scheduler/execute/(?P<job_id>.*)/cluster/(?P<cluster_id>.*)/$', scheduler.execute, name='scheduler-job-execute'),
    url(r'^zato/scheduler/get-definition/(?P<start_date>.*)/(?P<repeat>.*)/'
        '(?P<weeks>.*)/(?P<days>.*)/(?P<hours>.*)/(?P<minutes>.*)/(?P<seconds>.*)/$',
        scheduler.get_definition, name='scheduler-job-get-definition'),

    # Definitions

    # .. AMQP
    url(r'^zato/definition/amqp/$', def_amqp.Index(), name=def_amqp.Index.url_name),
    url(r'^zato/definition/amqp/create/$', def_amqp.Create(), name=def_amqp.Create.url_name),
    url(r'^zato/definition/amqp/edit/$', def_amqp.Edit(), name=def_amqp.Edit.url_name),
    url(r'^zato/definition/amqp/change-password/$', def_amqp.change_password, name='def-amqp-change-password'),
    url(r'^zato/definition/amqp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', def_amqp.Delete(), name=def_amqp.Delete.url_name),

    # .. JMS WebSphere MQ
    url(r'^zato/definition/jms-wmq/$', def_jms_wmq.Index(), name=def_jms_wmq.Index.url_name),
    url(r'^zato/definition/jms-wmq/create/$', def_jms_wmq.Create(), name=def_jms_wmq.Create.url_name),
    url(r'^zato/definition/jms-wmq/edit/$', def_jms_wmq.Edit(), name=def_jms_wmq.Edit.url_name),
    url(r'^zato/definition/jms-wmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', def_jms_wmq.Delete(), name=def_jms_wmq.Delete.url_name),

    # Outgoing connections

    # .. AMQP
    url(r'^zato/outgoing/amqp/$', out_amqp.Index(), name=out_amqp.Index.url_name),
    url(r'^zato/outgoing/amqp/create/$', out_amqp.create, name='out-amqp-create'),
    url(r'^zato/outgoing/amqp/edit/$', out_amqp.edit, name='out-amqp-edit'),
    url(r'^zato/outgoing/amqp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', out_amqp.Delete(), name=out_amqp.Delete.url_name),
    
    # .. FTP
    url(r'^zato/outgoing/ftp/$', out_ftp.Index(), name=out_ftp.Index.url_name),
    url(r'^zato/outgoing/ftp/create/$', out_ftp.Create(), name=out_ftp.Create.url_name),
    url(r'^zato/outgoing/ftp/edit/$', out_ftp.Edit(), name=out_ftp.Edit.url_name),
    url(r'^zato/outgoing/ftp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', out_ftp.Delete(), name=out_ftp.Delete.url_name),
    url(r'^zato/outgoing/ftp/change-password/$', out_ftp.change_password, name='out-ftp-change-password'),

    # .. JMS WebSphere MQ
    url(r'^zato/outgoing/jms-wmq/$', out_jms_wmq.index, name='out-jms-wmq'),
    url(r'^zato/outgoing/jms-wmq/create/$', out_jms_wmq.create, name='out-jms-wmq-create'),
    url(r'^zato/outgoing/jms-wmq/edit/$', out_jms_wmq.edit, name='out-jms-wmq-edit'),
    url(r'^zato/outgoing/jms-wmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', out_jms_wmq.Delete(), name=out_jms_wmq.Delete.url_name),
    
    # SQL connection pools
    url(r'^zato/outgoing/sql/$', out_sql.index, name='out-sql'),
    url(r'^zato/outgoing/sql/create/$', out_sql.create, name='out-sql-create'),
    url(r'^zato/outgoing/sql/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', out_sql.ping, name='out-sql-ping'),
    url(r'^zato/outgoing/sql/edit/$', out_sql.edit, name='out-sql-edit'),
    url(r'^zato/outgoing/sql/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', out_sql.delete, name='out-sql-delete'),
    url(r'^zato/outgoing/sql/change-password/$', out_sql.change_password, name='out-sql-change-password'),
    
    # .. ZeroMQ
    url(r'^zato/outgoing/zmq/$', out_zmq.index, name='out-zmq'),
    url(r'^zato/outgoing/zmq/create/$', out_zmq.create, name='out-zmq-create'),
    url(r'^zato/outgoing/zmq/edit/$', out_zmq.edit, name='out-zmq-edit'),
    url(r'^zato/outgoing/zmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', out_zmq.delete, name='out-zmq-delete'),

    # Channels

    # .. AMQP
    url(r'^zato/channel/amqp/$', channel_amqp.index, name='channel-amqp'),
    url(r'^zato/channel/amqp/create/$', channel_amqp.create, name='channel-amqp-create'),
    url(r'^zato/channel/amqp/edit/$', channel_amqp.edit, name='channel-amqp-edit'),
    url(r'^zato/channel/amqp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', channel_amqp.delete, name='channel-amqp-delete'),

    # .. JMS WebSphere MQ
    url(r'^zato/channel/jms-wmq/$', channel_jms_wmq.index, name='channel-jms-wmq'),
    url(r'^zato/channel/jms-wmq/create/$', channel_jms_wmq.create, name='channel-jms-wmq-create'),
    url(r'^zato/channel/jms-wmq/edit/$', channel_jms_wmq.edit, name='channel-jms-wmq-edit'),
    url(r'^zato/channel/jms-wmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', channel_jms_wmq.delete, name='channel-jms-wmq-delete'),

    # .. ZeroMQ
    url(r'^zato/channel/zmq/$', channel_zmq.index, name='channel-zmq'),
    url(r'^zato/channel/zmq/create/$', channel_zmq.create, name='channel-zmq-create'),
    url(r'^zato/channel/zmq/edit/$', channel_zmq.edit, name='channel-zmq-edit'),
    url(r'^zato/channel/zmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', channel_zmq.delete, name='channel-zmq-delete'),

    # HTTP/SOAP
    url(r'^zato/http-soap/$', http_soap.index, name='http-soap'),
    url(r'^zato/http-soap/create/$', http_soap.create, name='http-soap-create'),
    url(r'^zato/http-soap/edit/$', http_soap.edit, name='http-soap-edit'),
    url(r'^zato/http-soap/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', http_soap.delete, name='http-soap-delete'),
    url(r'^zato/http-soap/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', http_soap.ping, name='http-soap-ping'),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

