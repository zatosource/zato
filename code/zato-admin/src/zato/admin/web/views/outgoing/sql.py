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

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext

# lxml
from lxml.objectify import Element

# Validate
from validate import is_boolean

# anyjson
from anyjson import dumps

# Zato
from zato.admin.settings import odb_engine_friendly_name
from zato.admin.web import invoke_admin_service
from zato.admin.web.views import change_password as _change_password
from zato.admin.web.forms import ChangePasswordForm, ChooseClusterForm
from zato.admin.web.forms.outgoing.sql import CreateForm, EditForm
from zato.admin.web.views import meth_allowed
from zato.common.odb.model import Cluster, SQLConnectionPool
from zato.common import zato_namespace, zato_path
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

def _get_edit_create_message(params, prefix=''):
    """ Creates a base document which can be used by both 'edit' and 'create' actions.
    """
    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.data = Element('data')
    zato_message.data.id = params.get('id')
    zato_message.data.cluster_id = params['cluster_id']
    zato_message.data.name = params[prefix + 'name']
    zato_message.data.is_active = bool(params.get(prefix + 'is_active'))
    zato_message.data.engine = params[prefix + 'engine']
    zato_message.data.host = params[prefix + 'host']
    zato_message.data.port = params[prefix + 'port']
    zato_message.data.db_name = params[prefix + 'db_name']
    zato_message.data.username = params[prefix + 'username']
    zato_message.data.pool_size = params[prefix + 'pool_size']
    zato_message.data.extra = params.get(prefix + 'extra')

    return zato_message

def _edit_create_response(verb, id, name, engine):

    return_data = {'id': id,
                   'message': 'Successfully {0} the outgoing SQL connection [{1}]'.format(verb, name),
                   'engine_text': odb_engine_friendly_name[engine],
                }

    return HttpResponse(dumps(return_data), mimetype='application/javascript')

@meth_allowed('GET')
def index(req):
    zato_clusters = req.odb.query(Cluster).order_by('name').all()
    choose_cluster_form = ChooseClusterForm(zato_clusters, req.GET)
    cluster_id = req.GET.get('cluster')
    items = []

    create_form = CreateForm()
    edit_form = EditForm(prefix='edit')
    change_password_form = ChangePasswordForm()

    if cluster_id and req.method == 'GET':

        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.cluster_id = cluster_id

        _, zato_message, soap_response  = invoke_admin_service(cluster, 'zato:outgoing.sql.get-list', zato_message)

        if zato_path('data.item_list.item').get_from(zato_message) is not None:

            for msg_item in zato_message.data.item_list.item:

                id = msg_item.id.text
                name = msg_item.name.text
                is_active = is_boolean(msg_item.is_active.text)
                engine = msg_item.engine.text if msg_item.engine else ''
                host = msg_item.host.text if msg_item.host else ''
                port = msg_item.port.text if msg_item.port else ''
                db_name = msg_item.db_name.text if msg_item.db_name else ''
                username = msg_item.username.text if msg_item.username else ''
                pool_size = msg_item.pool_size.text if msg_item.pool_size else ''
                extra = msg_item.extra.text if msg_item.extra else ''
                
                item =  SQLConnectionPool()
                item.id = id
                item.name = name
                item.is_active = is_active
                item.engine = engine
                item.engine_text = odb_engine_friendly_name[engine]
                item.host = host
                item.port = port
                item.db_name = db_name
                item.username = username
                item.pool_size = pool_size
                item.extra = extra
                items.append(item)

    return_data = {'zato_clusters':zato_clusters,
        'cluster_id':cluster_id,
        'choose_cluster_form':choose_cluster_form,
        'items':items,
        'create_form':create_form,
        'edit_form':edit_form,
        'change_password_form': change_password_form
        }

    # TODO: Should really be done by a decorator.
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [{0}]'.format(return_data))

    return render_to_response('zato/outgoing/sql.html', return_data,
                              context_instance=RequestContext(req))

@meth_allowed('POST')
def create(req):

    cluster = req.odb.query(Cluster).filter_by(id=req.POST['cluster_id']).first()

    try:
        zato_message = _get_edit_create_message(req.POST)
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:outgoing.sql.create', zato_message)

        return _edit_create_response('created', zato_message.data.out_sql.id.text, req.POST['name'])

    except Exception, e:
        msg = "Could not create an outgoing SQL connection, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)


def edit():
    pass

def delete():
    pass

def ping():
    pass

def change_password():
    pass

