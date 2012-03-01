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
import logging
from traceback import format_exc

# Django
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext

# Zato
from zato.admin.web.forms.servers import RegisterServerForm, EditServerForm
from zato.admin.web.views import meth_allowed
from zato.common.odb.model import Server
from zato.common.soap import SOAPPool

logger = logging.getLogger(__name__)

def _ping(address):
    pool = SOAPPool(address)
    pool.invoke("/soap", "zato:Ping", "")

@meth_allowed('GET')
def ping(req, server_id):

    server = req.odb.query(Server).filter_by(id=server_id).first()

    try:
        _ping(server.address)
        template = "zato/servers/ping_server_ok.html"
        e = None
    except Exception, e:
        template = "zato/servers/ping_server_error.html"

    if e:
        logger.error("Could not ping server, ID [%s], address [%s], exception [%s]" % (server_id, server.address, format_exc()))

    return render_to_response(template, {"error": e})

@meth_allowed("POST")
def ping_by_address(req, address):
    if _ping(address):
        template = "zato/servers/ping_server_ok.html"
    else:
        template = "zato/servers/ping_server_error.html"

    return render_to_response(template)

@meth_allowed("GET")
def index(req):

    zato_servers = req.odb.query(Server).order_by("name").all()
    is_edit = req.POST.get("is_edit", False)
    success_message = req.GET.get("success_message", None)
    error_message = req.GET.get("error_message", None)

    if req.method == "POST":

        if is_edit:
            prefix = "edit-"
            edit_form = EditServerForm(req.POST, prefix="edit")
            form = RegisterServerForm()
            current_form = edit_form
            zato_server = Server(req.POST[prefix + "server_id"])
            success_message = "Successfully saved the changes"
        else:
            prefix = ""
            form = RegisterServerForm(req.POST)
            edit_form = EditServerForm(prefix="edit")
            current_form = form
            zato_server = Server()
            success_message = "Successfully registered the server"

        if current_form.is_valid():

            name = req.POST[prefix + "name"].strip()
            address = req.POST[prefix + "address"].strip()

            zato_server.name = name
            zato_server.address = address
            zato_server.save()

            # Return to the list of registered servers.
            return HttpResponseRedirect(reverse(index) + "?success_message=%s" % success_message)

        else:
            success_message = None
            error_message = current_form.errors
            print(edit_form.errors, 2222)


    else:
        form = RegisterServerForm()
        edit_form = EditServerForm(prefix="edit")

    return render_to_response("zato/servers/index.html", {
        "form": form,
        "edit_form": edit_form,
        "zato_servers":zato_servers,
        "success_message":success_message,
        "error_message":error_message
    }, context_instance=RequestContext(req))

@meth_allowed("POST")
def status(req, server_id):
    pass

@meth_allowed("POST")
def unregister(req, server_id):
    server = Server.objects.get(id=server_id)
    server.delete()

    # Return to the list of registered servers.
    return HttpResponseRedirect(reverse(index))
