# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

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
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext

# lxml
from lxml import etree
from lxml.objectify import Element

# Validate
from validate import is_boolean

# anyjson
from anyjson import dumps

# Zato
from zato.admin.settings import delivery_friendly_name
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms import ChangePasswordForm, ChooseClusterForm
from zato.admin.web.forms.outgoing.s3 import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, meth_allowed
from zato.common.odb.model import Cluster, OutgoingS3
from zato.common import zato_namespace, zato_path, ZatoException, ZATO_NOT_GIVEN
from zato.common.util import TRACE1, to_form

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
    zato_message.data.prefix = params[prefix + 'prefix']
    zato_message.data.separator = params[prefix + 'separator']
    zato_message.data.key_sync_timeout = params[prefix + 'key_sync_timeout']

    return zato_message

def _edit_create_response(verb, id, name):

    return_data = {'id': id,
                   'message': 'Successfully {0} the outgoing S3 connection [{1}]'.format(verb, name),
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

        _, zato_message, soap_response  = invoke_admin_service(cluster, 'zato:outgoing.s3.get-list', zato_message)

        if zato_path('data.item_list.item').get_from(zato_message) is not None:

            for msg_item in zato_message.data.item_list.item:

                id = msg_item.id.text
                name = msg_item.name.text
                is_active = is_boolean(msg_item.is_active.text)

                prefix = msg_item.prefix_.text
                separator = msg_item.separator.text
                key_sync_timeout = msg_item.key_sync_timeout.text

                item =  OutgoingS3(id, name, is_active, prefix, separator, key_sync_timeout)
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

    return render_to_response('zato/outgoing/s3.html', return_data,
                              context_instance=RequestContext(req))

@meth_allowed('POST')
def create(req):

    cluster = req.odb.query(Cluster).filter_by(id=req.POST['cluster_id']).first()

    try:
        zato_message = _get_edit_create_message(req.POST)
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:outgoing.s3.create', zato_message)

        return _edit_create_response('created', zato_message.data.out_s3.id.text, req.POST['name'])

    except Exception, e:
        msg = "Could not create an outgoing S3 connection, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)


@meth_allowed('POST')
def edit(req):

    cluster = req.odb.query(Cluster).filter_by(id=req.POST['cluster_id']).first()

    try:
        zato_message = _get_edit_create_message(req.POST, 'edit-')
        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:outgoing.s3.edit', zato_message)

        return _edit_create_response('updated', req.POST['id'], req.POST['edit-name'])

    except Exception, e:
        msg = "Could not update the outgoing S3 connection, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

@meth_allowed('POST')
def delete(req, id, cluster_id):

    cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()

    try:
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.id = id

        _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:outgoing.s3.delete', zato_message)

        return HttpResponse()

    except Exception, e:
        msg = "Could not delete the outgoing S3 connection, e=[{e}]".format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

@meth_allowed('POST')
def change_secret_key(req):
    return _change_password(req, 'zato:outgoing.s3.change-secret-key', success_msg='Secret key updated')