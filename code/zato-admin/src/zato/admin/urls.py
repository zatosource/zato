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
from zato.admin.web.views import(cluster, load_balancer, main, scheduler, 
    service, servers)
from zato.admin.web.views.channel import soap
from zato.admin.web.views.channel import amqp as channel_amqp
from zato.admin.web.views.definition import amqp as def_amqp
from zato.admin.web.views.definition import jms_wmq as def_jms_wmq
from zato.admin.web.views.outgoing import amqp as out_amqp
from zato.admin.web.views.outgoing import jms_wmq as out_jms_wmq
from zato.admin.web.views.pool import sql
from zato.admin.web.views.security import basic_auth, tech_account, wss


urlpatterns = patterns('',

    # Main URLs
    (r'^accounts/login/$', login, {'template_name': 'zato/login.html'}),
    (r'^$', main.index_redirect),
    url(r'^zato/$', main.index, name='main-page'),
    url(r'^logout/$', main.logout, name='logout'),
    url(r'^accounts/self$', main.my_account, name='accounts-self'),

    # Clusters.
    url(r'^zato/cluster/$', cluster.index, name='cluster'),
    url(r'^zato/cluster/create/$', cluster.create, name='cluster-create'),
    url(r'^zato/cluster/edit/$', cluster.edit, name='cluster-edit'),
    url(r'^zato/cluster/delete/(?P<cluster_id>.*)/$', cluster.delete, name='cluster-delete'),
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

    # Servers registry.
    url(r'^zato/servers/$', servers.index, name='servers'),
    url(r'^zato/servers/status/(?P<server_id>.*)$', servers.status, name='server-status'),
    url(r'^zato/servers/ping/(?P<server_id>.*)$', servers.ping, name='server-ping'),
    url(r'^zato/servers/unregister/(?P<server_id>.*)$', servers.unregister, name='server-unregister'),

    # Services.
    url(r'^zato/service/$', service.index, name='service'),
    url(r'^zato/service/details/(?P<server_id>\d*)/(?P<service_name>.*)/invoke/$', service.invoke, name='service-invoke'),
    url(r'^zato/service/details/(?P<server_id>\d*)/(?P<service_name>.*)/$', service.details, name='service-details'),

    # Channels.
    url(r'^zato/channel/soap/$', soap.index, name='channel-soap'),
    url(r'^zato/channel/soap/create/$', basic_auth.create, name='channel-soap-create'),
    url(r'^zato/channel/soap/edit/$', basic_auth.edit, name='channel-soap-edit'),

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
    url(r'^zato/security/tech-account/delete/(?P<tech_account_id>.*)/cluster/(?P<cluster_id>.*)/$', tech_account.delete, name='security-tech-account-delete'),
    
    # .. WS-Security
    url(r'^zato/security/wss/$', wss.index, name='security-wss'),
    url(r'^zato/security/wss/create/$', wss.create, name='security-wss-create'),
    url(r'^zato/security/wss/edit/$', wss.edit, name='security-wss-edit'),
    url(r'^zato/security/wss/change-password/$', wss.change_password, name='security-wss-change-password'),
    url(r'^zato/security/wss/delete/(?P<wss_id>.*)/cluster/(?P<cluster_id>.*)/$', wss.delete, name='security-wss-delete'),

    # SQL connection pools.
    url(r'^zato/pool/sql/$', sql.index, name='pool-sql'),
    url(r'^zato/pool/sql/ping/$', sql.ping, name='pool-sql-ping'),
    url(r'^zato/pool/sql/delete/$', sql.delete, name='pool-sql-delete'),

    # Scheduler
    url(r'^zato/scheduler/$', scheduler.index, name='scheduler'),
    url(r'^zato/scheduler/delete/(?P<job_id>.*)/cluster/(?P<cluster_id>.*)/$', scheduler.delete, name='scheduler-job-delete'),
    url(r'^zato/scheduler/execute/(?P<job_id>.*)/cluster/(?P<cluster_id>.*)/$', scheduler.execute, name='scheduler-job-execute'),
    url(r'^zato/scheduler/get-definition/(?P<start_date>.*)/(?P<repeat>.*)/'
        '(?P<weeks>.*)/(?P<days>.*)/(?P<hours>.*)/(?P<minutes>.*)/(?P<seconds>.*)/$',
        scheduler.get_definition, name='scheduler-job-get-definition'),

    # Definitions
    
    # .. AMQP
    url(r'^zato/definition/amqp/$', def_amqp.index, name='def-amqp'),
    url(r'^zato/definition/amqp/create/$', def_amqp.create, name='def-amqp-create'),
    url(r'^zato/definition/amqp/edit/$', def_amqp.edit, name='def-amqp-edit'),
    url(r'^zato/definition/amqp/change-password/$', def_amqp.change_password, name='def-amqp-change-password'),
    url(r'^zato/definition/amqp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', def_amqp.delete, name='def-amqp-delete'),
    
    # .. JMS WebSphere MQ
    url(r'^zato/definition/jms-wmq/$', def_jms_wmq.index, name='def-jms-wmq'),
    url(r'^zato/definition/jms-wmq/create/$', def_jms_wmq.create, name='def-jms-wmq-create'),
    url(r'^zato/definition/jms-wmq/edit/$', def_jms_wmq.edit, name='def-jms-wmq-edit'),
    url(r'^zato/definition/jms-wmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', def_jms_wmq.delete, name='def-jms-wmq-delete'),
    
    # Outgoing connections
    
    # .. AMQP
    url(r'^zato/outgoing/amqp/$', out_amqp.index, name='out-amqp'),
    url(r'^zato/outgoing/amqp/create/$', out_amqp.create, name='out-amqp-create'),
    url(r'^zato/outgoing/amqp/edit/$', out_amqp.edit, name='out-amqp-edit'),
    url(r'^zato/outgoing/amqp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', out_amqp.delete, name='out-amqp-delete'),
    
    # .. JMS WebSphere MQ
    url(r'^zato/outgoing/jms-wmq/$', out_jms_wmq.index, name='out-jms-wmq'),
    url(r'^zato/outgoing/jms-wmq/create/$', out_jms_wmq.create, name='out-jms-wmq-create'),
    url(r'^zato/outgoing/jms-wmq/edit/$', out_jms_wmq.edit, name='out-jms-wmq-edit'),
    url(r'^zato/outgoing/jms-wmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', out_jms_wmq.delete, name='out-jms-wmq-delete'),
    
    # Channels
    
    # .. AMQP
    url(r'^zato/channel/amqp/$', channel_amqp.index, name='channel-amqp'),
    url(r'^zato/channel/amqp/create/$', channel_amqp.create, name='channel-amqp-create'),
    url(r'^zato/channel/amqp/edit/$', channel_amqp.edit, name='channel-amqp-edit'),
    url(r'^zato/channel/amqp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', channel_amqp.delete, name='channel-amqp-delete'),
    
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

