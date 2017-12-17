# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime, timedelta
from itertools import chain
from traceback import format_exc

# anyjson
from json import dumps

# bunch
from bunch import Bunch

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# pytz
from pytz import UTC

# Zato
from zato.admin.settings import ssl_key_file, ssl_cert_file, ssl_ca_certs, LB_AGENT_CONNECT_TIMEOUT
from zato.admin.web import from_utc_to_user
from zato.common import SEC_DEF_TYPE_NAME, ZatoException, ZATO_NONE, ZATO_SEC_USE_RBAC
from zato.common.util import get_lb_client as _get_lb_client

# ################################################################################################################################

try:
    from django.core.urlresolvers import reverse as django_url_reverse # Django < 1.10
    from django.utils.text import slugify
except ImportError:
    from django.urls import reverse as django_url_reverse              # Django >= 1.10
    from django.utils import slugify

# For pyflakes
django_url_reverse = django_url_reverse
slugify = slugify

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

def parse_response_data(response):
    """ Parses out data and metadata out an internal API call response.
    """
    meta = response.data.pop('_meta', None)
    data = response.data[response.data.keys()[0]]
    return data, meta

# ################################################################################################################################

def _get_list(client, cluster, service):

    out = {}
    for item in client.invoke(service, {'cluster_id':cluster.id}):
        out[item.id] = item.name

    return out

# ################################################################################################################################

def get_definition_list(client, cluster, def_type):
    """ Returns all definitions of a given type existing on a given cluster.
    """
    return _get_list(client, cluster, 'zato.definition.{}.get-list'.format(def_type))

# ################################################################################################################################

def get_tls_ca_cert_list(client, cluster):
    """ Returns all TLS CA certs on a given cluster.
    """
    return _get_list(client, cluster, 'zato.security.tls.ca-cert.get-list')

# ################################################################################################################################

def get_sample_dt(user_profile):
    """ A sample date and time an hour in the future serving as a hint as to what
    format to use when entering date and time manually in the user-provided format.
    """
    return from_utc_to_user((datetime.utcnow() + timedelta(hours=1)).replace(tzinfo=UTC), user_profile)

# ################################################################################################################################

def get_js_dt_format(user_profile):
    """ Converts the user-given datetime format to the one that JavaScript's date time picker is to use.
    """
    return {
        'js_date_format':user_profile.date_format.replace('yyyy', 'yy') if 'yyyy' in user_profile.date_format else user_profile.date_format.replace('yy', 'y'),
        'js_time_format':'h:mm.ss TT' if user_profile.time_format == '12' else 'hh:mm:ss',
        'js_ampm':user_profile.time_format == '12',
    }

# ################################################################################################################################

def get_lb_client(cluster):
    """ A convenience wrapper over the function for creating a load-balancer client
    which may use web admin's SSL material (the client from zato.common can't use
    it because it would make it dependent on the zato.admin package).
    """
    return _get_lb_client(cluster.lb_host, cluster.lb_agent_port, ssl_ca_certs,
                          ssl_key_file, ssl_cert_file, LB_AGENT_CONNECT_TIMEOUT)

# ################################################################################################################################

def method_allowed(*methods_allowed):
    """ Accepts a list (possibly one-element long) of HTTP methods allowed
    for a given view. An exception will be raised if a request has been made
    with a method outside of those allowed, otherwise the view executes
    unchanged.
    TODO: Make it return a custom Exception so that whoever called us can
    catch it and return a correct HTTP status (405 Method not allowed).
    """
    def inner_method_allowed(view):
        def inner_view(*args, **kwargs):
            req = args[1] if len(args) > 1 else args[0]
            if req.method not in methods_allowed:
                msg = 'Method `{}` is not allowed here `{}`, methods allowed:`{}`'.format(
                    req.method, view.func_name, methods_allowed)
                logger.error(msg)
                raise Exception(msg)
            return view(*args, **kwargs)
        return inner_view
    return inner_method_allowed

# ################################################################################################################################

