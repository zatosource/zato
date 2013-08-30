# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django.conf.urls.defaults import * # noqa
from django.contrib.auth.views import login

# Zato
from zato.admin import settings
from zato.admin.web.views import account, cluster, http_soap, kvdb, load_balancer, main, scheduler, service, stats
from zato.admin.web.views.channel import amqp as channel_amqp
from zato.admin.web.views.channel import jms_wmq as channel_jms_wmq
from zato.admin.web.views.channel import zmq as channel_zmq
from zato.admin.web.views.definition import amqp as def_amqp
from zato.admin.web.views.definition import jms_wmq as def_jms_wmq
from zato.admin.web.views.kvdb.data_dict import dictionary, impexp, translation
from zato.admin.web.views.outgoing import amqp as out_amqp
from zato.admin.web.views.outgoing import ftp as out_ftp
from zato.admin.web.views.outgoing import jms_wmq as out_jms_wmq
from zato.admin.web.views.outgoing import sql as out_sql
from zato.admin.web.views.outgoing import zmq as out_zmq
from zato.admin.web.views.pattern import delivery as pattern_delivery
from zato.admin.web.views.pattern.delivery import definition as pattern_delivery_def
from zato.admin.web.views.security import basic_auth, tech_account, wss


urlpatterns = patterns('',

    # Main URLs
    (r'^accounts/login/$', login, {'template_name': 'zato/login.html'}),
    (r'^$', main.index_redirect),
    url(r'^zato/$', main.index, name='main-page'),
    url(r'^logout/$', main.logout, name='logout'),
    
    # User accounts
    url(r'^account/settings/basic/$', account.settings_basic, name='account-settings-basic'),
    url(r'^account/settings/basic/save/$', account.settings_basic_save, name='account-settings-basic-save'),

    # Clusters
    url(r'^zato/cluster/$', cluster.index, name='cluster'),
    url(r'^zato/cluster/edit/$', cluster.edit, name='cluster-edit'),
    url(r'^zato/cluster/delete/(?P<id>.*)/$', cluster.delete, name='cluster-delete'),
    url(r'^zato/cluster/servers-state/(?P<cluster_id>.*)$', cluster.get_servers_state, name='cluster-servers-state'),
    url(r'^zato/cluster/get/by-id/(?P<cluster_id>.*)$', cluster.get_by_id, name='cluster-get-by-id'),
    url(r'^zato/cluster/get/by-name/(?P<cluster_name>.*)/$', cluster.get_by_name, name='cluster-get-by-name'),
    url(r'^zato/cluster/servers/$', cluster.servers, name='cluster-servers'),
    url(r'^zato/cluster/servers/edit/$', cluster.servers_edit, name='cluster-servers-edit'),
    url(r'^zato/cluster/servers/load-balancer/(?P<action>.*)/(?P<server_id>.*)/$', 
        cluster.servers_add_remove_lb, name='cluster-servers-add-remove-lb'),
    url(r'^zato/cluster/servers/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        cluster.ServerDelete(), name=cluster.ServerDelete.url_name),

    # Load balancer
    url(r'^zato/load-balancer/get-addresses/cluster/(?P<cluster_id>.*)/$', 
        load_balancer.get_addresses, name='lb-get-addresses'),
    url(r'^zato/load-balancer/manage/cluster/(?P<cluster_id>\d+)/validate-save/$', 
        load_balancer.validate_save, name='lb-manage-validate-save'),
    url(r'^zato/load-balancer/manage/cluster/(?P<cluster_id>.*)/$', load_balancer.manage, name='lb-manage'),
    url(r'^zato/load-balancer/manage/source-code/cluster/(?P<cluster_id>.*)/validate-save$', 
        load_balancer.validate_save_source_code, name='lb-manage-source-code-validate-save'),
    url(r'^zato/load-balancer/manage/source-code/cluster/(?P<cluster_id>.*)/$', 
        load_balancer.manage_source_code, name='lb-manage-source-code'),
    url(r'^zato/load-balancer/remote-command/(?P<cluster_id>.*)/$', 
        load_balancer.remote_command, name='lb-remote-command'),

    # Services
    url(r'^zato/service/$', service.Index(), name=service.Index.url_name),
    url(r'^zato/service/last-stats/(?P<service_id>.*)/cluster/(?P<cluster_id>.*)/$', 
        service.last_stats, name='service-last-stats'),
    url(r'^zato/service/cluster/(?P<cluster_id>.*)/upload/$', service.package_upload, name='service-package-upload'),
    url(r'^zato/service/create/$', service.create, name='service-create'),
    url(r'^zato/service/edit/$', service.Edit(), name=service.Edit.url_name),
    url(r'^zato/service/invoke/(?P<name>.*)/cluster/(?P<cluster_id>.*)/$', service.invoke, name='service-invoke'),
    url(r'^zato/service/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', service.Delete(), name=service.Delete.url_name),
    url(r'^zato/service/overview/(?P<service_name>.*)/$', service.overview, name='service-overview'),
    url(r'^zato/service/invoker/(?P<service_name>.*)/$', service.invoker, name='service-invoker'),
    url(r'^zato/service/source-info/(?P<service_name>.*)/$', service.source_info, name='service-source-info'),
    url(r'^zato/service/wsdl/(?P<service_name>.*)/cluster/(?P<cluster_id>.*)/upload/$', 
        service.wsdl_upload, name='service-wsdl-upload'),
    url(r'^zato/service/wsdl/(?P<service_name>.*)/cluster/(?P<cluster_id>.*)/download/$', 
        service.wsdl_download, name='service-wsdl-download'),
    url(r'^zato/service/wsdl/(?P<service_name>.*)/$', service.wsdl, name='service-wsdl'),
    url(r'^zato/service/request-response/(?P<service_name>.*)/cluster/(?P<cluster_id>.*)/configure/$', 
        service.request_response_configure, name='service-request-response-configure'),
    url(r'^zato/service/request-response/(?P<service_name>.*)/$', 
        service.request_response, name='service-request-response'),
    url(r'^zato/service/slow-response/details/(?P<cid>.*)/(?P<service_name>.*)/$', 
        service.slow_response_details, name='service-slow-response-details'),
    url(r'^zato/service/slow-response/(?P<service_name>.*)/$', service.slow_response, name='service-slow-response'),

    # Patterns ..
    
    # Delivery

    url(r'^zato/pattern/delivery/(?P<def_name>.*)/(?P<target_type>.*)/(?P<target>.*)/(?P<state>.*)/(?P<cluster_id>.*)/$', pattern_delivery.Index(), name=pattern_delivery.Index.url_name),
    url(r'^zato/pattern/delivery/delete/(?P<task_id>.*)/(?P<cluster_id>.*)/$', pattern_delivery.Delete(), name=pattern_delivery.Delete.url_name),
    url(r'^zato/pattern/delivery/delete-many/(?P<cluster_id>.*)/$', pattern_delivery.delete_many, name='pattern-delivery-delete-many'),
    url(r'^zato/pattern/delivery/details/(?P<task_id>.*)/$', pattern_delivery.Details(), name=pattern_delivery.Details.url_name),
    url(r'^zato/pattern/delivery/edit/(?P<task_id>.*)/(?P<cluster_id>.*)/$', pattern_delivery.Edit(), name=pattern_delivery.Edit.url_name),
    url(r'^zato/pattern/delivery/resubmit/(?P<task_id>.*)/(?P<cluster_id>.*)/$', pattern_delivery.Resubmit(), name=pattern_delivery.Resubmit.url_name),
    url(r'^zato/pattern/delivery/resubmit-many/(?P<cluster_id>.*)/$', pattern_delivery.resubmit_many, name='pattern-delivery-resubmit-many'),
    
    url(r'^zato/pattern/delivery/definition/$', pattern_delivery_def.Index(), name=pattern_delivery_def.Index.url_name),
    url(r'^zato/pattern/delivery/definition/create/$', pattern_delivery_def.Create(), name=pattern_delivery_def.Create.url_name),
    url(r'^zato/pattern/delivery/definition/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', pattern_delivery_def.Delete(), name=pattern_delivery_def.Delete.url_name),
    url(r'^zato/pattern/delivery/definition/edit/$', pattern_delivery_def.Edit(), name=pattern_delivery_def.Edit.url_name),
    
    # Security..

    # .. HTTP Basic Auth
    url(r'^zato/security/basic-auth/$', basic_auth.Index(), name=basic_auth.Index.url_name),
    url(r'^zato/security/basic-auth/create/$', basic_auth.Create(), name=basic_auth.Create.url_name),
    url(r'^zato/security/basic-auth/edit/$', basic_auth.Edit(), name=basic_auth.Edit.url_name),
    url(r'^zato/security/basic-auth/change-password/$', 
        basic_auth.change_password, name='security-basic-auth-change-password'),
    url(r'^zato/security/basic-auth/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        basic_auth.Delete(), name=basic_auth.Delete.url_name),

    # .. Technical accounts
    url(r'^zato/security/tech-account/$', tech_account.Index(), name=tech_account.Index.url_name),
    url(r'^zato/security/tech-account/create/$', tech_account.Create(), name=tech_account.Create.url_name),
    url(r'^zato/security/tech-account/edit/$', tech_account.Edit(), name=tech_account.Edit.url_name),
    url(r'^zato/security/tech-account/change-password/$', 
        tech_account.change_password, name='security-tech-account-change-password'),
    url(r'^zato/security/tech-account/get/by-id/(?P<tech_account_id>.*)/cluster/(?P<cluster_id>.*)/$', 
        tech_account.get_by_id, name='security-tech-account-get-by-id'),
    url(r'^zato/security/tech-account/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        tech_account.delete, name='security-tech-account-delete'),

    # .. WS-Security
    url(r'^zato/security/wss/$', wss.index, name='security-wss'),
    url(r'^zato/security/wss/create/$', wss.create, name='security-wss-create'),
    url(r'^zato/security/wss/edit/$', wss.edit, name='security-wss-edit'),
    url(r'^zato/security/wss/change-password/$', wss.change_password, name='security-wss-change-password'),
    url(r'^zato/security/wss/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', wss.Delete(), name=wss.Delete.url_name),

    # Scheduler
    url(r'^zato/scheduler/$', scheduler.index, name='scheduler'),
    url(r'^zato/scheduler/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        scheduler.Delete(), name=scheduler.Delete.url_name),
    url(r'^zato/scheduler/execute/(?P<job_id>.*)/cluster/(?P<cluster_id>.*)/$', 
        scheduler.execute, name='scheduler-job-execute'),
    url(r'^zato/scheduler/get-definition/(?P<start_date>.*)/(?P<repeat>.*)/'
        '(?P<weeks>.*)/(?P<days>.*)/(?P<hours>.*)/(?P<minutes>.*)/(?P<seconds>.*)/$',
        scheduler.get_definition, name='scheduler-job-get-definition'),

    # Definitions

    # .. AMQP
    url(r'^zato/definition/amqp/$', def_amqp.Index(), name=def_amqp.Index.url_name),
    url(r'^zato/definition/amqp/create/$', def_amqp.Create(), name=def_amqp.Create.url_name),
    url(r'^zato/definition/amqp/edit/$', def_amqp.Edit(), name=def_amqp.Edit.url_name),
    url(r'^zato/definition/amqp/change-password/$', def_amqp.change_password, name='def-amqp-change-password'),
    url(r'^zato/definition/amqp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        def_amqp.Delete(), name=def_amqp.Delete.url_name),

    # .. JMS WebSphere MQ
    url(r'^zato/definition/jms-wmq/$', def_jms_wmq.Index(), name=def_jms_wmq.Index.url_name),
    url(r'^zato/definition/jms-wmq/create/$', def_jms_wmq.Create(), name=def_jms_wmq.Create.url_name),
    url(r'^zato/definition/jms-wmq/edit/$', def_jms_wmq.Edit(), name=def_jms_wmq.Edit.url_name),
    url(r'^zato/definition/jms-wmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        def_jms_wmq.Delete(), name=def_jms_wmq.Delete.url_name),

    # Outgoing connections

    # .. AMQP
    url(r'^zato/outgoing/amqp/$', out_amqp.Index(), name=out_amqp.Index.url_name),
    url(r'^zato/outgoing/amqp/create/$', out_amqp.create, name='out-amqp-create'),
    url(r'^zato/outgoing/amqp/edit/$', out_amqp.edit, name='out-amqp-edit'),
    url(r'^zato/outgoing/amqp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        out_amqp.Delete(), name=out_amqp.Delete.url_name),
    
    # .. FTP
    url(r'^zato/outgoing/ftp/$', out_ftp.Index(), name=out_ftp.Index.url_name),
    url(r'^zato/outgoing/ftp/create/$', out_ftp.Create(), name=out_ftp.Create.url_name),
    url(r'^zato/outgoing/ftp/edit/$', out_ftp.Edit(), name=out_ftp.Edit.url_name),
    url(r'^zato/outgoing/ftp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        out_ftp.Delete(), name=out_ftp.Delete.url_name),
    url(r'^zato/outgoing/ftp/change-password/$', out_ftp.change_password, name='out-ftp-change-password'),

    # .. JMS WebSphere MQ
    url(r'^zato/outgoing/jms-wmq/$', out_jms_wmq.index, name='out-jms-wmq'),
    url(r'^zato/outgoing/jms-wmq/create/$', out_jms_wmq.create, name='out-jms-wmq-create'),
    url(r'^zato/outgoing/jms-wmq/edit/$', out_jms_wmq.edit, name='out-jms-wmq-edit'),
    url(r'^zato/outgoing/jms-wmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        out_jms_wmq.Delete(), name=out_jms_wmq.Delete.url_name),
    
    # SQL connection pools
    url(r'^zato/outgoing/sql/$', out_sql.index, name='out-sql'),
    url(r'^zato/outgoing/sql/create/$', out_sql.create, name='out-sql-create'),
    url(r'^zato/outgoing/sql/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', out_sql.ping, name='out-sql-ping'),
    url(r'^zato/outgoing/sql/edit/$', out_sql.edit, name='out-sql-edit'),
    url(r'^zato/outgoing/sql/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        out_sql.Delete(), name=out_sql.Delete.url_name),
    url(r'^zato/outgoing/sql/change-password/$', out_sql.change_password, name='out-sql-change-password'),
    
    # .. ZeroMQ
    url(r'^zato/outgoing/zmq/$', out_zmq.Index(), name=out_zmq.Index.url_name),
    url(r'^zato/outgoing/zmq/create/$', out_zmq.Create(), name=out_zmq.Create.url_name),
    url(r'^zato/outgoing/zmq/edit/$', out_zmq.Edit(), name=out_zmq.Edit.url_name),
    url(r'^zato/outgoing/zmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        out_zmq.Delete(), name=out_zmq.Delete.url_name),

    # Channels

    # .. AMQP
    url(r'^zato/channel/amqp/$', channel_amqp.Index(), name=channel_amqp.Index.url_name),
    url(r'^zato/channel/amqp/create/$', channel_amqp.create, name='channel-amqp-create'),
    url(r'^zato/channel/amqp/edit/$', channel_amqp.edit, name='channel-amqp-edit'),
    url(r'^zato/channel/amqp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        channel_amqp.Delete(), name=channel_amqp.Delete.url_name),

    # .. JMS WebSphere MQ
    url(r'^zato/channel/jms-wmq/$', channel_jms_wmq.Index(), name=channel_jms_wmq.Index.url_name),
    url(r'^zato/channel/jms-wmq/create/$', channel_jms_wmq.create, name='channel-jms-wmq-create'),
    url(r'^zato/channel/jms-wmq/edit/$', channel_jms_wmq.edit, name='channel-jms-wmq-edit'),
    url(r'^zato/channel/jms-wmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        channel_jms_wmq.Delete(), name=channel_jms_wmq.Delete.url_name),

    # .. ZeroMQ
    url(r'^zato/channel/zmq/$', channel_zmq.Index(), name=channel_zmq.Index.url_name),
    url(r'^zato/channel/zmq/create/$', channel_zmq.Create(), name=channel_zmq.Create.url_name),
    url(r'^zato/channel/zmq/edit/$', channel_zmq.Edit(), name=channel_zmq.Edit.url_name),
    url(r'^zato/channel/zmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        channel_zmq.Delete(), name=channel_zmq.Delete.url_name),

    # HTTP/SOAP
    url(r'^zato/http-soap/$', http_soap.index, name='http-soap'),
    url(r'^zato/http-soap/create/$', http_soap.create, name='http-soap-create'),
    url(r'^zato/http-soap/edit/$', http_soap.edit, name='http-soap-edit'),
    url(r'^zato/http-soap/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', http_soap.delete, name='http-soap-delete'),
    url(r'^zato/http-soap/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', http_soap.ping, name='http-soap-ping'),
    
    # Key/value DB
    url(r'^zato/kvdb/remote-command/$', kvdb.remote_command, name='kvdb-remote-command'),
    url(r'^zato/kvdb/remote-command/execute/$', kvdb.remote_command_execute, name='kvdb-remote-command-execute'),
    url(r'^zato/kvdb/data-dict/dictionary/$', dictionary.Index(), name=dictionary.Index.url_name),
    url(r'^zato/kvdb/data-dict/dictionary/create/$', dictionary.Create(), name=dictionary.Create.url_name),
    url(r'^zato/kvdb/data-dict/dictionary/edit/$', dictionary.Edit(), name=dictionary.Edit.url_name),
    url(r'^zato/kvdb/data-dict/dictionary/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        dictionary.Delete(), name=dictionary.Delete.url_name),
    
    url(r'^zato/kvdb/data-dict/translation/$', translation.Index(), name=translation.Index.url_name),
    url(r'^zato/kvdb/data-dict/translation/create/$', translation.Create(), name=translation.Create.url_name),
    url(r'^zato/kvdb/data-dict/translation/edit/$', translation.Edit(), name=translation.Edit.url_name),
    url(r'^zato/kvdb/data-dict/translation/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$', 
        translation.Delete(), name=translation.Delete.url_name),
    url(r'^zato/kvdb/data-dict/translation/get-key-list/$', 
        translation.get_key_list, name='kvdb-data-dict-translation-get-key-list'),
    url(r'^zato/kvdb/data-dict/translation/get-value-list/$', 
        translation.get_value_list, name='kvdb-data-dict-translation-get-value-list'),
    url(r'^zato/kvdb/data-dict/translation/translate/$', 
        translation.translate, name='kvdb-data-dict-translation-translate'),
    
    url(r'^zato/kvdb/data-dict/impexp/$', impexp.index, name='kvdb-data-dict-impexp'),
    url(r'^zato/kvdb/data-dict/impexp/cluster/(?P<cluster_id>.*)/import/$', 
        impexp.import_, name='kvdb-data-dict-impexp-import'),
    url(r'^zato/kvdb/data-dict/impexp/cluster/(?P<cluster_id>.*)/export/$', 
        impexp.export, name='kvdb-data-dict-impexp-export'),
    
    # Statistics
    url(r'^zato/stats/trends/data/$', stats.stats_trends_data, name='stats-trends-data'),
    url(r'^zato/stats/trends/(?P<choice>.*)/$', stats.trends, name='stats-trends'),
    url(r'^zato/stats/summary/data/$', stats.stats_summary_data, name='stats-summary-data'),
    url(r'^zato/stats/summary/(?P<choice>.*)/$', stats.summary, name='stats-summary'),
    url(r'^zato/stats/settings/$', stats.settings, name='stats-settings'),
    url(r'^zato/stats/settings/save/$', stats.settings_save, name='stats-settings-save'),
    url(r'^zato/stats/maintenance/$', stats.maintenance, name='stats-maintenance'),
    url(r'^zato/stats/maintenance/delete/$', stats.maintenance_delete, name='stats-maintenance-delete'),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
