# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.static import serve as django_static_serve

# Zato
from zato.admin import settings
from zato.admin.web.views import account, cluster, http_soap, kvdb, load_balancer, main, scheduler, service, stats
from zato.admin.web.views.cache import builtin as cache_builtin
from zato.admin.web.views.cache.builtin import entries as cache_builtin_entries
from zato.admin.web.views.cache.builtin import entry as cache_builtin_entry
from zato.admin.web.views.cache import memcached_ as cache_memcached
from zato.admin.web.views.channel import amqp_ as channel_amqp
from zato.admin.web.views.channel import file_transfer as channel_file_transfer
from zato.admin.web.views.channel import jms_wmq as channel_jms_wmq
from zato.admin.web.views.channel import json_rpc as channel_json_rpc
from zato.admin.web.views.channel import web_socket as channel_web_socket
from zato.admin.web.views.channel import zmq as channel_zmq
from zato.admin.web.views.cloud.aws import s3 as cloud_aws_s3
from zato.admin.web.views.cloud import dropbox as cloud_dropbox
from zato.admin.web.views.cloud.openstack import swift as cloud_openstack_swift
from zato.admin.web.views import config_file
from zato.admin.web.views.definition import amqp_ as def_amqp
from zato.admin.web.views.definition import cassandra as def_cassandra
from zato.admin.web.views.definition import kafka as def_kafka
from zato.admin.web.views.definition import jms_wmq as def_wmq
from zato.admin.web.views.email import imap as email_imap
from zato.admin.web.views.email import smtp as email_smtp
from zato.admin.web.views.kvdb.data_dict import dictionary, impexp, translation
from zato.admin.web.views.message import json_pointer, live_browser, namespace, xpath
from zato.admin.web.views.notif.cloud.openstack import swift as notif_cloud_openstack_swift
from zato.admin.web.views.notif import sql as notif_sql
from zato.admin.web.views.outgoing import amqp_ as out_amqp
from zato.admin.web.views.outgoing import ftp as out_ftp
from zato.admin.web.views.outgoing.im import slack as out_im_slack
from zato.admin.web.views.outgoing.im import telegram as out_im_telegram
from zato.admin.web.views.outgoing import jms_wmq as out_jms_wmq
from zato.admin.web.views.outgoing import ldap as out_ldap
from zato.admin.web.views.outgoing import mongodb as out_mongodb
from zato.admin.web.views.outgoing import odoo as out_odoo
from zato.admin.web.views.outgoing import sap as out_sap
from zato.admin.web.views.outgoing import sftp as out_sftp
from zato.admin.web.views.outgoing import sql as out_sql
from zato.admin.web.views.outgoing import wsx as out_wsx
from zato.admin.web.views.outgoing import zmq as out_zmq
from zato.admin.web.views.pubsub import endpoint as pubsub_endpoint
from zato.admin.web.views.pubsub import message as pubsub_message
from zato.admin.web.views.pubsub import subscription as pubsub_subscription
from zato.admin.web.views.pubsub.task import sync as pubsub_task_sync
from zato.admin.web.views.pubsub.task import delivery as pubsub_task
from zato.admin.web.views.pubsub.task.delivery import message as pubsub_task_message
from zato.admin.web.views.pubsub.task.delivery import server as pubsub_task_delivery_server
from zato.admin.web.views.pubsub import topic as pubsub_topic
from zato.admin.web.views.query import cassandra as query_cassandra
from zato.admin.web.views.search import es
from zato.admin.web.views.search import solr
from zato.admin.web.views.sms import twilio
from zato.admin.web.views.security import apikey, aws, basic_auth, jwt, ntlm, oauth, openstack as openstack_security, rbac, \
     wss, xpath as xpath_sec
from zato.admin.web.views.security.tls import ca_cert as tls_ca_cert, channel as tls_channel, key_cert as tls_key_cert
from zato.admin.web.views.security.vault import connection as vault_conn

urlpatterns = [

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Main URLs
# #
# ################################################################################################################################
# ################################################################################################################################

    url(r'^accounts/login/$', main.login, name='login'),
    url(r'^$', main.index_redirect),
    url(r'^zato/$', login_required(main.index), name='main-page'),
    url(r'^logout/$', login_required(main.logout), name='logout'),
    ]

# ################################################################################################################################

urlpatterns += [

    # User accounts

    url(r'^account/settings/basic/$',
        login_required(account.settings_basic), name='account-settings-basic'),
    url(r'^account/settings/basic/save/$',
        login_required(account.settings_basic_save), name='account-settings-basic-save'),
    url(r'^account/settings/basic/generate-totp-key$',
        login_required(account.generate_totp_key), name='account-settings-basic-generate-totp-key'),
    ]

# ################################################################################################################################

