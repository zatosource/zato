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

# stdlib
import json, logging
from datetime import datetime
from traceback import format_exc

# OrderedDict is new in 2.7
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

# Django
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.load_balancer import ManageLoadBalancerForm, RemoteCommandForm, \
     ManageLoadBalancerSourceCodeForm
from zato.admin.web.views import get_lb_client, meth_allowed
from zato.common.haproxy import haproxy_stats, Config
from zato.common.odb.model import Cluster

logger = logging.getLogger(__name__)

def _haproxy_alive(client):
    """ Check whether HAProxy is up and running. If 'status' is True then HAProxy
    is alive, sets 'status' to False otherwise and fills in the 'error' attribute
    with the details of an exception caught.
    """
    haproxy_alive = {}
    try:
        is_alive = client.is_haproxy_alive()
    except Exception, e:
        haproxy_alive["status"] = False
        haproxy_alive["error"] = format_exc(e)
    else:
        haproxy_alive["status"] = True

    return haproxy_alive

def _haproxy_stat_config(client=None, lb_config=None):
    """ Return the configuration of the HAProxy HTTP stats interface.
    """
    if not lb_config:
        lb_config = client.get_config()

    # Stats URI is optional
    try:
        stats_uri = lb_config["defaults"]["stats_uri"]
    except KeyError, e:
        return None, None
    else:
        stats_port = lb_config["frontend"]["front_http_plain"]["bind"]["port"]
        return stats_uri, stats_port

def _get_validate_save_flag(cluster_id, req_post):
    """ A convenience function for checking we were told to validate & save
    a config or was it a request for validating it only.
    """
    if "validate_save" in req_post:
        save = True
    elif "validate" in req_post:
        save = False
    else:
        msg = "Expected a flag indicating what to do with input data. cluster_id:[{cluster_id}] req.POST:[{post}]"
        msg = msg.format(cluster_id=cluster_id, post=req_post)
        logger.error(msg)
        raise Exception(msg)

    return save

def _client_validate_save(req, meth, *args):
    """ A convenience function for validating or validating & saving a config
    file on a remote SSL XML-RPC server.
    """
    save = args[1]
    try:
        meth(*args)
    except Exception, e:
        msg = "Caught an exception while invoking the load-balancer agent, e={e}".format(e=format_exc(e))
        logger.error(msg)
        messages.add_message(req, messages.INFO, msg, extra_tags="failure")
    else:
        if save:
            msg = "Config validated and saved successfully"
        else:
            msg = "Config is valid, it's safe to save it"
        messages.add_message(req, messages.INFO, msg, extra_tags="success")

@meth_allowed("GET", "POST")
def remote_command(req, cluster_id):
    """ Execute a HAProxy command.
    """
    cluster = req.zato.odb.query(Cluster).filter_by(id=cluster_id).one()
    client = get_lb_client(cluster)

    haproxy_alive = _haproxy_alive(client)
    cluster.stats_uri, cluster.stats_port = _haproxy_stat_config(client=client)

    # We need to know the HAProxy version before we can build up the select box
    # on the form.
    commands = haproxy_stats[("1", "3")]

    version_info = tuple(client.haproxy_version_info())
    if version_info >= ("1", "4"):
        commands.update(haproxy_stats[("1", "4")])

    if req.method == "POST":
        result = client.execute_command(req.POST["command"], req.POST["timeout"], req.POST.get("extra", ""))
        if not result.strip():
            result = "(empty result)"

        initial={"result":result}
        for k, v in req.POST.items():
            if k != "result":
                initial[k] = v
        form = RemoteCommandForm(commands, initial)
    else:
        form = RemoteCommandForm(commands)

    return_data = {"form":form, "cluster":cluster, "haproxy_alive":haproxy_alive}

    return TemplateResponse(req, 'zato/load_balancer/remote_command.html', return_data)

@meth_allowed("GET")
def manage(req, cluster_id):
    """ GUI for managing HAProxy configuration.
    """
    cluster = req.zato.odb.query(Cluster).filter_by(id=cluster_id).one()
    client = get_lb_client(cluster)

    lb_start_time = datetime.fromtimestamp(client.get_uptime_info())
    lb_config = client.get_config()
    lb_work_config = client.get_work_config()
    lb_work_config['verify_fields'] = ', '.join(['%s=%s' % (k,v) for (k, v) in sorted(lb_work_config['verify_fields'].items())])

    form_data = {
        'global_log_host': lb_config['global_']['log']['host'],
        'global_log_port': lb_config['global_']['log']['port'],
        'global_log_level': lb_config['global_']['log']['level'],
        'global_log_facility': lb_config['global_']['log']['facility'],

        'timeout_connect': lb_config['defaults']['timeout_connect'],
        'timeout_client': lb_config['defaults']['timeout_client'],
        'timeout_server': lb_config['defaults']['timeout_server'],

        'http_plain_bind_address':lb_config['frontend']['front_http_plain']['bind']['address'],
        'http_plain_bind_port':lb_config['frontend']['front_http_plain']['bind']['port'],
        'http_plain_log_http_requests':lb_config['frontend']['front_http_plain']['log_http_requests'],
        'http_plain_maxconn':lb_config['frontend']['front_http_plain']['maxconn'],
        'http_plain_monitor_uri':lb_config['frontend']['front_http_plain']['monitor_uri'],
        }

    backends = {}
    for backend_type in lb_config['backend']:
        for name in lb_config['backend'][backend_type]:
            # Is it a server?
            if 'address' in lb_config['backend'][backend_type][name]:
                if not name in backends:
                    backends[name] = {}
                backends[name][backend_type] = {}
                backends[name][backend_type]['address']  = lb_config['backend'][backend_type][name]['address']
                backends[name][backend_type]['port']  = lb_config['backend'][backend_type][name]['port']
                backends[name][backend_type]['extra']  = lb_config['backend'][backend_type][name]['extra']

    backends = OrderedDict(sorted(backends.items(), key=lambda t: t[0]))
    form = ManageLoadBalancerForm(initial=form_data)
    haproxy_alive = _haproxy_alive(client)
    cluster.stats_uri, cluster.stats_port = _haproxy_stat_config(lb_config=lb_config)
    servers_state = client.get_servers_state()

    return_data = {'cluster':cluster, 'lb_start_time':lb_start_time,
                   'lb_config':lb_config, 'lb_work_config':lb_work_config,
                   'form':form, 'backends':backends, 'haproxy_alive':haproxy_alive,
                   'servers_state':servers_state}

    return TemplateResponse(req, 'zato/load_balancer/manage.html', return_data)