'''
from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import copy
import logging
from uuid import uuid4
from traceback import format_exc

# Django
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseServerError
from django.template import RequestContext

# lxml
from lxml import etree
from lxml import objectify
from lxml.objectify import Element

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.views import meth_allowed
from zato.admin.settings import engine_friendly_name
from zato.admin.web.forms import ChooseClusterForm
from zato.admin.web.forms.pool.sql import SQLConnectionPoolForm
from zato.common import zato_namespace, path, zato_path, ZatoException
from zato.common.soap import invoke_admin_service
from zato.common.odb.model import Server
from zato.common.util import encrypt, pprint, TRACE1

logger = logging.getLogger("zatoadmin.web.views.sql")

def _get_edit_create_message(params, form_prefix=""):
    """ Creates a base document which can be used by both 'edit' and 'create' actions.
    """
    zato_message = Element("{%s}zato_message" % zato_namespace)
    zato_message.pool = Element("pool")
    zato_message.pool.pool_name = params[form_prefix + "pool_name"]
    zato_message.pool.engine = params[form_prefix + "engine"]
    zato_message.pool.user = params[form_prefix + "user"]
    zato_message.pool.host = params[form_prefix + "host"]
    zato_message.pool.db_name = params[form_prefix + "db_name"]
    zato_message.pool.pool_size = params[form_prefix + "pool_size"]

    # Extra parameters are, well, extra.
    extra = params.get(form_prefix + "extra", "")
    if extra:
        zato_message.pool.extra_list = Element("extra_list")
        extra = (elem for elem in extra.split("\n") if elem)
        for value in extra:
            extra_elem = etree.Element("{%s}extra" % zato_namespace)
            extra_elem.text = value
            zato_message.pool.extra_list.append(extra_elem)

    return zato_message

def _ping_delete(req, soap_action):
    """ Code common to both deleting and pinging connection pools.
    """
    server_id = req.GET.get("server")
    pool_name = req.GET.get("pool_name")

    if not server_id:
        raise ZatoException("No 'server' parameter found, req.GET=[%s]" % req.GET)

    if not pool_name:
        raise ZatoException("No 'pool_name' parameter found, req.GET=[%s]" % req.GET)

    server = Server.objects.get(id=server_id)
    zato_message = Element("{%s}zato_message" % zato_namespace)
    zato_message.pool_name = pool_name

    return invoke_admin_service(server.address, soap_action, etree.tostring(zato_message))

def _edit(server_address, params):
    """ Updates SQL connection pool's parameters (everything except for the password).
    """
    logger.info("About to change an SQL connection pool, server_address=[%s], params=[%s]" % (server_address, params))
    zato_message = _get_edit_create_message(params, "edit-")

    # original_pool_name is needed only by 'edit'.
    zato_message.pool.original_pool_name = params.get("edit-original_pool_name")
    invoke_admin_service(server_address, "zato:pool.sql.edit", etree.tostring(zato_message))

    logger.info("Saved changes to SQL connection pool, server_address=[%s], params=[%s]" % (server_address, params))

def _create(server_address, params):
    """ Creates a new SQL connection pool.
    """
    logger.info("About to create an SQL connection pool, server_address=[%s], params=[%s]" % (server_address, params))

    zato_message = _get_edit_create_message(params)
    invoke_admin_service(server_address, "zato:pool.sql.create", etree.tostring(zato_message))

    logger.info("Created SQL connection pool, server_address=[%s], params=[%s]" % (server_address, params))

def _change_password(server_address, params):
    """ Changes the SQL connection pool's password.
    """
    params_no_passwords = copy.deepcopy(params)
    params_no_passwords["password1"] = "***"
    params_no_passwords["password2"] = "***"

    logger.info("About to change an SQL connection pool password, server_address=[%s], params=[%s]" % (server_address, params_no_passwords))

    config_pub_key = str(params["config_pub_key"])
    encrypted_password1 = encrypt(params["password1"], config_pub_key)
    encrypted_password2 = encrypt(params["password2"], config_pub_key)

    zato_message = Element("{%s}zato_message" % zato_namespace)
    zato_message.pool_name = params["pool_name"]
    zato_message.password1 = encrypted_password1
    zato_message.password2 = encrypted_password2

    invoke_admin_service(server_address, "zato:pool.sql.change-password", etree.tostring(zato_message))

@meth_allowed("GET", "POST")
def index(req):
    """ Lists SQL connection pools and dispatches the management requests
    (create, edit and change_password).
    """

    zato_servers = Server.objects.all().order_by("name")
    pools = []
    config_pub_key = ""
    server_id = None

    choose_server_form = ChooseClusterForm(zato_servers, req.GET)
    edit_form = SQLConnectionPoolForm(prefix="edit")

    # Build a list of SQL connection pools for a given Zato server.
    server_id = req.GET.get("server")
    if server_id and req.method == "GET":

        # We have a server to pick the connection pools from, try to
        # invoke it now.
        server = Server.objects.get(id=server_id)
        _ignored, zato_message, soap_response = invoke_admin_service(server.address, "zato:pool.sql.get-list")

        # Config pub key is always needed.
        config_pub_key = zato_path("envelope.config_pub_key", True).get_from(zato_message)

        if zato_path("data.pool_list.pool").get_from(zato_message) is not None:

            for pool in zato_message.data.pool_list.pool:
                    original_pool_name = unicode(pool.pool_name)
                    pool_name = unicode(pool.pool_name)
                    engine = unicode(pool.engine)
                    engine_friendly = engine_friendly_name[str(engine)]
                    user = unicode(pool.user)
                    host = unicode(pool.host)
                    db_name = unicode(pool.db_name)
                    pool_size = pool.pool_size

                    if path("pool.extra.item").get_from(pool) is not None:
                        logger.log(TRACE1, "Found 'extra.item' in the response, pool_name=[%s]" % pool_name)
                        extra = []
                        for extra_elem in pool.extra.item:
                            extra.append(unicode(extra_elem))
                        extra = "\n".join(extra)
                    else:
                        logger.log(TRACE1, "No 'extra.item' found in the response, pool_name=[%s]" % pool_name)
                        extra = ""

                    pool = SQLConnectionPool(uuid4().hex, original_pool_name,
                                             pool_name, engine, engine_friendly, user,
                                             host, db_name, pool_size, extra)
                    pools.append(pool)
        else:
            logger.info("No pools found, soap_response=[%s]" % soap_response)

    if req.method == "POST":

        action = req.POST.get("zato_action")
        if not action:
            msg = "Missing 'zato_action' parameter in req.POST"
            logger.error(msg)
            return HttpResponseServerError(msg)

        if not server_id:
            msg = "Parameter 'server' is missing in GET data."

            if action != "change_password":
                msg += " Action [%s], req.POST=[%s], req.GET=[%s]" % (action, pprint(req.POST), pprint(req.GET))

            logger.error(msg)
            return HttpResponseServerError(msg)

        server = Server.objects.get(id=server_id)

        handler = globals().get("_" + action)
        if not handler:
            msg = "No handler found for action [%s]." % action

            if action != "change_password":
                msg += " req.POST=[%s], req.GET=[%s]" % (pprint(req.POST), pprint(req.GET))

            logger.error(msg)
            return HttpResponseServerError(msg)

        # Finally, invoke the action handler.
        try:
            response = handler(server.address, req.POST)
            response = response if response else ""
            return HttpResponse(response)
        except Exception, e:
            msg = "Could not invoke action [%s], e=[%s]. " % (action, format_exc())

            if action != "change_password":
                msg += " req.POST=[%s], req.GET=[%s]" % (pprint(req.POST), pprint(req.GET))

            logger.error(msg)
            return HttpResponseServerError(msg)

    logger.log(TRACE1, "Returning render_to_response.")

    return render_to_response("zato/pool/sql.html", {
            "choose_server_form":choose_server_form,
            "zato_servers":zato_servers,
            "pools":pools,
            "config_pub_key":config_pub_key,
            "server_id": server_id,
            "edit_form": edit_form,
            "create_form":SQLConnectionPoolForm(),
            "engine_friendly_name": engine_friendly_name.items(),
            "change_password_form":ChangePasswordForm()
        }, context_instance=RequestContext(req))

@meth_allowed("POST")
def ping(req):
    """ Pings a database and returns the time it took, in milliseconds.
    """
    try:
        result, zato_message_response, soap_response = _ping_delete(req, "zato:pool.sql.ping")
        response_time = zato_path("data.response_time").get_from(zato_message_response)
    except Exception, e:
        msg = "Ping failed. server_id=[%s], pool_name=[%s], e=[%s]" % (req.GET.get("server"), req.GET.get("pool_name"), format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        return render_to_response("zato/pool/sql-ping-ok.html", 
                                  {"response_time":"%.3f" % response_time},
                                  context_instance=RequestContext(req))

@meth_allowed("POST")
def delete(req):
    """ Deletes an SQL connection pool.
    """
    try:
        _ping_delete(req, "zato:pool.sql.delete")
    except Exception, e:
        msg = "Could not delete the SQL connection pool. server_id=[%s], pool_name=[%s], e=[%s]" % (req.GET.get("server"), req.GET.get("pool_name"), format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        # 200 OK
        return HttpResponse()
'''