urlpatterns += [

    # Clusters

    url(r'^zato/cluster/$',
        login_required(cluster.index), name='cluster'),
    url(r'^zato/cluster/edit/$',
        login_required(cluster.edit), name='cluster-edit'),
    url(r'^zato/cluster/delete/(?P<id>.*)/$',
        login_required(cluster.delete), name='cluster-delete'),
    url(r'^zato/cluster/servers-state/(?P<cluster_id>.*)$',
        login_required(cluster.get_servers_state), name='cluster-servers-state'),
    url(r'^zato/cluster/get/by-id/(?P<cluster_id>.*)$',
        login_required(cluster.get_by_id), name='cluster-get-by-id'),
    url(r'^zato/cluster/get/by-name/(?P<cluster_name>.*)/$',
        login_required(cluster.get_by_name), name='cluster-get-by-name'),
    url(r'^zato/cluster/servers/$',
        login_required(cluster.servers), name='cluster-servers'),
    url(r'^zato/cluster/servers/edit/$',
        login_required(cluster.servers_edit), name='cluster-servers-edit'),
    url(r'^zato/cluster/servers/load-balancer/(?P<action>.*)/(?P<server_id>.*)/$',
        login_required(cluster.servers_add_remove_lb), name='cluster-servers-add-remove-lb'),
    url(r'^zato/cluster/servers/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cluster.ServerDelete()), name=cluster.ServerDelete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # Load balancer

    url(r'^zato/load-balancer/get-addresses/cluster/(?P<cluster_id>.*)/$',
        login_required(load_balancer.get_addresses), name='lb-get-addresses'),
    url(r'^zato/load-balancer/manage/cluster/(?P<cluster_id>\d+)/validate-save/$',
        login_required(load_balancer.validate_save), name='lb-manage-validate-save'),
    url(r'^zato/load-balancer/manage/cluster/(?P<cluster_id>.*)/$', login_required(load_balancer.manage), name='lb-manage'),
    url(r'^zato/load-balancer/manage/source-code/cluster/(?P<cluster_id>.*)/validate-save$',
        login_required(load_balancer.validate_save_source_code), name='lb-manage-source-code-validate-save'),
    url(r'^zato/load-balancer/manage/source-code/cluster/(?P<cluster_id>.*)/$',
        login_required(load_balancer.manage_source_code), name='lb-manage-source-code'),
    url(r'^zato/load-balancer/remote-command/(?P<cluster_id>.*)/$',
        login_required(load_balancer.remote_command), name='lb-remote-command'),
    ]

# ################################################################################################################################

urlpatterns += [

    # Services

    url(r'^zato/service/$',
        login_required(service.Index()), name=service.Index.url_name),
    url(r'^zato/service/details$',
        login_required(service.Index()), name=service.Index.url_name),
    url(r'^zato/service/last-stats/(?P<service_id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(service.last_stats), name='service-last-stats'),
    url(r'^zato/service/cluster/(?P<cluster_id>.*)/upload/$',
        login_required(service.package_upload), name='service-package-upload'),
    url(r'^zato/service/create/$',
        login_required(service.create), name='service-create'),
    url(r'^zato/service/edit/$',
        login_required(service.Edit()), name=service.Edit.url_name),
    url(r'^zato/service/invoke/(?P<name>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(service.invoke), name='service-invoke'),
    url(r'^zato/service/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(service.Delete()), name=service.Delete.url_name),
    url(r'^zato/service/overview/(?P<service_name>.*)/$',
        login_required(service.overview), name='service-overview'),
    url(r'^zato/service/invoker/(?P<service_name>.*)/$',
        login_required(service.invoker), name='service-invoker'),
    url(r'^zato/service/source-info/(?P<service_name>.*)/$',
        login_required(service.source_info), name='service-source-info'),
    url(r'^zato/service/request-response/(?P<service_name>.*)/cluster/(?P<cluster_id>.*)/configure/$',
        login_required(service.request_response_configure), name='service-request-response-configure'),
    url(r'^zato/service/request-response/(?P<service_name>.*)/$',
        login_required(service.request_response), name='service-request-response'),
    url(r'^zato/service/slow-response/details/(?P<cid>.*)/(?P<service_name>.*)/$',
        login_required(service.slow_response_details), name='service-slow-response-details'),
    url(r'^zato/service/slow-response/(?P<service_name>.*)/$',
        login_required(service.slow_response), name='service-slow-response'),
    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Messages
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # .. Namespace
    url(r'^zato/messages/namespace/$',
        login_required(namespace.Index()), name=namespace.Index.url_name),
    url(r'^zato/messages/namespace/create/$',
        login_required(namespace.Create()), name=namespace.Create.url_name),
    url(r'^zato/messages/namespace/edit/$',
        login_required(namespace.Edit()), name=namespace.Edit.url_name),
    url(r'^zato/messages/namespace/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(namespace.Delete()), name=namespace.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. XPath
    url(r'^zato/messages/xpath/$',
        login_required(xpath.Index()), name=xpath.Index.url_name),
    url(r'^zato/messages/xpath/create/$',
        login_required(xpath.Create()), name=xpath.Create.url_name),
    url(r'^zato/messages/xpath/edit/$',
        login_required(xpath.Edit()), name=xpath.Edit.url_name),
    url(r'^zato/messages/xpath/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(xpath.Delete()), name=xpath.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. JSON Pointer
    url(r'^zato/messages/json-pointer/$',
        login_required(json_pointer.Index()), name=json_pointer.Index.url_name),
    url(r'^zato/messages/json-pointer/create/$',
        login_required(json_pointer.Create()), name=json_pointer.Create.url_name),
    url(r'^zato/messages/json-pointer/edit/$',
        login_required(json_pointer.Edit()), name=json_pointer.Edit.url_name),
    url(r'^zato/messages/json-pointer/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(json_pointer.Delete()), name=json_pointer.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. Live browser
    url(r'^zato/messages/live-browser/$',
        login_required(live_browser.index), name='message-live-browser-index'),
    url(r'^zato/messages/live-browser/get-connection-details$',
        login_required(live_browser.get_connection_details), name='message-live-browser-get-connection-details'),
    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Security
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # .. API keys

    url(r'^zato/security/apikey/$',
        login_required(apikey.Index()), name=apikey.Index.url_name),
    url(r'^zato/security/apikey/$',
        login_required(apikey.Index()), name=apikey.Index.url_name),
    url(r'^zato/security/apikey/create/$',
        login_required(apikey.Create()), name=apikey.Create.url_name),
    url(r'^zato/security/apikey/edit/$',
        login_required(apikey.Edit()), name=apikey.Edit.url_name),
    url(r'^zato/security/apikey/change-password/$',
        login_required(apikey.change_password), name='security-apikey-change-password'),
    url(r'^zato/security/apikey/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(apikey.Delete()), name=apikey.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. AWS

    url(r'^zato/security/aws/$',
        login_required(aws.Index()), name=aws.Index.url_name),
    url(r'^zato/security/aws/$',
        login_required(aws.Index()), name=aws.Index.url_name),
    url(r'^zato/security/aws/create/$',
        login_required(aws.Create()), name=aws.Create.url_name),
    url(r'^zato/security/aws/edit/$',
        login_required(aws.Edit()), name=aws.Edit.url_name),
    url(r'^zato/security/aws/change-password/$',
        login_required(aws.change_password), name='security-aws-change-password'),
    url(r'^zato/security/aws/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(aws.Delete()), name=aws.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. HTTP Basic Auth

    url(r'^zato/security/basic-auth/$',
        login_required(basic_auth.Index()), name=basic_auth.Index.url_name),
    url(r'^zato/security/basic-auth/$',
        login_required(basic_auth.Index()), name=basic_auth.Index.url_name),
    url(r'^zato/security/basic-auth/create/$',
        login_required(basic_auth.Create()), name=basic_auth.Create.url_name),
    url(r'^zato/security/basic-auth/edit/$',
        login_required(basic_auth.Edit()), name=basic_auth.Edit.url_name),
    url(r'^zato/security/basic-auth/change-password/$',
        login_required(basic_auth.change_password), name='security-basic-auth-change-password'),
    url(r'^zato/security/basic-auth/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(basic_auth.Delete()), name=basic_auth.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. JWT

    url(r'^zato/security/jwt/$',
        login_required(jwt.Index()), name=jwt.Index.url_name),
    url(r'^zato/security/jwt/$',
        login_required(jwt.Index()), name=jwt.Index.url_name),
    url(r'^zato/security/jwt/create/$',
        login_required(jwt.Create()), name=jwt.Create.url_name),
    url(r'^zato/security/jwt/edit/$',
        login_required(jwt.Edit()), name=jwt.Edit.url_name),
    url(r'^zato/security/jwt/change-password/$',
        login_required(jwt.change_password), name='security-jwt-change-password'),
    url(r'^zato/security/jwt/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(jwt.Delete()), name=jwt.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. NTLM

    url(r'^zato/security/ntlm/$',
        login_required(ntlm.Index()), name=ntlm.Index.url_name),
    url(r'^zato/security/ntlm/$',
        login_required(ntlm.Index()), name=ntlm.Index.url_name),
    url(r'^zato/security/ntlm/create/$',
        login_required(ntlm.Create()), name=ntlm.Create.url_name),
    url(r'^zato/security/ntlm/edit/$',
        login_required(ntlm.Edit()), name=ntlm.Edit.url_name),
    url(r'^zato/security/ntlm/change-password/$',
        login_required(ntlm.change_password), name='security-ntlm-change-password'),
    url(r'^zato/security/ntlm/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(ntlm.Delete()), name=ntlm.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. OAuth

    url(r'^zato/security/oauth/$',
        login_required(oauth.Index()), name=oauth.Index.url_name),
    url(r'^zato/security/oauth/$',
        login_required(oauth.Index()), name=oauth.Index.url_name),
    url(r'^zato/security/oauth/create/$',
        login_required(oauth.Create()), name=oauth.Create.url_name),
    url(r'^zato/security/oauth/edit/$',
        login_required(oauth.Edit()), name=oauth.Edit.url_name),
    url(r'^zato/security/oauth/change-password/$',
        login_required(oauth.change_secret), name='security-oauth-change-secret'),
    url(r'^zato/security/oauth/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(oauth.Delete()), name=oauth.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. OpenStack security

    url(r'^zato/security/openstack_security/$',
        login_required(openstack_security.Index()), name=openstack_security.Index.url_name),
    url(r'^zato/security/openstack_security/$',
        login_required(openstack_security.Index()), name=openstack_security.Index.url_name),
    url(r'^zato/security/openstack_security/create/$',
        login_required(openstack_security.Create()), name=openstack_security.Create.url_name),
    url(r'^zato/security/openstack_security/edit/$',
        login_required(openstack_security.Edit()), name=openstack_security.Edit.url_name),
    url(r'^zato/security/openstack_security/change-password/$',
        login_required(openstack_security.change_password), name='security-openstack-change-password'),
    url(r'^zato/security/openstack_security/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(openstack_security.Delete()), name=openstack_security.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. RBAC - Roles

    url(r'^zato/security/rbac/role/$',
        login_required(rbac.role.Index()), name=rbac.role.Index.url_name),
    url(r'^zato/security/rbac/role/create/$',
        login_required(rbac.role.Create()), name=rbac.role.Create.url_name),
    url(r'^zato/security/rbac/role/edit/$',
        login_required(rbac.role.Edit()), name=rbac.role.Edit.url_name),
    url(r'^zato/security/rbac/role/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(rbac.role.Delete()), name=rbac.role.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. RBAC - Client roles

    url(r'^zato/security/rbac/client-role/$',
        login_required(rbac.client_role.Index()), name=rbac.client_role.Index.url_name),
    url(r'^zato/security/rbac/client-role/create/$',
        login_required(rbac.client_role.Create()), name=rbac.client_role.Create.url_name),
    url(r'^zato/security/rbac/client-role/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(rbac.client_role.Delete()), name=rbac.client_role.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. RBAC - Permissions

    url(r'^zato/security/rbac/permission/$',
        login_required(rbac.permission.Index()), name=rbac.permission.Index.url_name),
    url(r'^zato/security/rbac/permission/create/$',
        login_required(rbac.permission.Create()), name=rbac.permission.Create.url_name),
    url(r'^zato/security/rbac/permission/edit/$',
        login_required(rbac.permission.Edit()), name=rbac.permission.Edit.url_name),
    url(r'^zato/security/rbac/permission/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(rbac.permission.Delete()), name=rbac.permission.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. RBAC - Role Permissions

    url(r'^zato/security/rbac/role-permission/$',
        login_required(rbac.role_permission.Index()), name=rbac.role_permission.Index.url_name),
    url(r'^zato/security/rbac/role-permission/create/$',
        login_required(rbac.role_permission.Create()), name=rbac.role_permission.Create.url_name),
    url(r'^zato/security/rbac/role-permission/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(rbac.role_permission.Delete()), name=rbac.role_permission.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. TLS - channel security based on client certificates

    url(r'^zato/security/tls/channel/$',
        login_required(tls_channel.Index()), name=tls_channel.Index.url_name),
    url(r'^zato/security/tls/channel/create/$',
        login_required(tls_channel.Create()), name=tls_channel.Create.url_name),
    url(r'^zato/security/tls/channel/edit/$',
        login_required(tls_channel.Edit()), name=tls_channel.Edit.url_name),
    url(r'^zato/security/tls/channel/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(tls_channel.Delete()), name='security-tls-channel-delete'),

    # .. TLS - keys and certificates Zato itself uses in outgoing connections

    url(r'^zato/security/tls/key-cert/$',
        login_required(tls_key_cert.Index()), name=tls_key_cert.Index.url_name),
    url(r'^zato/security/tls/key-cert/create/$',
        login_required(tls_key_cert.Create()), name=tls_key_cert.Create.url_name),
    url(r'^zato/security/tls/key-cert/edit/$',
        login_required(tls_key_cert.Edit()), name=tls_key_cert.Edit.url_name),
    url(r'^zato/security/tls/key-cert/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(tls_key_cert.Delete()), name='security-tls-key-cert-delete'),

    # .. TLS - CA certs signing off certificates of endpoints Zato services invoke

    url(r'^zato/security/tls/ca-cert/$',
        login_required(tls_ca_cert.Index()), name=tls_ca_cert.Index.url_name),
    url(r'^zato/security/tls/ca-cert/create/$',
        login_required(tls_ca_cert.Create()), name=tls_ca_cert.Create.url_name),
    url(r'^zato/security/tls/ca-cert/edit/$',
        login_required(tls_ca_cert.Edit()), name=tls_ca_cert.Edit.url_name),
    url(r'^zato/security/tls/ca-cert/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(tls_ca_cert.Delete()), name='security-tls-ca-cert-delete'),

    ]

# ################################################################################################################################

urlpatterns += [

    # .. Vault connections

    url(r'^zato/security/vault/conn/$',
        login_required(vault_conn.Index()), name=vault_conn.Index.url_name),
    url(r'^zato/security/vault/conn/create/$',
        login_required(vault_conn.Create()), name=vault_conn.Create.url_name),
    url(r'^zato/security/vault/conn/edit/$',
        login_required(vault_conn.Edit()), name=vault_conn.Edit.url_name),
    url(r'^zato/security/vault/conn/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(vault_conn.Delete()), name=vault_conn.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. WS-Security

    url(r'^zato/security/wss/$',
        login_required(wss.index), name='security-wss'),
    url(r'^zato/security/wss/create/$',
        login_required(wss.create), name='security-wss-create'),
    url(r'^zato/security/wss/edit/$',
        login_required(wss.edit), name='security-wss-edit'),
    url(r'^zato/security/wss/change-password/$',
        login_required(wss.change_password), name='security-wss-change-password'),
    url(r'^zato/security/wss/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(wss.Delete()), name=wss.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. XPath

    url(r'^zato/security/xpath/$',
        login_required(xpath_sec.Index()), name=xpath_sec.Index.url_name),
    url(r'^zato/security/xpath/$',
        login_required(xpath_sec.Index()), name=xpath_sec.Index.url_name),
    url(r'^zato/security/xpath/create/$',
        login_required(xpath_sec.Create()), name=xpath_sec.Create.url_name),
    url(r'^zato/security/xpath/edit/$',
        login_required(xpath_sec.Edit()), name=xpath_sec.Edit.url_name),
    url(r'^zato/security/xpath/change-password/$',
        login_required(xpath_sec.change_password), name='security-xpath-change-password'),
    url(r'^zato/security/xpath/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(xpath_sec.Delete()), name=xpath_sec.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # Scheduler

    url(r'^zato/scheduler/$', login_required(scheduler.index), name='scheduler'),
    url(r'^zato/scheduler/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(scheduler.Delete()), name=scheduler.Delete.url_name),
    url(r'^zato/scheduler/execute/(?P<job_id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(scheduler.execute), name='scheduler-job-execute'),
    url(r'^zato/scheduler/get-definition/(?P<start_date>.*)/(?P<repeat>.*)/'
        '(?P<weeks>.*)/(?P<days>.*)/(?P<hours>.*)/(?P<minutes>.*)/(?P<seconds>.*)/$',
        login_required(scheduler.get_definition), name='scheduler-job-get-definition'),
    ]

# ################################################################################################################################

urlpatterns += [

    # Config files

    url(r'^zato/config-file/$',
        login_required(config_file.Index()), name=config_file.Index.url_name),
    url(r'^zato/config-file/create/$',
        login_required(config_file.Create()), name=config_file.Create.url_name),
    url(r'^zato/config-file/edit/$',
        login_required(config_file.Edit()), name=config_file.Edit.url_name),
    url(r'^zato/config-file/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(config_file.Delete()), name=config_file.Delete.url_name),
    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Definitions
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # .. AMQP

    url(r'^zato/definition/amqp/$',
        login_required(def_amqp.Index()), name=def_amqp.Index.url_name),
    url(r'^zato/definition/amqp/create/$',
        login_required(def_amqp.Create()), name=def_amqp.Create.url_name),
    url(r'^zato/definition/amqp/edit/$',
        login_required(def_amqp.Edit()), name=def_amqp.Edit.url_name),
    url(r'^zato/definition/amqp/change-password/$',
        login_required(def_amqp.change_password), name='def-amqp-change-password'),
    url(r'^zato/definition/amqp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(def_amqp.Delete()), name=def_amqp.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. Cassandra

    url(r'^zato/definition/cassandra/$',
        login_required(def_cassandra.Index()), name=def_cassandra.Index.url_name),
    url(r'^zato/definition/cassandra/create/$',
        login_required(def_cassandra.Create()), name=def_cassandra.Create.url_name),
    url(r'^zato/definition/cassandra/edit/$',
        login_required(def_cassandra.Edit()), name=def_cassandra.Edit.url_name),
    url(r'^zato/definition/cassandra/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(def_cassandra.Delete()), name=def_cassandra.Delete.url_name),
    url(r'^zato/definition/cassandra/change-password/$',
        login_required(def_cassandra.change_password), name='definition-cassandra-change-password'),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. Kafka

    url(r'^zato/definition/kafka/$',
        login_required(def_kafka.Index()), name=def_kafka.Index.url_name),
    url(r'^zato/definition/kafka/create/$',
        login_required(def_kafka.Create()), name=def_kafka.Create.url_name),
    url(r'^zato/definition/kafka/edit/$',
        login_required(def_kafka.Edit()), name=def_kafka.Edit.url_name),
    url(r'^zato/definition/kafka/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(def_kafka.Delete()), name=def_kafka.Delete.url_name),
    url(r'^zato/definition/kafka/change-password/$',
        login_required(def_kafka.change_password), name='definition-kafka-change-password'),
    url(r'^zato/definition/kafka/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(def_kafka.ping), name='definition-wmq-ping'),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. IBM MQ

    url(r'^zato/definition/jms-wmq/$',
        login_required(def_wmq.Index()), name=def_wmq.Index.url_name),
    url(r'^zato/definition/jms-wmq/create/$',
        login_required(def_wmq.Create()), name=def_wmq.Create.url_name),
    url(r'^zato/definition/jms-wmq/edit/$',
        login_required(def_wmq.Edit()), name=def_wmq.Edit.url_name),
    url(r'^zato/definition/jms-wmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(def_wmq.Delete()), name=def_wmq.Delete.url_name),
    url(r'^zato/definition/jms-wmq/change-password/$',
        login_required(def_wmq.change_password), name='definition-wmq-change-password'),
    url(r'^zato/definition/jms-wmq/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(def_wmq.ping), name='definition-wmq-ping'),
    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Outgoing connections
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # .. AMQP

    url(r'^zato/outgoing/amqp/$',
        login_required(out_amqp.Index()), name=out_amqp.Index.url_name),
    url(r'^zato/outgoing/amqp/create/$',
        login_required(out_amqp.create), name='out-amqp-create'),
    url(r'^zato/outgoing/amqp/edit/$',
        login_required(out_amqp.edit), name='out-amqp-edit'),
    url(r'^zato/outgoing/amqp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_amqp.Delete()), name=out_amqp.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. FTP

    url(r'^zato/outgoing/ftp/$',
        login_required(out_ftp.Index()), name=out_ftp.Index.url_name),
    url(r'^zato/outgoing/ftp/create/$',
        login_required(out_ftp.Create()), name=out_ftp.Create.url_name),
    url(r'^zato/outgoing/ftp/edit/$',
        login_required(out_ftp.Edit()), name=out_ftp.Edit.url_name),
    url(r'^zato/outgoing/ftp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_ftp.Delete()), name=out_ftp.Delete.url_name),
    url(r'^zato/outgoing/ftp/change-password/$',
        login_required(out_ftp.change_password), name='out-ftp-change-password'),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. IBM MQ

    url(r'^zato/outgoing/jms-wmq/$',
        login_required(out_jms_wmq.index), name='out-jms-wmq'),
    url(r'^zato/outgoing/jms-wmq/create/$',
        login_required(out_jms_wmq.create), name='out-jms-wmq-create'),
    url(r'^zato/outgoing/jms-wmq/edit/$',
        login_required(out_jms_wmq.edit), name='out-jms-wmq-edit'),
    url(r'^zato/outgoing/jms-wmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_jms_wmq.Delete()), name=out_jms_wmq.Delete.url_name),
    url(r'^zato/outgoing/jms-wmq/send/cluster/(?P<cluster_id>.*)/conn/(?P<conn_id>.*)/(?P<name_slug>.*)$',
        login_required(out_jms_wmq.send_message), name='outgoing-wmq-send-message'),
    url(r'^zato/outgoing/jms-wmq/send/action/cluster/(?P<cluster_id>.*)/conn/(?P<conn_id>.*)/(?P<name_slug>.*)$',
        login_required(out_jms_wmq.send_message_action), name='outgoing-wmq-send-message-action'),

    ]

# ################################################################################################################################

urlpatterns += [

    # .. LDAP

    url(r'^zato/outgoing/ldap/$',
        login_required(out_ldap.Index()), name=out_ldap.Index.url_name),
    url(r'^zato/outgoing/ldap/create/$',
        login_required(out_ldap.Create()), name=out_ldap.Create.url_name),
    url(r'^zato/outgoing/ldap/edit/$',
        login_required(out_ldap.Edit()), name=out_ldap.Edit.url_name),
    url(r'^zato/outgoing/ldap/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_ldap.Delete()), name=out_ldap.Delete.url_name),
    url(r'^zato/outgoing/ldap/change-password/$',
        login_required(out_ldap.change_password), name='out-ldap-change-password'),
    url(r'^zato/outgoing/ldap/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_ldap.ping), name='out-ldap-ping'),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. MongoDB

    url(r'^zato/outgoing/mongodb/$',
        login_required(out_mongodb.Index()), name=out_mongodb.Index.url_name),
    url(r'^zato/outgoing/mongodb/create/$',
        login_required(out_mongodb.Create()), name=out_mongodb.Create.url_name),
    url(r'^zato/outgoing/mongodb/edit/$',
        login_required(out_mongodb.Edit()), name=out_mongodb.Edit.url_name),
    url(r'^zato/outgoing/mongodb/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_mongodb.Delete()), name=out_mongodb.Delete.url_name),
    url(r'^zato/outgoing/mongodb/change-password/$',
        login_required(out_mongodb.change_password), name='out-mongodb-change-password'),
    url(r'^zato/outgoing/mongodb/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_mongodb.ping), name='out-mongodb-ping'),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. Odoo

    url(r'^zato/outgoing/odoo/$',
        login_required(out_odoo.Index()), name=out_odoo.Index.url_name),
    url(r'^zato/outgoing/odoo/create/$',
        login_required(out_odoo.Create()), name=out_odoo.Create.url_name),
    url(r'^zato/outgoing/odoo/edit/$',
        login_required(out_odoo.Edit()), name=out_odoo.Edit.url_name),
    url(r'^zato/outgoing/odoo/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_odoo.Delete()), name=out_odoo.Delete.url_name),
    url(r'^zato/outgoing/odoo/change-password/$',
        login_required(out_odoo.change_password), name='out-odoo-change-password'),
    url(r'^zato/outgoing/odoo/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_odoo.ping), name='out-odoo-ping'),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. SAP RFC

    url(r'^zato/outgoing/sap/$',
        login_required(out_sap.Index()), name=out_sap.Index.url_name),
    url(r'^zato/outgoing/sap/create/$',
        login_required(out_sap.Create()), name=out_sap.Create.url_name),
    url(r'^zato/outgoing/sap/edit/$',
        login_required(out_sap.Edit()), name=out_sap.Edit.url_name),
    url(r'^zato/outgoing/sap/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_sap.Delete()), name=out_sap.Delete.url_name),
    url(r'^zato/outgoing/sap/change-password/$',
        login_required(out_sap.change_password), name='out-sap-change-password'),
    url(r'^zato/outgoing/sap/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_sap.ping), name='out-sap-ping'),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. SFTP

    url(r'^zato/outgoing/sftp/$',
        login_required(out_sftp.Index()), name=out_sftp.Index.url_name),
    url(r'^zato/outgoing/sftp/create/$',
        login_required(out_sftp.Create()), name=out_sftp.Create.url_name),
    url(r'^zato/outgoing/sftp/edit/$',
        login_required(out_sftp.Edit()), name=out_sftp.Edit.url_name),
    url(r'^zato/outgoing/sftp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_sftp.Delete()), name=out_sftp.Delete.url_name),
    url(r'^zato/outgoing/sftp/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_sftp.ping), name='out-sftp-ping'),
    url(r'^zato/outgoing/sftp/command-shell/(?P<id>.*)/cluster/(?P<cluster_id>.*)/(?P<name_slug>.*)/$',
        login_required(out_sftp.command_shell), name='out-sftp-command-shell'),
    url(r'^zato/outgoing/sftp/command-shell-action/(?P<id>.*)/cluster/(?P<cluster_id>.*)/(?P<name_slug>.*)/$',
        login_required(out_sftp.command_shell_action), name='out-sftp-command-shell-action'),
    ]

# ################################################################################################################################

urlpatterns += [

    # SQL connection pools

    url(r'^zato/outgoing/sql/$',
        login_required(out_sql.index), name='out-sql'),
    url(r'^zato/outgoing/sql/create/$',
        login_required(out_sql.create), name='out-sql-create'),
    url(r'^zato/outgoing/sql/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_sql.ping), name='out-sql-ping'),
    url(r'^zato/outgoing/sql/edit/$',
        login_required(out_sql.edit), name='out-sql-edit'),
    url(r'^zato/outgoing/sql/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_sql.Delete()), name=out_sql.Delete.url_name),
    url(r'^zato/outgoing/sql/change-password/$',
        login_required(out_sql.change_password), name='out-sql-change-password'),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. WSX

    url(r'^zato/outgoing/wsx/$',
        login_required(out_wsx.Index()), name=out_wsx.Index.url_name),
    url(r'^zato/outgoing/wsx/create/$',
        login_required(out_wsx.Create()), name=out_wsx.Create.url_name),
    url(r'^zato/outgoing/wsx/edit/$',
        login_required(out_wsx.Edit()), name=out_wsx.Edit.url_name),
    url(r'^zato/outgoing/wsx/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_wsx.Delete()), name=out_wsx.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. ZeroMQ
    url(r'^zato/outgoing/zmq/$',
        login_required(out_zmq.Index()), name=out_zmq.Index.url_name),
    url(r'^zato/outgoing/zmq/create/$',
        login_required(out_zmq.Create()), name=out_zmq.Create.url_name),
    url(r'^zato/outgoing/zmq/edit/$',
        login_required(out_zmq.Edit()), name=out_zmq.Edit.url_name),
    url(r'^zato/outgoing/zmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_zmq.Delete()), name=out_zmq.Delete.url_name),
    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Channels
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # .. AMQP
    url(r'^zato/channel/amqp/$',
        login_required(channel_amqp.Index()), name=channel_amqp.Index.url_name),
    url(r'^zato/channel/amqp/create/$',
        login_required(channel_amqp.create), name='channel-amqp-create'),
    url(r'^zato/channel/amqp/edit/$',
        login_required(channel_amqp.edit), name='channel-amqp-edit'),
    url(r'^zato/channel/amqp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(channel_amqp.Delete()), name=channel_amqp.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. FTP
    url(r'^zato/channel/file-transfer/$',
        login_required(channel_file_transfer.Index()), name=channel_file_transfer.Index.url_name),
    url(r'^zato/channel/file-transfer/create/$',
        login_required(channel_file_transfer.Create()), name=channel_file_transfer.Create.url_name),
    url(r'^zato/channel/file-transfer/edit/$',
        login_required(channel_file_transfer.Edit()), name=channel_file_transfer.Edit.url_name),
    url(r'^zato/channel/file-transfer/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(channel_file_transfer.Delete()), name=channel_file_transfer.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. IBM MQ
    url(r'^zato/channel/jms-wmq/$',
        login_required(channel_jms_wmq.Index()), name=channel_jms_wmq.Index.url_name),
    url(r'^zato/channel/jms-wmq/create/$',
        login_required(channel_jms_wmq.create), name='channel-jms-wmq-create'),
    url(r'^zato/channel/jms-wmq/edit/$',
        login_required(channel_jms_wmq.edit), name='channel-jms-wmq-edit'),
    url(r'^zato/channel/jms-wmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(channel_jms_wmq.Delete()), name=channel_jms_wmq.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. JSON-RPC
    url(r'^zato/channel/json-rpc/$',
        login_required(channel_json_rpc.Index()), name=channel_json_rpc.Index.url_name),
    url(r'^zato/channel/json-rpc/create/$',
        login_required(channel_json_rpc.Create()), name=channel_json_rpc.Create.url_name),
    url(r'^zato/channel/json-rpc/edit/$',
        login_required(channel_json_rpc.Edit()), name=channel_json_rpc.Edit.url_name),
    url(r'^zato/channel/json-rpc/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(channel_json_rpc.Delete()), name=channel_json_rpc.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. WebSocket
    url(r'^zato/channel/wsx/$',
        login_required(channel_web_socket.Index()), name=channel_web_socket.Index.url_name),
    url(r'^zato/channel/wsx/create/$',
        login_required(channel_web_socket.Create()), name=channel_web_socket.Create.url_name),
    url(r'^zato/channel/wsx/edit/$',
        login_required(channel_web_socket.Edit()), name=channel_web_socket.Edit.url_name),
    url(r'^zato/channel/wsx/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(channel_web_socket.Delete()), name=channel_web_socket.Delete.url_name),

    url(r'^zato/channel/wsx/connection/invoke/action/(?P<pub_client_id>.*)/$',
        login_required(channel_web_socket.invoke_action), name='channel-web-socket-invoke-action'),

    url(r'^zato/channel/wsx/connection/invoke/(?P<conn_id>.*)/(?P<pub_client_id>.*)/(?P<ext_client_id>.*)/(?P<ext_client_name>.*)/(?P<channel_id>.*)/(?P<channel_name>.*)/$',
        login_required(channel_web_socket.invoke), name='channel-web-socket-invoke'),

    url(r'^zato/channel/wsx/connection-list/(?P<id>.*)/delete/(?P<pub_client_id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(channel_web_socket.DisconnectionConnection()), name=channel_web_socket.DisconnectionConnection.url_name),

    url(r'^zato/channel/wsx/connection-list/(?P<id>.*)/$',
        login_required(channel_web_socket.ConnectionList()), name=channel_web_socket.ConnectionList.url_name),

    url(r'^zato/channel/wsx/connection/sub-key-data-list/(?P<pub_client_id>.*)/$',
        login_required(channel_web_socket.SubKeyDataList()), name=channel_web_socket.SubKeyDataList.url_name),
]

# ################################################################################################################################

urlpatterns += [

    # .. ZeroMQ
    url(r'^zato/channel/zmq/$',
        login_required(channel_zmq.Index()), name=channel_zmq.Index.url_name),
    url(r'^zato/channel/zmq/create/$',
        login_required(channel_zmq.Create()), name=channel_zmq.Create.url_name),
    url(r'^zato/channel/zmq/edit/$',
        login_required(channel_zmq.Edit()), name=channel_zmq.Edit.url_name),
    url(r'^zato/channel/zmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(channel_zmq.Delete()), name=channel_zmq.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # HTTP/SOAP

    url(r'^zato/http-soap/$',
        login_required(http_soap.index), name='http-soap'),
    ]

# ################################################################################################################################

urlpatterns += [

    url(r'^zato/http-soap/create/$',
        login_required(http_soap.create), name='http-soap-create'),
    url(r'^zato/http-soap/edit/$',
        login_required(http_soap.edit), name='http-soap-edit'),
    url(r'^zato/http-soap/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(http_soap.delete), name='http-soap-delete'),
    url(r'^zato/http-soap/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(http_soap.ping), name='http-soap-ping'),
    url(r'^zato/http-soap/reload-wsdl/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(http_soap.reload_wsdl), name='http-soap-reload-wsdl'),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. ZeroMQ

    url(r'^zato/channel/zmq/$',
        login_required(channel_zmq.Index()), name=channel_zmq.Index.url_name),
    url(r'^zato/channel/zmq/create/$',
        login_required(channel_zmq.Create()), name=channel_zmq.Create.url_name),
    url(r'^zato/channel/zmq/edit/$',
        login_required(channel_zmq.Edit()), name=channel_zmq.Edit.url_name),
    url(r'^zato/channel/zmq/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(channel_zmq.Delete()), name=channel_zmq.Delete.url_name),
    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Cache
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # .. Built-in

    url(r'^zato/cache/builtin/$',
        login_required(cache_builtin.Index()), name=cache_builtin.Index.url_name),
    url(r'^zato/cache/builtin/create/$',
        login_required(cache_builtin.Create()), name=cache_builtin.Create.url_name),
    url(r'^zato/cache/builtin/edit/$',
        login_required(cache_builtin.Edit()), name=cache_builtin.Edit.url_name),
    url(r'^zato/cache/builtin/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cache_builtin.Delete()), name=cache_builtin.Delete.url_name),
    url(r'^zato/cache/builtin/clear/$',
        login_required(cache_builtin.clear), name='cache-builtin-clear'),

    url(r'^zato/cache/builtin/entries/(?P<cache_id>.*)/delete/$',
        login_required(cache_builtin_entries.Delete()), name=cache_builtin_entries.Delete.url_name),

    url(r'^zato/cache/builtin/entries/(?P<cache_id>.*)/$',
        login_required(cache_builtin_entries.Index()), name=cache_builtin_entries.Index.url_name),

    url(r'^zato/cache/builtin/details/entry/create/cache-id/(?P<cache_id>.*)/cluster/(?P<cluster_id>.*)/action/$',
        login_required(cache_builtin_entry.create_action), name='cache-builtin-create-entry-action'),

    url(r'^zato/cache/builtin/details/entry/create/cache-id/(?P<cache_id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cache_builtin_entry.create), name='cache-builtin-create-entry'),

    url(r'^zato/cache/builtin/details/entry/edit/cache-id/(?P<cache_id>.*)/cluster/(?P<cluster_id>.*)/action/$',
        login_required(cache_builtin_entry.edit_action), name='cache-builtin-edit-entry-action'),

    url(r'^zato/cache/builtin/details/entry/edit/cache-id/(?P<cache_id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cache_builtin_entry.edit), name='cache-builtin-edit-entry'),

    # .. Memcached

    url(r'^zato/cache/memcached/$',
        login_required(cache_memcached.Index()), name=cache_memcached.Index.url_name),
    url(r'^zato/cache/memcached/create/$',
        login_required(cache_memcached.Create()), name=cache_memcached.Create.url_name),
    url(r'^zato/cache/memcached/edit/$',
        login_required(cache_memcached.Edit()), name=cache_memcached.Edit.url_name),
    url(r'^zato/cache/memcached/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cache_memcached.Delete()), name=cache_memcached.Delete.url_name),
    url(r'^zato/cache/memcached/details/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cache_memcached.DetailsIndex()), name=cache_memcached.DetailsIndex.url_name),

    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Search
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # .. ElasticSearch

    url(r'^zato/search/es/$',
        login_required(es.Index()), name=es.Index.url_name),
    url(r'^zato/search/es/create/$',
        login_required(es.Create()), name=es.Create.url_name),
    url(r'^zato/search/es/edit/$',
        login_required(es.Edit()), name=es.Edit.url_name),
    url(r'^zato/search/es/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(es.Delete()), name=es.Delete.url_name),

    # .. Solr

    url(r'^zato/search/solr/$',
        login_required(solr.Index()), name=solr.Index.url_name),
    url(r'^zato/search/solr/create/$',
        login_required(solr.Create()), name=solr.Create.url_name),
    url(r'^zato/search/solr/edit/$',
        login_required(solr.Edit()), name=solr.Edit.url_name),
    url(r'^zato/search/solr/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(solr.Delete()), name=solr.Delete.url_name),
    url(r'^zato/search/solr/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(solr.ping), name='search-solr-ping'),

    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Notifications
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # .. OpenStack Swift

    url(r'^zato/notif/cloud/openstack/swift/$',
        login_required(notif_cloud_openstack_swift.Index()), name=notif_cloud_openstack_swift.Index.url_name),
    url(r'^zato/notif/cloud/openstack/swift/create/$',
        login_required(notif_cloud_openstack_swift.Create()), name=notif_cloud_openstack_swift.Create.url_name),
    url(r'^zato/notif/cloud/openstack/swift/edit/$',
        login_required(notif_cloud_openstack_swift.Edit()), name=notif_cloud_openstack_swift.Edit.url_name),
    url(r'^zato/notif/cloud/openstack/swift/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(notif_cloud_openstack_swift.Delete()), name=notif_cloud_openstack_swift.Delete.url_name),

    url(r'^zato/notif/sql/$',
        login_required(notif_sql.Index()), name=notif_sql.Index.url_name),
    url(r'^zato/notif/sql/create/$',
        login_required(notif_sql.Create()), name=notif_sql.Create.url_name),
    url(r'^zato/notif/sql/edit/$',
        login_required(notif_sql.Edit()), name=notif_sql.Edit.url_name),
    url(r'^zato/notif/sql/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(notif_sql.Delete()), name=notif_sql.Delete.url_name),

    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Query
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # .. Cassandra

    url(r'^zato/query/cassandra/$',
        login_required(query_cassandra.Index()), name=query_cassandra.Index.url_name),
    url(r'^zato/query/cassandra/create/$',
        login_required(query_cassandra.Create()), name=query_cassandra.Create.url_name),
    url(r'^zato/query/cassandra/edit/$',
        login_required(query_cassandra.Edit()), name=query_cassandra.Edit.url_name),
    url(r'^zato/query/cassandra/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(query_cassandra.Delete()), name=query_cassandra.Delete.url_name),
    ]

urlpatterns += [

    # .. MongoDB

    url(r'^zato/outgoing/mongodb/$',
        login_required(out_mongodb.Index()), name=out_mongodb.Index.url_name),
    url(r'^zato/outgoing/mongodb/create/$',
        login_required(out_mongodb.Create()), name=out_mongodb.Create.url_name),
    url(r'^zato/outgoing/mongodb/edit/$',
        login_required(out_mongodb.Edit()), name=out_mongodb.Edit.url_name),
    url(r'^zato/outgoing/mongodb/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_mongodb.Delete()), name=out_mongodb.Delete.url_name),
    url(r'^zato/outgoing/mongodb/change-password/$',
        login_required(out_mongodb.change_password), name='out-mongodb-change-password'),
    url(r'^zato/outgoing/mongodb/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_mongodb.ping), name='out-mongodb-ping'),
    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   IM
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # .. Slack

    url(r'^zato/outgoing/im/slack/$',
        login_required(out_im_slack.Index()), name=out_im_slack.Index.url_name),
    url(r'^zato/outgoing/im/slack/create/$',
        login_required(out_im_slack.Create()), name=out_im_slack.Create.url_name),
    url(r'^zato/outgoing/im/slack/edit/$',
        login_required(out_im_slack.Edit()), name=out_im_slack.Edit.url_name),
    url(r'^zato/outgoing/im/slack/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_im_slack.Delete()), name=out_im_slack.Delete.url_name),
    url(r'^zato/outgoing/im/slack/change-password/$',
        login_required(out_im_slack.change_password), name='out-im-slack-change-password'),
    url(r'^zato/outgoing/im/slack/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_im_slack.ping), name='out-im-slack-ping'),
    ]

urlpatterns += [

    # .. Telegram

    url(r'^zato/outgoing/im/telegram/$',
        login_required(out_im_telegram.Index()), name=out_im_telegram.Index.url_name),
    url(r'^zato/outgoing/im/telegram/create/$',
        login_required(out_im_telegram.Create()), name=out_im_telegram.Create.url_name),
    url(r'^zato/outgoing/im/telegram/edit/$',
        login_required(out_im_telegram.Edit()), name=out_im_telegram.Edit.url_name),
    url(r'^zato/outgoing/im/telegram/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_im_telegram.Delete()), name=out_im_telegram.Delete.url_name),
    url(r'^zato/outgoing/im/telegram/change-password/$',
        login_required(out_im_telegram.change_password), name='out-im-telegram-change-password'),
    url(r'^zato/outgoing/im/telegram/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_im_telegram.ping), name='out-im-telegram-ping'),
    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   E-mail
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # .. IMAP

    url(r'^zato/email/imap/$',
        login_required(email_imap.Index()), name=email_imap.Index.url_name),
    url(r'^zato/email/imap/create/$',
        login_required(email_imap.Create()), name=email_imap.Create.url_name),
    url(r'^zato/email/imap/edit/$',
        login_required(email_imap.Edit()), name=email_imap.Edit.url_name),
    url(r'^zato/email/imap/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(email_imap.Delete()), name=email_imap.Delete.url_name),
    url(r'^zato/email/imap/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(email_imap.ping), name='imap-email-ping'),
    url(r'^zato/email/imap/change-password/$',
        login_required(email_imap.change_password), name='email-imap-change-password'),

    # .. SMTP

    url(r'^zato/email/smtp/$',
        login_required(email_smtp.Index()), name=email_smtp.Index.url_name),
    url(r'^zato/email/smtp/create/$',
        login_required(email_smtp.Create()), name=email_smtp.Create.url_name),
    url(r'^zato/email/smtp/edit/$',
        login_required(email_smtp.Edit()), name=email_smtp.Edit.url_name),
    url(r'^zato/email/smtp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(email_smtp.Delete()), name=email_smtp.Delete.url_name),
    url(r'^zato/email/smtp/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(email_smtp.ping), name='smtp-email-ping'),
    url(r'^zato/email/smtp/change-password/$',
        login_required(email_smtp.change_password), name='email-smtp-change-password'),

    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   SMS
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # .. Twilio

    url(r'^zato/sms/twilio/$',
        login_required(twilio.Index()), name=twilio.Index.url_name),
    url(r'^zato/sms/twilio/create/$',
        login_required(twilio.Create()), name=twilio.Create.url_name),
    url(r'^zato/sms/twilio/edit/$',
        login_required(twilio.Edit()), name=twilio.Edit.url_name),
    url(r'^zato/sms/twilio/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(twilio.Delete()), name=twilio.Delete.url_name),

    url(r'^zato/sms/twilio/send/cluster/(?P<cluster_id>.*)/conn/(?P<conn_id>.*)/(?P<name_slug>.*)$',
        login_required(twilio.send_message), name='sms-twilio-send-message'),
    url(r'^zato/sms/twilio/send/action/cluster/(?P<cluster_id>.*)/conn/(?P<conn_id>.*)/(?P<name_slug>.*)$',
        login_required(twilio.send_message_action), name='sms-twilio-send-message-action'),

    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Cloud
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # .. OpenStack - S3

    url(r'^zato/cloud/aws/s3/$',
        login_required(cloud_aws_s3.Index()), name=cloud_aws_s3.Index.url_name),
    url(r'^zato/cloud/aws/s3/create/$',
        login_required(cloud_aws_s3.Create()), name=cloud_aws_s3.Create.url_name),
    url(r'^zato/cloud/aws/s3/edit/$',
        login_required(cloud_aws_s3.Edit()), name=cloud_aws_s3.Edit.url_name),
    url(r'^zato/cloud/aws/s3/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cloud_aws_s3.Delete()), name=cloud_aws_s3.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. Dropbox

    url(r'^zato/cloud/dropbox/$',
        login_required(cloud_dropbox.Index()), name=cloud_dropbox.Index.url_name),
    url(r'^zato/cloud/dropbox/create/$',
        login_required(cloud_dropbox.Create()), name=cloud_dropbox.Create.url_name),
    url(r'^zato/cloud/dropbox/edit/$',
        login_required(cloud_dropbox.Edit()), name=cloud_dropbox.Edit.url_name),
    url(r'^zato/cloud/dropbox/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cloud_dropbox.Delete()), name=cloud_dropbox.Delete.url_name),
    url(r'^zato/cloud/dropbox/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cloud_dropbox.ping), name='cloud-dropbox-ping'),
    url(r'^zato/cloud/dropbox/change-password/$',
        login_required(cloud_dropbox.change_password), name='cloud-dropbox-change-password'),
    ]

# ################################################################################################################################

urlpatterns += [

    # .. OpenStack - Swift

    url(r'^zato/cloud/openstack/swift/$',
        login_required(cloud_openstack_swift.Index()), name=cloud_openstack_swift.Index.url_name),
    url(r'^zato/cloud/openstack/swift/create/$',
        login_required(cloud_openstack_swift.Create()), name=cloud_openstack_swift.Create.url_name),
    url(r'^zato/cloud/openstack/swift/edit/$',
        login_required(cloud_openstack_swift.Edit()), name=cloud_openstack_swift.Edit.url_name),
    url(r'^zato/cloud/openstack/swift/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cloud_openstack_swift.Delete()), name=cloud_openstack_swift.Delete.url_name),
    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   KVDB
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    url(r'^zato/kvdb/remote-command/$',
        login_required(kvdb.remote_command), name='kvdb-remote-command'),
    url(r'^zato/kvdb/remote-command/execute/$',
        login_required(kvdb.remote_command_execute), name='kvdb-remote-command-execute'),
    url(r'^zato/kvdb/data-dict/dictionary/$',
        login_required(dictionary.Index()), name=dictionary.Index.url_name),
    url(r'^zato/kvdb/data-dict/dictionary/create/$',
        login_required(dictionary.Create()), name=dictionary.Create.url_name),
    url(r'^zato/kvdb/data-dict/dictionary/edit/$',
        login_required(dictionary.Edit()), name=dictionary.Edit.url_name),
    url(r'^zato/kvdb/data-dict/dictionary/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(dictionary.Delete()), name=dictionary.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    url(r'^zato/kvdb/data-dict/translation/$',
        login_required(translation.Index()), name=translation.Index.url_name),
    url(r'^zato/kvdb/data-dict/translation/create/$',
        login_required(translation.Create()), name=translation.Create.url_name),
    url(r'^zato/kvdb/data-dict/translation/edit/$',
        login_required(translation.Edit()), name=translation.Edit.url_name),
    url(r'^zato/kvdb/data-dict/translation/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(translation.Delete()), name=translation.Delete.url_name),
    url(r'^zato/kvdb/data-dict/translation/get-key-list/$',
        login_required(translation.get_key_list), name='kvdb-data-dict-translation-get-key-list'),
    url(r'^zato/kvdb/data-dict/translation/get-value-list/$',
        login_required(translation.get_value_list), name='kvdb-data-dict-translation-get-value-list'),
    url(r'^zato/kvdb/data-dict/translation/translate/$',
        login_required(translation.translate), name='kvdb-data-dict-translation-translate'),
    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Pub/sub
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # Pub/sub - endpoints

    url(r'^zato/pubsub/endpoint/$',
        login_required(pubsub_endpoint.Index()), name=pubsub_endpoint.Index.url_name),
    url(r'^zato/pubsub/endpoint/create/$',
        login_required(pubsub_endpoint.Create()), name=pubsub_endpoint.Create.url_name),
    url(r'^zato/pubsub/endpoint/edit/$',
        login_required(pubsub_endpoint.Edit()), name=pubsub_endpoint.Edit.url_name),
    url(r'^zato/pubsub/endpoint/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(pubsub_endpoint.Delete()), name=pubsub_endpoint.Delete.url_name),
    url(r'^zato/pubsub/endpoint/topics/(?P<cluster_id>.*)/endpoint/(?P<endpoint_id>.*)/(?P<name_slug>.*)$',
        login_required(pubsub_endpoint.EndpointTopics()), name=pubsub_endpoint.EndpointTopics.url_name),

    url(r'^zato/pubsub/endpoint/queues/(?P<cluster_id>.*)/endpoint/(?P<endpoint_id>.*)/(?P<name_slug>.*)$',
        login_required(pubsub_endpoint.EndpointQueues()), name=pubsub_endpoint.EndpointQueues.url_name),

    url(r'^zato/pubsub/endpoint/queue/delete/(?P<sub_id>.*)/(?P<sub_key>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(pubsub_endpoint.endpoint_queue_delete), name='pubsub-endpoint-queue-delete'),

    url(r'^zato/pubsub/endpoint/topic-sub-list/(?P<endpoint_id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(pubsub_endpoint.endpoint_topic_sub_list), name='pubsub-endpoint-topic-sub-list'),

    url(r'^zato/pubsub/endpoint/queue/clear/cluster/(?P<cluster_id>.*)/queue/(?P<sub_key>.*)/$',
        login_required(pubsub_endpoint.endpoint_queue_clear), name='pubsub-endpoint-queue-clear'),

    url(r'^zato/pubsub/endpoint/queue/edit/$',
        login_required(pubsub_endpoint.endpoint_queue_edit), name='pubsub-endpoint-queue-edit'),

    url(r'^zato/pubsub/endpoint/queue/interactions/cluster/(?P<cluster_id>.*)/queue/(?P<sub_id>.*)/(?P<name_slug>.*)$',
        login_required(pubsub_endpoint.endpoint_queue_interactions), name='pubsub-endpoint-queue-interactions'),

    url(r'^zato/pubsub/endpoint/queue/browser/gd/(?P<has_gd>.*)/queue/(?P<sub_id>.*)/(?P<name_slug>.*)$',
        login_required(pubsub_endpoint.EndpointQueueBrowser()), name=pubsub_endpoint.EndpointQueueBrowser.url_name),

    # Pub/sub - topics

    url(r'^zato/pubsub/topic/$',
        login_required(pubsub_topic.Index()), name=pubsub_topic.Index.url_name),
    url(r'^zato/pubsub/topic/create/$',
        login_required(pubsub_topic.Create()), name=pubsub_topic.Create.url_name),
    url(r'^zato/pubsub/topic/edit/$',
        login_required(pubsub_topic.Edit()), name=pubsub_topic.Edit.url_name),
    url(r'^zato/pubsub/topic/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(pubsub_topic.Delete()), name=pubsub_topic.Delete.url_name),
    url(r'^zato/pubsub/topic/clear/cluster/(?P<cluster_id>.*)/topic/(?P<topic_id>.*)/$',
        login_required(pubsub_topic.topic_clear), name='pubsub-topic-clear'),
    url(r'^zato/pubsub/topic/publishers/(?P<cluster_id>.*)/topic/(?P<topic_id>.*)/(?P<name_slug>.*)$',
        login_required(pubsub_topic.TopicPublishers()), name=pubsub_topic.TopicPublishers.url_name),
    url(r'^zato/pubsub/topic/subscribers/(?P<cluster_id>.*)/topic/(?P<topic_id>.*)/(?P<name_slug>.*)$',
        login_required(pubsub_topic.TopicSubscribers()), name=pubsub_topic.TopicSubscribers.url_name),
    url(r'^zato/pubsub/topic/messages/(?P<topic_id>.*)/(?P<name_slug>.*)$',
        login_required(pubsub_topic.TopicMessages()), name=pubsub_topic.TopicMessages.url_name),

    # Pub/sub - subscriptions

    url(r'^zato/pubsub/subscription/$',
        login_required(pubsub_subscription.Index()), name=pubsub_subscription.Index.url_name),
    url(r'^zato/pubsub/subscription/create/$',
        login_required(pubsub_subscription.Create()), name=pubsub_subscription.Create.url_name),
    url(r'^zato/pubsub/subscription/edit/$',
        login_required(pubsub_subscription.Edit()), name=pubsub_subscription.Edit.url_name),
    url(r'^zato/pubsub/subscription/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(pubsub_subscription.Delete()), name=pubsub_subscription.Delete.url_name),

    # Details of an individual message
    url(r'^zato/pubsub/message/details/cluster/(?P<cluster_id>.*)/(?P<object_type>.*)/(?P<object_id>.*)/msg/(?P<msg_id>.*)$',
        login_required(pubsub_message.get), name='pubsub-message'),

    # Updates an individual message
    url(r'^zato/pubsub/message/update/cluster/(?P<cluster_id>.*)/msg/(?P<msg_id>.*)$',
        login_required(pubsub_message.update_action), name='pubsub-message-update'),

    # Deletes an individual message
    url(r'^zato/pubsub/message/delete/cluster/(?P<cluster_id>.*)/msg/(?P<msg_id>.*)$',
        login_required(pubsub_message.delete), name='pubsub-message-delete'),

    # Publishes a message to topic (POST action)
    url(r'^zato/pubsub/message/publish-action/$',
        login_required(pubsub_message.publish_action), name='pubsub-message-publish-action'),

    # Publishes a message to topic (GET form)
    url(r'^zato/pubsub/message/publish/cluster/(?P<cluster_id>.*)/topic/(?P<topic_id>.*)$',
        login_required(pubsub_message.publish), name='pubsub-message-publish'),

    # Delivery tasks

    url(r'^zato/pubsub/task/delivery/$',
        login_required(pubsub_task_delivery_server.Index()), name=pubsub_task_delivery_server.Index.url_name),

    # In-flight messages from a delivery task
    url(r'^zato/pubsub/task/delivery/browser/in-flight/(?P<server_name>.*)/(?P<server_pid>.*)/(?P<python_id>.*)/$',
        login_required(pubsub_task_message.MessageBrowserInFlight()), name=pubsub_task_message.MessageBrowserInFlight.url_name),

    # History of messages in a delivery task
    url(r'^zato/pubsub/task/delivery/browser/history/(?P<server_name>.*)/(?P<server_pid>.*)/(?P<python_id>.*)/$',
        login_required(pubsub_task_message.MessageBrowserHistory()), name=pubsub_task_message.MessageBrowserHistory.url_name),

    # Details of an individual in-flight message
    url(r'^zato/pubsub/task/delivery/browser/message/(?P<server_name>.*)/(?P<server_pid>.*)/(?P<python_id>.*)/(?P<msg_id>.*)$',
        login_required(pubsub_task_message.get), name='pubsub-task-message'),

    # PubSub objects / tools
    url(r'^zato/pubsub/task/sync/$',
        login_required(pubsub_task_sync.Index()), name=pubsub_task_sync.Index.url_name),

    # PubSub tools - dict keys
    url(r'^zato/pubsub/task/sync/dict-keys/(?P<dict_name>.*)/cluster/(?P<cluster>.*)/(?P<server_name>.*)/(?P<server_pid>.*)/$',
        login_required(pubsub_task_sync.SubscriptionDictKeys()), name=pubsub_task_sync.SubscriptionDictKeys.url_name),

    # PubSub tools - dict values - subscriptions
    url(r'^zato/pubsub/task/sync/dict-values/sub/(?P<dict_name>.*)/cluster/(?P<cluster>.*)/(?P<server_name>.*)/(?P<server_pid>.*)/$',
        login_required(pubsub_task_sync.DictValuesSubscriptions()), name=pubsub_task_sync.DictValuesSubscriptions.url_name),

    # PubSub tools - dict values - sub key servers
    url(r'^zato/pubsub/task/sync/dict-values/sks/(?P<dict_name>.*)/cluster/(?P<cluster>.*)/(?P<server_name>.*)/(?P<server_pid>.*)/$',
        login_required(pubsub_task_sync.DictValuesSubKeyServer()), name=pubsub_task_sync.DictValuesSubKeyServer.url_name),

    # PubSub tools - dict values - endpoints
    url(r'^zato/pubsub/task/sync/dict-values/endpoint/(?P<dict_name>.*)/cluster/(?P<cluster>.*)/(?P<server_name>.*)/(?P<server_pid>.*)/$',
        login_required(pubsub_task_sync.DictValuesEndpoints()), name=pubsub_task_sync.DictValuesEndpoints.url_name),

    # PubSub tools - dict values - topics
    url(r'^zato/pubsub/task/sync/dict-values/topic/(?P<dict_name>.*)/cluster/(?P<cluster>.*)/(?P<server_name>.*)/(?P<server_pid>.*)/$',
        login_required(pubsub_task_sync.DictValuesTopics()), name=pubsub_task_sync.DictValuesTopics.url_name),

    # PubSub tools - event list
    url(r'^zato/pubsub/task/sync/event-list/cluster/(?P<cluster>.*)/(?P<server_name>.*)/(?P<server_pid>.*)/$',
        login_required(pubsub_task_sync.EventList()), name=pubsub_task_sync.EventList.url_name),

    # Per-server delivery tasks

    url(r'^zato/pubsub/task/(?P<server_name>.*)/(?P<server_pid>.*)/$',
        login_required(pubsub_task.Index()), name=pubsub_task.Index.url_name),
    url(r'^zato/pubsub/task/clear-messages/(?P<server_name>.*)/(?P<server_pid>.*)/(?P<task_id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(pubsub_task.clear_messages), name='pubsub.task.clear-messages'),
    url(r'^zato/pubsub/task/toggle-active/(?P<server_name>.*)/(?P<server_pid>.*)/(?P<task_id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(pubsub_task.toggle_active), name='pubsub.task.toggle-active'),
]

# ################################################################################################################################

urlpatterns += [

    url(r'^zato/kvdb/data-dict/impexp/$',
        login_required(impexp.index), name='kvdb-data-dict-impexp'),
    url(r'^zato/kvdb/data-dict/impexp/cluster/(?P<cluster_id>.*)/import/$',
        login_required(impexp.import_), name='kvdb-data-dict-impexp-import'),
    url(r'^zato/kvdb/data-dict/impexp/cluster/(?P<cluster_id>.*)/export/$',
        login_required(impexp.export), name='kvdb-data-dict-impexp-export'),
    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Statistics
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # Statistics

    url(r'^zato/stats/trends/data/$',
        login_required(stats.stats_trends_data), name='stats-trends-data'),
    url(r'^zato/stats/trends/(?P<choice>.*)/$',
        login_required(stats.trends), name='stats-trends'),
    url(r'^zato/stats/summary/data/$',
        login_required(stats.stats_summary_data), name='stats-summary-data'),
    url(r'^zato/stats/summary/(?P<choice>.*)/$',
        login_required(stats.summary), name='stats-summary'),
    url(r'^zato/stats/settings/$',
        login_required(stats.settings), name='stats-settings'),
    url(r'^zato/stats/settings/save/$',
        login_required(stats.settings_save), name='stats-settings-save'),
    url(r'^zato/stats/maintenance/$',
        login_required(stats.maintenance), name='stats-maintenance'),
    url(r'^zato/stats/maintenance/delete/$',
        login_required(stats.maintenance_delete), name='stats-maintenance-delete'),
    ]

# ################################################################################################################################

urlpatterns += [
    url(r'^static/(?P<path>.*)$', django_static_serve, {'document_root': settings.MEDIA_ROOT}),
]