@meth_allowed("POST")
def validate_save(req, cluster_id):
    """ A common handler for both validating and saving a HAProxy config using
    a pretty GUI form.
    """
    save = _get_validate_save_flag(cluster_id, req.POST)

    cluster = req.zato.odb.query(Cluster).filter_by(id=cluster_id).one()
    client = get_lb_client(cluster)

    lb_config = Config()
    lb_config.global_["log"] = {}

    lb_config.frontend["front_http_plain"] = {}
    lb_config.frontend["front_http_plain"]["bind"] = {}

    lb_config.global_["log"]["host"] = req.POST["global_log_host"]
    lb_config.global_["log"]["port"] = req.POST["global_log_port"]
    lb_config.global_["log"]["level"] = req.POST["global_log_level"]
    lb_config.global_["log"]["facility"] = req.POST["global_log_facility"]

    lb_config.defaults["timeout_connect"] = req.POST["timeout_connect"]
    lb_config.defaults["timeout_client"] = req.POST["timeout_client"]
    lb_config.defaults["timeout_server"] = req.POST["timeout_server"]

    lb_config.frontend["front_http_plain"]["bind"]["address"] = req.POST["http_plain_bind_address"]
    lb_config.frontend["front_http_plain"]["bind"]["port"] = req.POST["http_plain_bind_port"]
    lb_config.frontend["front_http_plain"]["log_http_requests"] = req.POST["http_plain_log_http_requests"]
    lb_config.frontend["front_http_plain"]["maxconn"] = req.POST["http_plain_maxconn"]
    lb_config.frontend["front_http_plain"]["monitor_uri"] = req.POST["http_plain_monitor_uri"]

    for key, value in req.POST.items():
        if key.startswith("bck_http"):
            for token in("address", "port", "extra"):
                splitted = key.split(token)
                if splitted[0] == key:
                    continue # We don't have the token in that key.

                backend_type, backend_name = splitted

                # Get rid of underscores left over from the .split above.
                backend_type = backend_type[:-1]
                backend_name = backend_name[1:]

                lb_config.backend.setdefault(backend_type, {})
                lb_config.backend[backend_type].setdefault(backend_name, {})
                lb_config.backend[backend_type][backend_name][token] = value

    # Invoke the LB agent
    _client_validate_save(req, client.validate_save, lb_config, save)

    return redirect("lb-manage", cluster_id=cluster_id)

@meth_allowed("GET")
def manage_source_code(req, cluster_id):
    """ Source code view for managing HAProxy configuration.
    """
    cluster = req.zato.odb.query(Cluster).filter_by(id=cluster_id).one()
    client = get_lb_client(cluster)
    cluster.stats_uri, cluster.stats_port = _haproxy_stat_config(client=client)

    haproxy_alive = _haproxy_alive(client)
    source_code = client.get_config_source_code()
    form = ManageLoadBalancerSourceCodeForm(initial={"source_code":source_code})

    return_data = {"form": form, "haproxy_alive":haproxy_alive, "cluster":cluster}

    return TemplateResponse(req, 'zato/load_balancer/manage_source_code.html', return_data)

@meth_allowed("POST")
def validate_save_source_code(req, cluster_id):
    """ A common handler for both validating and saving a HAProxy config using
    the raw HAProxy config file's view.
    """
    cluster = req.zato.odb.query(Cluster).filter_by(id=cluster_id).one()
    save = _get_validate_save_flag(cluster_id, req.POST)

    # Invoke the LB agent
    client = get_lb_client(cluster)
    _client_validate_save(req, client.validate_save_source_code, req.POST["source_code"], save)

    return redirect("lb-manage-source-code", cluster_id=cluster_id)

@meth_allowed("GET")
def get_addresses(req, cluster_id):
    """ Return JSON-formatted addresses known to HAProxy.
    """
    cluster = req.zato.odb.query(Cluster).filter_by(id=cluster_id).one()
    client = get_lb_client(cluster)

    addresses = {}
    addresses["cluster"] = {"lb_host": cluster.lb_host, "lb_agent_port":cluster.lb_agent_port}

    try:
        lb_config = client.get_config()
    except Exception, e:
        msg = "Could not get load balancer's config, client:[{client!r}], e:[{e}]".format(client=client,
                                                            e=format_exc(e))
        logger.error(msg)
        lb_config = None

    addresses["cluster"]["lb_config"] = lb_config

    return HttpResponse(json.dumps(addresses))