def set_servers_state(cluster, client):
    """ Assignes 3 flags to the cluster indicating whether load-balancer
    believes the servers are UP, DOWN or in the MAINT mode.
    """
    servers_state = client.get_servers_state()

    up = []
    down = []
    maint = []

    cluster.some_down = False
    cluster.some_maint = False
    cluster.all_down = False

    # Note: currently we support only the 'http_plain' access_type.
    for access_type in('http_plain',):
        up.extend(servers_state['UP'][access_type])
        down.extend(servers_state['DOWN'][access_type])
        maint.extend(servers_state['MAINT'][access_type])

    # Do we have any servers at all?
    if any((up, down, maint)):
        if not(up or maint) and down:
            cluster.all_down = True
        else:
            if down:
                cluster.some_down = True
            if maint:
                cluster.some_maint = True

# ################################################################################################################################

def change_password(req, service_name, field1='password1', field2='password2', success_msg='Password updated'):
    try:
        input_dict = {
            'id': req.POST.get('id'),
            'password1': req.POST.get(field1, ''),
            'password2': req.POST.get(field2, ''),
        }
        req.zato.client.invoke(service_name, input_dict)

    except Exception, e:
        msg = 'Could not change the password, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        return HttpResponse(dumps({'message':success_msg}))

# ################################################################################################################################

def get_security_id_from_select(params, prefix, field_name='security'):
    security = params[prefix + field_name]

    if security == ZATO_NONE:
        security_id = ZATO_NONE

    elif security == ZATO_SEC_USE_RBAC:
        security_id = ZATO_SEC_USE_RBAC

    else:
        _, security_id = security.split('/')

    return security_id

# ################################################################################################################################

class _BaseView(object):
    method_allowed = 'method_allowed-must-be-defined-in-a-subclass'
    service_name = None
    async_invoke = False
    form_prefix = ''

    def on_before_append_item(self, item):
        return item

    def on_after_set_input(self):
        pass

    def clear_user_message(self):
        self.user_message = None
        self.user_message_class = 'failure'

    class SimpleIO:
        input_required = []
        input_optional = []
        output_required = []
        output_optional = []
        output_repeated = False

    def fetch_cluster_id(self):
        # Doesn't look overtly smart right now but more code will follow to sanction
        # the existence of this function
        cluster_id = self.req.zato.cluster_id

        if cluster_id:
            self.cluster_id = cluster_id

    def __init__(self):
        self.req = None
        self.cluster_id = None

    def __call__(self, req, *args, **kwargs):
        self.req = req
        for k, v in kwargs.items():
            self.req.zato.args[k] = v
        self.cluster_id = None
        self.fetch_cluster_id()

    def get_sec_def_list(self, sec_type):
        return SecurityList.from_service(self.req.zato.client, self.req.zato.cluster.id, sec_type)

    def set_input(self, req=None, default_attrs=('cur_page', 'query')):
        req = req or self.req
        self.input.update({
            'cluster_id':self.cluster_id,
            'paginate': getattr(self, 'paginate', False),
        })
        for name in chain(self.SimpleIO.input_required, self.SimpleIO.input_optional, default_attrs):
            if name != 'cluster_id':
                value = \
                    req.GET.get(name) or \
                    req.GET.get(self.form_prefix + name) or \
                    req.POST.get(self.form_prefix + name) or \
                    req.zato.args.get(self.form_prefix + name)
                self.input[name] = value

        self.on_after_set_input()

# ################################################################################################################################

