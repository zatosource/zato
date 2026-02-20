from typing import Any, TYPE_CHECKING

from django.urls import path, re_path as url
from django.contrib.auth.decorators import login_required
from zato.admin import settings
from zato.admin.web.util import static_serve
from zato.admin.web.views import account, datadog, grafana_cloud, http_soap, log_streaming, main, news, openapi_, python_packages, scheduler, service, updates
from zato.admin.web.views.ai import chat as ai_chat
from zato.admin.web.views.ai import highlight as ai_highlight
from zato.admin.web.views.ai import stream as ai_stream
from zato.admin.web.views.ai.mcp import views as ai_mcp
from zato.admin.web.views.ide import complete as ide_complete
from zato.admin.web.views.ide import lint as ide_lint
from zato.admin.web.views.cache import builtin as cache_builtin
from zato.admin.web.views.cache.builtin import entries as cache_builtin_entries
from zato.admin.web.views.cache.builtin import entry as cache_builtin_entry
from zato.admin.web.views.channel import amqp_ as channel_amqp
from zato.admin.web.views.channel import openapi_ as channel_openapi
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

