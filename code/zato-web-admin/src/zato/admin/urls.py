# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.urls import path, re_path as url
from django.contrib.auth.decorators import login_required

# Zato
from zato.admin import settings
from zato.admin.web.util import static_serve
from zato.admin.web.views import account, http_soap, log_streaming, main, scheduler, service, updates
from zato.admin.web.views.cache import builtin as cache_builtin
from zato.admin.web.views.cache.builtin import entries as cache_builtin_entries
from zato.admin.web.views.cache.builtin import entry as cache_builtin_entry
from zato.admin.web.views.channel import amqp_ as channel_amqp
from zato.admin.web.views.cloud import confluence as cloud_confluence
from zato.admin.web.views.cloud import jira as cloud_jira
from zato.admin.web.views.cloud import microsoft_365 as cloud_microsoft_365
from zato.admin.web.views.cloud import salesforce as cloud_salesforce
from zato.admin.web.views.email import imap as email_imap
from zato.admin.web.views.email import smtp as email_smtp
from zato.admin.web.views import groups
from zato.admin.web.views.outgoing import amqp_ as out_amqp
from zato.admin.web.views.outgoing import ftp as out_ftp
from zato.admin.web.views.outgoing import ldap as out_ldap
from zato.admin.web.views.outgoing import mongodb as out_mongodb
from zato.admin.web.views.outgoing import odoo as out_odoo
from zato.admin.web.views.outgoing import sap as out_sap
from zato.admin.web.views.outgoing import sql as out_sql
from zato.admin.web.views.search import es
from zato.admin.web.views.service import ide as service_ide
from zato.admin.web.views.security import apikey, basic_auth, ntlm
from zato.admin.web.views.security.oauth import outconn_client_credentials as oauth_outconn_client_credentials
from zato.admin.web.views.stats import user as stats_user
from zato.admin.web.views.monitoring import config as monitoring_config
from zato.admin.web.views.monitoring import dashboard as monitoring_dashboard
from zato.admin.web.views.monitoring.wizard import health as monitoring_wizard_health
from zato.admin.web.views.vendors import keysight_vision
from zato.admin.web.views.pubsub import topic
from zato.admin.web.views.pubsub import client
from zato.admin.web.views.pubsub import permission
from zato.admin.web.views.pubsub import subscription

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

    # Services

    url(r'^zato/service/$',
        login_required(service.Index()), name=service.Index.url_name),
    url(r'^zato/service/details$',
        login_required(service.Index()), name=service.Index.url_name),
    url(r'^zato/service/upload/$',
        login_required(service.upload), name='service-package-upload'),
    url(r'^zato/service/edit/$',
        login_required(service.Edit()), name=service.Edit.url_name),
    url(r'^zato/service/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(service.Delete()), name=service.Delete.url_name),
    url(r'^zato/service/overview/(?P<service_name>.*)/$',
        login_required(service.overview), name='service-overview'),
    url(r'^zato/service/invoke/(?P<name>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(service.invoke), name='service-invoke'),
    url(r'^zato/service/ide/get-service/(?P<service_name>.*)/$',
        login_required(service_ide.get_service), name='service-ide-get-service'),
    url(r'^zato/service/ide/create-file/$',
        login_required(service_ide.create_file), name='service-ide-create-file'),
    url(r'^zato/service/ide/delete-file/$',
        login_required(service_ide.delete_file), name='service-ide-delete-file'),
    url(r'^zato/service/ide/rename-file/$',
        login_required(service_ide.rename_file), name='service-ide-rename-file'),
    url(r'^zato/service/ide/get-file/(?P<fs_location>.*)/$',
        login_required(service_ide.get_file), name='service-ide-get-file'),
    url(r'^zato/service/ide/get-file-list/$',
        login_required(service_ide.get_file_list), name='service-ide-get-file-list'),
    url(r'^zato/service/ide/get-service-list/$',
        login_required(service_ide.get_service_list), name='service-ide-get-service-list'),
    url(r'^zato/service/ide/(?P<object_type>.*)/(?P<name>.*)/$',
        login_required(service_ide.IDE()), name=service_ide.IDE.url_name),
    url(r'^zato/service/enmasse-export$',
        login_required(service.enmasse_export), name='service-enmasse-export'), # type: ignore
    url(r'^zato/service/enmasse-import$',
        login_required(service.enmasse_import), name='service-enmasse-import'), # type: ignore
    url(r'^zato/pubsub/import-test-config$',
        login_required(service.import_test_config), name='pubsub-import-test-config'), # type: ignore
    url(r'^zato/pubsub/download-openapi$',
        login_required(service.download_openapi), name='pubsub-download-openapi'), # type: ignore
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

    # .. HTTP Basic Auth

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

    # .. OAuth - Outgoing connections

    url(r'^zato/security/oauth/outconn/client-credentials/$',
        login_required(oauth_outconn_client_credentials.Index()), name=oauth_outconn_client_credentials.Index.url_name),
    url(r'^zato/security/oauth/outconn/client-credentials/create/$',
        login_required(oauth_outconn_client_credentials.Create()), name=oauth_outconn_client_credentials.Create.url_name),
    url(r'^zato/security/oauth/outconn/client-credentials/edit/$',
        login_required(oauth_outconn_client_credentials.Edit()), name=oauth_outconn_client_credentials.Edit.url_name),
    url(r'^zato/security/oauth/outconn/client-credentials/change-secret/$',
        login_required(oauth_outconn_client_credentials.change_secret),
            name='security-oauth-outconn-client-credentials-change-secret'),
    url(r'^zato/security/oauth/outconn/client-credentials/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(oauth_outconn_client_credentials.Delete()), name=oauth_outconn_client_credentials.Delete.url_name),
    ]

# ################################################################################################################################

urlpatterns += [

    # Scheduler

    url(r'^zato/scheduler/$', login_required(scheduler.index), name='scheduler'),
    url(r'^zato/scheduler/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(scheduler.Delete()), name=scheduler.Delete.url_name),
    url(r'^zato/scheduler/execute/(?P<job_id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(scheduler.execute), name='scheduler-job-execute'),
    url(r'^zato/scheduler/get-definition/(?P<start_date>.*)/(?P<repeat>.*)/' + \
        '(?P<weeks>.*)/(?P<days>.*)/(?P<hours>.*)/(?P<minutes>.*)/(?P<seconds>.*)/$',
        login_required(scheduler.get_definition), name='scheduler-job-get-definition'),
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

    url(r'^zato/outgoing/amqp/$', login_required(out_amqp.Index()), name=out_amqp.Index.url_name),
    url(r'^zato/outgoing/amqp/create/$', login_required(out_amqp.create), name='out-amqp-create'),
    url(r'^zato/outgoing/amqp/edit/$', login_required(out_amqp.edit), name='out-amqp-edit'),
    url(r'^zato/outgoing/amqp/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(out_amqp.Delete()), name=out_amqp.Delete.url_name),

    url(r'^zato/outgoing/amqp/invoke/action/(?P<conn_name>.*)/$',
        login_required(out_amqp.invoke_action), name='out-amqp-invoke-action'),

    url(r'^zato/outgoing/amqp/invoke/(?P<conn_id>.*)/(?P<conn_name>.*)/(?P<conn_slug>.*)/$',
        login_required(out_amqp.invoke), name='out-amqp-invoke'),

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

    # HTTP

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
    url(r'^zato/http-soap/get-security-groups/(?P<group_type>.*)/$',
        login_required(groups.get_group_list), name='http-soap-get-all-security-groups'),

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

    url(r'^zato/cache/builtin/entries/(?P<id>.*)/delete/$',
        login_required(cache_builtin_entries.Delete()), name=cache_builtin_entries.Delete.url_name),

    url(r'^zato/cache/builtin/entries/(?P<id>.*)/$',
        login_required(cache_builtin_entries.Index()), name=cache_builtin_entries.Index.url_name),

    url(r'^zato/cache/builtin/details/entry/create/cache-id/(?P<id>.*)/cluster/(?P<cluster_id>.*)/action/$',
        login_required(cache_builtin_entry.create_action), name='cache-builtin-create-entry-action'),

    url(r'^zato/cache/builtin/details/entry/create/cache-id/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cache_builtin_entry.create), name='cache-builtin-create-entry'),

    url(r'^zato/cache/builtin/details/entry/edit/cache-id/(?P<id>.*)/cluster/(?P<cluster_id>.*)/action/$',
        login_required(cache_builtin_entry.edit_action), name='cache-builtin-edit-entry-action'),

    url(r'^zato/cache/builtin/details/entry/edit/cache-id/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cache_builtin_entry.edit), name='cache-builtin-edit-entry'),

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

    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   NoSQL
# #
# ################################################################################################################################
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
# #   Cloud
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # .. Jira

    url(r'^zato/cloud/confluence/$',
        login_required(cloud_confluence.Index()), name=cloud_confluence.Index.url_name),
    url(r'^zato/cloud/confluence/create/$',
        login_required(cloud_confluence.Create()), name=cloud_confluence.Create.url_name),
    url(r'^zato/cloud/confluence/edit/$',
        login_required(cloud_confluence.Edit()), name=cloud_confluence.Edit.url_name),
    url(r'^zato/cloud/confluence/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cloud_confluence.Delete()), name=cloud_confluence.Delete.url_name),
    url(r'^zato/cloud/confluence/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cloud_confluence.ping), name='cloud-dropbox-ping'),
    url(r'^zato/cloud/confluence/change-password/$',
        login_required(cloud_confluence.change_password), name='cloud-confluence-change-password'),
    ]

urlpatterns += [

    # .. Jira

    url(r'^zato/cloud/jira/$',
        login_required(cloud_jira.Index()), name=cloud_jira.Index.url_name),
    url(r'^zato/cloud/jira/create/$',
        login_required(cloud_jira.Create()), name=cloud_jira.Create.url_name),
    url(r'^zato/cloud/jira/edit/$',
        login_required(cloud_jira.Edit()), name=cloud_jira.Edit.url_name),
    url(r'^zato/cloud/jira/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cloud_jira.Delete()), name=cloud_jira.Delete.url_name),
    url(r'^zato/cloud/jira/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cloud_jira.ping), name='cloud-jira-ping'),
    url(r'^zato/cloud/jira/change-password/$',
        login_required(cloud_jira.change_password), name='cloud-jira-change-password'),
    ]

urlpatterns += [

    # .. Microsoft 365

    url(r'^zato/cloud/microsoft-365/$',
        login_required(cloud_microsoft_365.Index()), name=cloud_microsoft_365.Index.url_name),
    url(r'^zato/cloud/microsoft-365/create/$',
        login_required(cloud_microsoft_365.Create()), name=cloud_microsoft_365.Create.url_name),
    url(r'^zato/cloud/microsoft-365/edit/$',
        login_required(cloud_microsoft_365.Edit()), name=cloud_microsoft_365.Edit.url_name),
    url(r'^zato/cloud/microsoft-365/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cloud_microsoft_365.Delete()), name=cloud_microsoft_365.Delete.url_name),
    url(r'^zato/cloud/microsoft-365/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cloud_microsoft_365.ping), name='cloud-microsoft-365-ping'),
    url(r'^zato/cloud/jira/reset-oauth2-scopes/$',
        login_required(cloud_microsoft_365.reset_oauth2_scopes), name='cloud-microsoft-365-reset-oauth2-scopes'),
    ]

urlpatterns += [

    # .. Salesforce

    url(r'^zato/cloud/salesforce/$',
        login_required(cloud_salesforce.Index()), name=cloud_salesforce.Index.url_name),
    url(r'^zato/cloud/salesforce/create/$',
        login_required(cloud_salesforce.Create()), name=cloud_salesforce.Create.url_name),
    url(r'^zato/cloud/salesforce/edit/$',
        login_required(cloud_salesforce.Edit()), name=cloud_salesforce.Edit.url_name),
    url(r'^zato/cloud/salesforce/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cloud_salesforce.Delete()), name=cloud_salesforce.Delete.url_name),
    url(r'^zato/cloud/salesforce/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(cloud_salesforce.ping), name='cloud-dropbox-ping'),

    url(r'^zato/cloud/salesforce/invoke/action/(?P<conn_name>.*)/$',
        login_required(cloud_salesforce.invoke_action), name='cloud-salesforce-invoke-action'),

    url(r'^zato/cloud/salesforce/invoke/(?P<conn_id>.*)/(?P<max_wait_time>.*)/(?P<conn_name>.*)/(?P<conn_slug>.*)/$',
        login_required(cloud_salesforce.invoke), name='cloud-salesforce-invoke'),

    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Statistics
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # Statistics - user-defined
    url(r'^zato/stats/user/$',
        login_required(stats_user.Index()), name=stats_user.Index.url_name),

    # Statistics - user-defined - latest updates
    url(r'^zato/stats/user/get-updates/$',
        login_required(stats_user.get_updates), name='stats-user-get-updates'),
    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Monitoring
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # Monitoring - configuration
    url(r'^zato/monitoring/config/$',
        login_required(monitoring_config.config), name='monitoring-config'),

    # Monitoring - wizard - health
    url(r'^zato/monitoring/wizard/health/$',
        login_required(monitoring_wizard_health.health), name='monitoring-wizard-health'),

    # Monitoring - dashboard creation
    url(r'^zato/monitoring/dashboard/create/$',
        login_required(monitoring_dashboard.dashboard_create_page), name='monitoring-dashboard-create'),
    url(r'^zato/monitoring/dashboard/create/grafana/$',
        monitoring_dashboard.create_grafana_dashboard, name='monitoring-dashboard-create-grafana'),
    url(r'^zato/monitoring/dashboard/create/datadog/$',
        monitoring_dashboard.create_datadog_dashboard, name='monitoring-dashboard-create-datadog'),
    url(r'^zato/monitoring/dashboard/try/$',
        monitoring_dashboard.try_service_code, name='monitoring-dashboard-try'),
    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Vendors
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # Vendors - Keysight Vision Series
    url(r'^zato/vendors/keysight/vision/$',
        login_required(keysight_vision.Index()), name=keysight_vision.Index.url_name),
    url(r'^zato/vendors/keysight/vision/create/$',
        login_required(keysight_vision.Create()), name=keysight_vision.Create.url_name),
    url(r'^zato/vendors/keysight/vision/edit/$',
        login_required(keysight_vision.Edit()), name=keysight_vision.Edit.url_name),
    url(r'^zato/vendors/keysight/vision/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(keysight_vision.Delete()), name=keysight_vision.Delete.url_name),
    url(r'^zato/vendors/keysight/vision/ping/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(keysight_vision.ping), name='vendors-keysight-vision-ping'),
    url(r'^zato/vendors/keysight/vision/change-password/$',
        login_required(keysight_vision.change_password), name='vendors-keysight-vision-change-password'),
    ]

# ################################################################################################################################
# ################################################################################################################################
# #
# #   Groups
# #
# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # Groups

    url(r'^zato/groups/members/action/(?P<action>.*)/group/(?P<group_id>.*)/id-list/(?P<member_id_list>.*)/$',
        login_required(groups.members_action), name='groups-members-action'),
    url(r'^zato/groups/members/(?P<group_type>.*)/(?P<group_id>.*)/$', # type: ignore
        login_required(groups.manage_group_members), name='groups-members-manage'),
    url(r'^zato/groups/group/(?P<group_type>.*)/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(groups.Delete()), name=groups.Delete.url_name),

    url(r'^zato/groups/get-security-list/$', # type: ignore
        login_required(groups.get_security_list), name='groups-get-security-list'),

    url(r'^zato/groups/get-member-list/$', # type: ignore
        login_required(groups.get_member_list), name='groups-get-member-list'),

    url(r'^zato/groups/group/(?P<group_type>.*)/$',
        login_required(groups.Index()), name=groups.Index.url_name),
    url(r'^zato/groups/create/$',
        login_required(groups.Create()), name=groups.Create.url_name),
    url(r'^zato/groups/edit/$',
        login_required(groups.Edit()), name=groups.Edit.url_name),
    ]

# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # PubSub Topics

    url(r'^zato/pubsub/topic/$',
        login_required(topic.Index()), name=topic.Index.url_name),
    url(r'^zato/pubsub/topic/create/$',
        login_required(topic.Create()), name=topic.Create.url_name),
    url(r'^zato/pubsub/topic/edit/$',
        login_required(topic.Edit()), name=topic.Edit.url_name),
    url(r'^zato/pubsub/topic/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(topic.Delete()), name=topic.Delete.url_name),
    url(r'^zato/pubsub/topic/get-matches/$', login_required(topic.get_matches), name='pubsub-topic-get-matches'),

    # PubSub Client Assignments

    url(r'^zato/pubsub/client/$',
        login_required(client.Index()), name=client.Index.url_name),
    url(r'^zato/pubsub/client/create/$',
        login_required(client.Create()), name=client.Create.url_name),
    url(r'^zato/pubsub/client/edit/$',
        login_required(client.Edit()), name=client.Edit.url_name),
    url(r'^zato/pubsub/client/get-security-definitions/$',
        login_required(client.GetSecurityDefinitions.as_view()), name=client.GetSecurityDefinitions.url_name),
    url(r'^zato/pubsub/client/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(client.Delete()), name=client.Delete.url_name),

    # PubSub Permissions

    url(r'^zato/pubsub/permission/$',
        login_required(permission.Index()), name=permission.Index.url_name),
    url(r'^zato/pubsub/permission/create/$',
        login_required(permission.Create()), name=permission.Create.url_name),
    url(r'^zato/pubsub/permission/edit/$',
        login_required(permission.Edit()), name=permission.Edit.url_name),
    url(r'^zato/pubsub/permission/get-security-definitions/$',
        login_required(permission.GetSecurityDefinitions.as_view()), name=permission.GetSecurityDefinitions.url_name),
    url(r'^zato/pubsub/permission/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(permission.Delete()), name=permission.Delete.url_name),

    # PubSub Subscriptions

    url(r'^zato/pubsub/subscription/$',
        login_required(subscription.Index()), name=subscription.Index.url_name),
    url(r'^zato/pubsub/subscription/create/$',
        login_required(subscription.Create()), name=subscription.Create.url_name),
    url(r'^zato/pubsub/subscription/edit/$',
        login_required(subscription.Edit()), name=subscription.Edit.url_name),
    url(r'^zato/pubsub/subscription/delete/(?P<id>.*)/cluster/(?P<cluster_id>.*)/$',
        login_required(subscription.Delete()), name=subscription.Delete.url_name),
    url(r'^zato/pubsub/subscription/get-security-definitions/$',
        login_required(subscription.get_security_definitions), name='pubsub-subscription-get-security-definitions'),
    url(r'^zato/pubsub/subscription/get-topics/$',
        login_required(subscription.get_topics), name='pubsub-subscription-get-topics'),
    url(r'^zato/pubsub/subscription/get-rest-endpoints/$',
        login_required(subscription.get_rest_endpoints), name='pubsub-subscription-get-rest-endpoints'),
    url(r'^zato/pubsub/subscription/get-service-list/$',
        login_required(subscription.get_service_list), name='pubsub-subscription-get-service-list'),
    url(r'^zato/pubsub/subscription/get-topics-by-security/$',
        login_required(subscription.get_topics_by_security), name='pubsub-subscription-get-topics-by-security'),
    path('zato/pubsub/subscription/sec-def-topic-sub-list/<int:sec_base_id>/cluster/<int:cluster_id>/',
        login_required(subscription.sec_def_topic_sub_list),
        name='pubsub-subscription-sec-def-topic-sub-list'),
]

# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [

    # In-app updates

    url(r'^zato/updates/$',
        login_required(updates.index), name='in-app-updates'),
    url(r'^zato/updates/check-latest-version$',
        login_required(updates.check_latest_version), name='updates-check-latest-version'),
    url(r'^zato/updates/get-latest-audit-entry$',
        login_required(updates.get_latest_audit_entry), name='updates-get-latest-audit-entry'),
    url(r'^zato/updates/get-audit-log-refresh$',
        login_required(updates.get_audit_log_refresh), name='updates-get-audit-log-refresh'),
    url(r'^zato/updates/download-and-install$',
        login_required(updates.download_and_install), name='updates-download-and-install'),
    url(r'^zato/updates/restart-scheduler$',
        login_required(updates.restart_scheduler), name='updates-restart-scheduler'),
    url(r'^zato/updates/restart-server$',
        login_required(updates.restart_server), name='updates-restart-server'),
    url(r'^zato/updates/restart-proxy$',
        login_required(updates.restart_proxy), name='updates-restart-proxy'),
    url(r'^zato/updates/restart-dashboard$',
        login_required(updates.restart_dashboard), name='updates-restart-dashboard'),
    url(r'^zato/updates/save-schedule$',
        login_required(updates.save_schedule), name='updates-save-schedule'),
    url(r'^zato/updates/load-schedule$',
        login_required(updates.load_schedule), name='updates-load-schedule'),
    url(r'^zato/updates/delete-schedule$',
        login_required(updates.delete_schedule), name='updates-delete-schedule'),
    url(r'^zato/updates/download-logs$',
        login_required(updates.download_logs), name='updates-download-logs'),
]

# ################################################################################################################################

urlpatterns += [

    # Log streaming

    url(r'^zato/log-streaming/toggle$',
        login_required(log_streaming.toggle_streaming), name='log-streaming-toggle'),
    url(r'^zato/log-streaming/status$',
        login_required(log_streaming.get_status), name='log-streaming-status'),
    url(r'^zato/log-streaming/stream$',
        login_required(log_streaming.log_stream), name='log-streaming-stream'),
]

# ################################################################################################################################
# ################################################################################################################################

urlpatterns += [
    url(r'^static/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
]

# ################################################################################################################################
# ################################################################################################################################