class Index(_BaseView):
    """ A base class upon which other index views are based.
    """
    url_name = 'url_name-must-be-defined-in-a-subclass'
    template = 'template-must-be-defined-in-a-subclass'

    output_class = None

    def __init__(self):
        super(Index, self).__init__()
        self.input = Bunch()
        self.items = []
        self.item = None
        self.clear_user_message()

    def can_invoke_admin_service(self):
        """ Returns a boolean flag indicating that we know what service to invoke,
        what cluster on and all the required parameters were given in GET request.
        cluster_id doesn't have to be in GET, 'cluster' will suffice.
        """
        input_elems = self.req.GET.keys() + self.req.zato.args.keys()

        if not(self.service_name and self.cluster_id):
            return False

        for elem in self.SimpleIO.input_required:
            if elem == 'cluster_id':
                continue
            if not elem in input_elems:
                return False
            value = self.req.GET.get(elem)
            if not value:
                value = self.req.zato.args.get(elem)
                if not value:
                    return False
        return True

    def before_invoke_admin_service(self):
        pass

    def invoke_admin_service(self):
        if self.req.zato.get('cluster'):
            func = self.req.zato.client.invoke_async if self.async_invoke else self.req.zato.client.invoke
            return func(self.service_name, self.input)

    def _handle_item_list(self, item_list):
        """ Creates a new instance of the model class for each of the element received
        and fills it in with received attributes.
        """
        names = tuple(chain(self.SimpleIO.output_required, self.SimpleIO.output_optional))
        for msg_item in item_list:
            item = self.output_class()
            for name in names:
                value = getattr(msg_item, name, None)
                if value is not None:
                    value = getattr(value, 'text', '') or value
                if value or value == 0:
                    setattr(item, name, value)
            self.items.append(self.on_before_append_item(item))

    def _handle_item(self, item):
        pass

    def handle_return_data(self, return_data):
        return return_data

    def __call__(self, req, *args, **kwargs):
        """ Handles the request, taking care of common things and delegating
        control to the subclass for fetching this view-specific data.
        """
        self.clear_user_message()

        try:
            super(Index, self).__call__(req, *args, **kwargs)
            del self.items[:]
            self.item = None
            self.set_input()

            return_data = {'cluster_id':self.cluster_id}
            output_repeated = getattr(self.SimpleIO, 'output_repeated', False)

            response = None

            if self.can_invoke_admin_service():
                self.before_invoke_admin_service()
                response = self.invoke_admin_service()
                if response.ok:
                    return_data['response_inner'] = response.inner_service_response
                    if output_repeated:
                        if isinstance(response.data, dict):
                            response.data.pop('_meta', None)
                            data = response.data[response.data.keys()[0]]
                        else:
                            data = response.data
                        self._handle_item_list(data)
                    else:
                        self._handle_item(response.data)
                else:
                    self.user_message = response.details
            else:
                logger.info('can_invoke_admin_service returned False, not invoking an admin service:[%s]', self.service_name)


            return_data['req'] = self.req
            return_data['items'] = self.items
            return_data['item'] = self.item
            return_data['input'] = self.input
            return_data['user_message'] = self.user_message
            return_data['user_message_class'] = self.user_message_class
            return_data['zato_clusters'] = req.zato.clusters
            return_data['search_form'] = req.zato.search_form
            return_data['meta'] = response.meta if response else {}
            return_data['paginate'] = getattr(self, 'paginate', False)

            view_specific = self.handle()
            if view_specific:
                return_data.update(view_specific)

            return_data = self.handle_return_data(return_data)

            return TemplateResponse(req, self.template, return_data)

        except Exception, e:
            return HttpResponseServerError(format_exc(e))

    def handle(self, req=None, *args, **kwargs):
        raise NotImplementedError('Must be overloaded by a subclass')

# ################################################################################################################################

