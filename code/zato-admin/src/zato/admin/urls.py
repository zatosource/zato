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
from zato.admin.web.views import main, cluster, service, servers, scheduler, channel, \
     load_balancer
from zato.admin.web.views.pool import sql
from zato.admin.web.views.security import basic_auth, tech_account, wss


urlpatterns = patterns("",

    # Auth
    (r"^accounts/login/$", login, {"template_name": "zato/login.html"}),


    # Redirect to the main page.
    (r"^$", main.index_redirect),

    # Main page.
    url(r"^zato/$", main.index, name="main-page"),

    # Clusters.
    url(r"^zato/cluster/$", cluster.index, name="cluster"),
    url(r"^zato/cluster/create/$", cluster.create, name="cluster-create"),
    url(r"^zato/cluster/edit/$", cluster.edit, name="cluster-edit"),
    url(r"^zato/cluster/delete/$", cluster.delete, name="cluster-delete"),
    url(r"^zato/cluster/servers-state/(?P<cluster_id>.*)$", cluster.get_servers_state, name="cluster-servers-state"),
    url(r"^zato/cluster/get/by-id/(?P<cluster_id>.*)$", cluster.get_by_id, name="cluster-get-by-id"),
    url(r"^zato/cluster/get/by-name/(?P<cluster_name>.*)/$", cluster.get_by_name, name="cluster-get-by-name"),

    # Load balancer
    url(r"^zato/load-balancer/get-addresses/cluster/(?P<cluster_id>.*)$", load_balancer.get_addresses, name="lb-get-addresses"),
    url(r"^zato/load-balancer/manage/cluster/(?P<cluster_id>\d+)/validate-save/$", load_balancer.validate_save, name="lb-manage-validate-save"),
    url(r"^zato/load-balancer/manage/cluster/(?P<cluster_id>.*)$", load_balancer.manage, name="lb-manage"),
    url(r"^zato/load-balancer/manage/source-code/cluster/(?P<cluster_id>.*)/validate-save$", load_balancer.validate_save_source_code, name="lb-manage-source-code-validate-save"),
    url(r"^zato/load-balancer/manage/source-code/cluster/(?P<cluster_id>.*)$", load_balancer.manage_source_code, name="lb-manage-source-code"),
    url(r"^zato/load-balancer/remote-command/(?P<cluster_id>.*)$", load_balancer.remote_command, name="lb-remote-command"),

    # TODO: "servers" should be "server"

    # Servers registry.
    url(r"^zato/servers/$", servers.index, name="servers"),
    url(r"^zato/servers/status/(?P<server_id>.*)$", servers.status, name="server-status"),
    url(r"^zato/servers/ping/(?P<server_id>.*)$", servers.ping, name="server-ping"),
    url(r"^zato/servers/unregister/(?P<server_id>.*)$", servers.unregister, name="server-unregister"),

    # Services.
    url(r"^zato/service/$", service.index, name="service"),
    url(r"^zato/service/details/(?P<server_id>\d*)/(?P<service_name>.*)/invoke/$", service.invoke, name="service-invoke"),
    url(r"^zato/service/details/(?P<server_id>\d*)/(?P<service_name>.*)/$", service.details, name="service-details"),

    # Channels.
    url(r"^zato/channels/soap/$", channel.soap, name="channel-soap"),

    # Security.

    url(r"^zato/security/basic-auth/$", basic_auth.index, name="security-basic-auth"),
    url(r"^zato/security/basic-auth/create/$", basic_auth.create, name="security-basic-auth-create"),
    url(r"^zato/security/basic-auth/edit/$", basic_auth.edit, name="security-basic-auth-edit"),
    url(r"^zato/security/basic-auth/change-password/$", basic_auth.change_password, name="security-basic-auth-change-password"),
    
    url(r"^zato/security/tech-account/$", tech_account.index, name="security-tech-account"),
    url(r"^zato/security/tech-account/create/$", tech_account.create, name="security-tech-account-create"),
    url(r"^zato/security/tech-account/edit/$", tech_account.edit, name="security-tech-account-edit"),
    url(r"^zato/security/tech-account/change-password/$", tech_account.change_password, name="security-tech-account-change-password"),
    url(r"^zato/security/tech-account/get/by-id/(?P<tech_account_id>.*)/cluster/(?P<cluster_id>.*)/$", tech_account.get_by_id, name="security-tech-account-get-by-id"),
    url(r"^zato/security/tech-account/delete/(?P<tech_account_id>.*)/cluster/(?P<cluster_id>.*)/$", tech_account.delete, name="security-tech-account-delete"),
    
    url(r"^zato/security/wss/$", wss.index, name="security-wss"),
    url(r"^zato/security/wss/create/$", wss.create, name="security-wss-create"),
    url(r"^zato/security/wss/edit/$", wss.edit, name="security-wss-edit"),
    url(r"^zato/security/wss/change-password/$", wss.change_password, name="security-wss-change-password"),
    url(r"^zato/security/wss/delete/(?P<wss_id>.*)/cluster/(?P<cluster_id>.*)/$", wss.delete, name="security-wss-delete"),

    # SQL connection pools.
    url(r"^zato/pool/sql/$", sql.index, name="pool-sql"),
    url(r"^zato/pool/sql/ping/$", sql.ping, name="pool-sql-ping"),
    url(r"^zato/pool/sql/delete/$", sql.delete, name="pool-sql-delete"),

    # Scheduler
    url(r"^zato/scheduler/$", scheduler.index, name="scheduler"),
    url(r"^zato/scheduler/delete/$", scheduler.delete, name="scheduler-job-delete"),
    url(r"^zato/scheduler/get-definition/(?P<start_date>.*)/(?P<repeat>.*)/"
        "(?P<weeks>.*)/(?P<days>.*)/(?P<hours>.*)/(?P<minutes>.*)/(?P<seconds>.*)/$",
        scheduler.get_definition, name="scheduler-job-get-definition"),
)

if settings.DEBUG:
    urlpatterns += patterns("",
        (r"^static/(?P<path>.*)$", "django.views.static.serve", {"document_root": settings.MEDIA_ROOT}),
    )