class CreateEdit(_BaseView):
    """ Subclasses of this class will handle the creation/updates of Zato objects.
    """

    def __init__(self):
        super(CreateEdit, self).__init__()
        self.input = Bunch()
        self.input_dict = {}

    def __call__(self, req, initial_input_dict={}, initial_return_data={}, *args, **kwargs):
        """ Handles the request, taking care of common things and delegating
        control to the subclass for fetching this view-specific data.
        """
        self.input_dict.clear()
        self.clear_user_message()

        try:
            super(CreateEdit, self).__call__(req, *args, **kwargs)
            self.set_input()

            input_dict = {'cluster_id': self.cluster_id}
            post_id = self.req.POST.get('id')

            if post_id:
                input_dict['id'] = post_id

            input_dict.update(initial_input_dict)

            for name in chain(self.SimpleIO.input_required, self.SimpleIO.input_optional):
                if name not in input_dict and name not in self.input_dict:
                    input_dict[name] = self.input.get(name)

            self.input_dict.update(input_dict)

            logger.debug(
                'Request input dict `%r` out of `%r`, `%r`, `%r`, `%r`, `%r`', self.input_dict,
                self.SimpleIO.input_required, self.SimpleIO.input_optional, self.input, self.req.GET, self.req.POST)

            response = self.req.zato.client.invoke(self.service_name, self.input_dict)
            if response.ok:
                return_data = {
                    'message': self.success_message(response.data)
                    }

                return_data.update(initial_return_data)

                for name in chain(self.SimpleIO.output_optional, self.SimpleIO.output_required):
                    if name not in initial_return_data:
                        value = getattr(response.data, name, None)
                        if value:
                            if isinstance(value, basestring):
                                value = value.encode('utf-8')
                            else:
                                value = str(value)
                        return_data[name] = value

                self.post_process_return_data(return_data)

                return HttpResponse(dumps(return_data), content_type='application/javascript')
            else:
                msg = 'response:[{}], details.response.details:[{}]'.format(response, response.details)
                logger.error(msg)
                raise ZatoException(msg=msg)

        except Exception, e:
            return HttpResponseServerError(format_exc(e))

    def success_message(self, item):
        raise NotImplementedError('Must be implemented by a subclass')

    def post_process_return_data(self, return_data):
        return return_data

    @property
    def verb(self):
        if self.form_prefix:
            return 'updated'
        return 'created'

# ################################################################################################################################

class BaseCallView(_BaseView):

    method_allowed = 'POST'
    error_message = 'error_message-must-be-defined-in-a-subclass'

    def get_input_dict(self):
        raise NotImplementedError('Must be defined in subclasses')

    def __call__(self, req, initial_input_dict={}, *args, **kwargs):
        try:
            super(BaseCallView, self).__call__(req, *args, **kwargs)
            input_dict = self.get_input_dict()
            input_dict.update(initial_input_dict)
            req.zato.client.invoke(self.service_name, input_dict)
            return HttpResponse()
        except Exception, e:
            msg = '{}, e:`{}`'.format(self.error_message, format_exc(e))
            logger.error(msg)
            return HttpResponseServerError(msg)

# ################################################################################################################################

class Delete(BaseCallView):
    """ Our subclasses will delete objects such as connections and others.
    """
    id_elem = 'id'
    def get_input_dict(self):
        return {
            self.id_elem: self.req.zato.id,
            'cluster_id': self.cluster_id
        }

# ################################################################################################################################

class SecurityList(object):
    def __init__(self):
        self.def_items = []

    def __iter__(self):
        return iter(self.def_items)

    def append(self, def_item):
        value = b'{0}/{1}'.format(def_item.sec_type, def_item.id)
        label = b'{0}/{1}'.format(SEC_DEF_TYPE_NAME[def_item.sec_type], def_item.name)
        self.def_items.append((value, label))

    @staticmethod
    def from_service(client, cluster_id, sec_type=None):
        sec_list = SecurityList()

        result = client.invoke('zato.security.get-list', {'cluster_id': cluster_id, 'sec_type':sec_type})

        for def_item in result:
            sec_list.append(def_item)

        return sec_list

# ################################################################################################################################

def id_only_service(req, service, id, error_template):
    try:
        result = req.zato.client.invoke(service, {'id': id})
        if not result.ok:
            raise Exception(result.details)
        else:
            return result
    except Exception, e:
        msg = error_template.format(e=format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################

def invoke_service_with_json_response(req, service, input_dict, ok_msg, error_template='', content_type='application/javascript',
        extra=None):
    try:
        req.zato.client.invoke(service, input_dict)
    except Exception, e:
        return HttpResponseServerError(e.message, content_type=content_type)
    else:
        response = {'msg': ok_msg}
        response.update(extra or {})
        response = dumps(response)
        return HttpResponse(response, content_type=content_type)

# ################################################################################################################################

def upload_to_server(req, cluster_id, service, error_msg_template):
    try:
        input_dict = {
            'cluster_id': cluster_id,
            'payload': req.read().encode('base64'),
            'payload_name': req.GET['qqfile']
        }
        req.zato.client.invoke(service, input_dict)

        return HttpResponse(dumps({'success': True}))

    except Exception, e:
        msg = error_msg_template.format(format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
