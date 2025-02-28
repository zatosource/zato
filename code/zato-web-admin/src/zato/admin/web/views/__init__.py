# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pylint: disable=attribute-defined-outside-init

# stdlib
import logging
from base64 import b64encode
from datetime import datetime, timedelta
from itertools import chain
from traceback import format_exc

# bunch
from bunch import Bunch

# Django
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError

# pytz
from pytz import UTC

# Zato
try:
    from zato.admin.settings import lb_agent_use_tls
except ImportError:
    lb_agent_use_tls = True

from zato.admin.settings import ssl_key_file, ssl_cert_file, ssl_ca_certs, LB_AGENT_CONNECT_TIMEOUT
from zato.admin.web import from_utc_to_user
from zato.admin.web.util import get_template_response
from zato.common.api import CONNECTION, SEC_DEF_TYPE_NAME, URL_TYPE, ZATO_NONE, ZATO_SEC_USE_RBAC
from zato.common.exception import ZatoException
from zato.common.json_internal import dumps
from zato.common.util.api import get_lb_client as _get_lb_client, validate_python_syntax

# ################################################################################################################################

from django.urls import reverse as django_url_reverse
from django.utils.text import slugify

# For pyflakes
django_url_reverse = django_url_reverse
slugify = slugify

# ################################################################################################################################

if 0:
    from zato.client import ServiceInvokeResponse
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

SKIP_VALUE = 'zato.skip.value'

# ################################################################################################################################

def parse_response_data(response):
    """ Parses out data and metadata out an internal API call response.
    """
    meta = response.data.pop('_meta', None)
    keys = list(response.data.keys())
    data = response.data[keys[0]]
    return data, meta

# ################################################################################################################################

def invoke_list_service(client, cluster, service, extra=None):

    out = {}
    request = {'cluster_id':cluster.id}
    request.update(extra or {})
    for item in client.invoke(service, request):
        out[item.id] = item.name

    return out

# ################################################################################################################################

def get_definition_list(client, cluster, def_type):
    """ Returns all definitions of a given type existing on a given cluster.
    """
    return invoke_list_service(client, cluster, 'zato.definition.{}.get-list'.format(def_type))

# ################################################################################################################################

def get_outconn_rest_list(req, name_to_id=False):
    """ Returns a list of all outgoing REST connections.
    """
    out = {}
    response = req.zato.client.invoke('zato.http-soap.get-list', {
        'cluster_id': req.zato.cluster_id,
        'connection': CONNECTION.OUTGOING,
        'transport': URL_TYPE.PLAIN_HTTP,
    })

    for item in response:

        if name_to_id:
            key   = item.name
            value = item.id
        else:
            key   = item.id
            value = item.name

        out[key] = value

    return out

# ################################################################################################################################

def get_tls_ca_cert_list(client, cluster):
    """ Returns all TLS CA certs on a given cluster.
    """
    return invoke_list_service(client, cluster, 'zato.security.tls.ca-cert.get-list')

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
    return _get_lb_client(lb_agent_use_tls, cluster.lb_host, cluster.lb_agent_port, ssl_ca_certs,
                          ssl_key_file, ssl_cert_file, LB_AGENT_CONNECT_TIMEOUT)

# ################################################################################################################################

def method_allowed(*methods_allowed):
    """ Accepts a list (possibly one-element long) of HTTP methods allowed
    for a given view. An exception will be raised if a request has been made
    with a method outside of those allowed, otherwise the view executes
    unchanged.
    """
    def inner_method_allowed(view):
        def inner_view(*args, **kwargs):
            req = args[1] if len(args) > 1 else args[0]
            if req.method not in methods_allowed:
                msg = 'Method `{}` is not allowed here `{}`, methods allowed:`{}`'.format(
                    req.method, view, methods_allowed)
                logger.error(msg)
                raise Exception(msg)
            return view(*args, **kwargs)
        return inner_view
    return inner_method_allowed

# ################################################################################################################################

def set_servers_state(cluster, client):
    """ Assignes 3 flags to the cluster indicating whether load-balancer believes the servers are UP, DOWN or in the MAINT mode.
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

def change_password(req, service_name, field1='password1', field2='password2', success_msg='Password updated', data=None):

    data = data or req.POST
    secret_type = data.get('secret_type')

    if secret_type == 'secret':
        success_msg = 'Secret updated'

    try:
        input_dict = {
            'id': data.get('id'),
            'password1': data.get(field1, ''),
            'password2': data.get(field2, ''),
            'type_': data.get('type_', ''),
        }
        req.zato.client.invoke(service_name, input_dict)

    except Exception:
        msg = 'Caught an exception, e:`{}`'.format(format_exc())
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

def get_security_groups_from_checkbox_list(params, prefix, field_name_prefix='http_soap_security_group_checkbox_'):

    # Our response to produce
    groups = []

    # Local variables
    full_prefix = prefix + field_name_prefix

    for item in params:
        if item.startswith(full_prefix):
            item = item.replace(full_prefix, '')
            groups.append(item)

    return groups

# ################################################################################################################################

def build_sec_def_link(cluster_id, sec_type, sec_name):

    sec_type_name = SEC_DEF_TYPE_NAME[sec_type]
    sec_type = sec_type.replace('_', '-')
    url_path = django_url_reverse('security-{}'.format(sec_type))

    link = """
    {sec_type_name}
    <br/>
    <a href="{url_path}?cluster={cluster_id}&amp;query={sec_name}">{sec_name}</a>
    """.format(**{
           'cluster_id': cluster_id,
           'sec_type_name': sec_type_name,
           'sec_name': sec_name,
           'url_path': url_path,
        }).strip()

    return link

# ################################################################################################################################

def build_sec_def_link_by_input(req, cluster_id, input_data):
    # type: (dict) -> str

    security_id = input_data.get('security_id')
    if security_id and security_id != ZATO_NONE:

        security_id = extract_security_id(input_data)
        sec_response = id_only_service(req, 'zato.security.get-by-id', security_id).data

        return build_sec_def_link(cluster_id, sec_response.sec_type, sec_response.name)

# ################################################################################################################################

class BaseView:
    method_allowed = 'method_allowed-must-be-defined-in-a-subclass'
    service_name = None
    async_invoke = False
    form_prefix = ''

    def __init__(self):
        self.req = None # type: any_
        self.cluster_id = None
        self.clear_user_message()
        self.ctx = {}

    def __call__(self, req, *args, **kwargs):
        self.req = req
        for k, v in kwargs.items():
            self.req.zato.args[k] = v
        self.cluster_id = None
        self.fetch_cluster_id()

    def build_sec_def_link_by_input(self, input_data):
        return build_sec_def_link_by_input(self.req, self.cluster_id, input_data)

    def on_before_append_item(self, item):
        return item

    def get_output_class(self):
        pass

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

    def get_service_name(self, *_args, **_kwargs):
        raise NotImplementedError('May be implemented by subclasses')

    def fetch_cluster_id(self):
        # Doesn't look overtly smart right now but more code will follow to sanction
        # the existence of this function
        cluster_id = self.req.zato.cluster_id

        if cluster_id:
            self.cluster_id = int(cluster_id)

    def populate_initial_input_dict(self, initial_input_dict):
        """ May be overridden by subclasses if needed.
        """

    def get_sec_def_list(self, sec_type):
        if self.req.zato.get('client'):
            return SecurityList.from_service(self.req.zato.client, self.req.zato.cluster.id, sec_type)
        else:
            return []

    def set_input(self, req=None, default_attrs=('cur_page', 'query')):
        req = req or self.req
        self.input.update({
            'cluster_id':self.cluster_id,
            'paginate': getattr(self, 'paginate', False),
        })

        initial_input_dict = {}
        self.populate_initial_input_dict(initial_input_dict)
        self.input.update(initial_input_dict)

        for name in chain(self.SimpleIO.input_required, self.SimpleIO.input_optional, default_attrs):
            if name != 'cluster_id':

                value = req.GET.getlist(name)
                if value:
                    value = value if len(value) > 1 else value[0]

                if not value:
                    value = req.POST.getlist(self.form_prefix + name)
                    if value:
                        value = value if len(value) > 1 else value[0]

                if not value:
                    value = req.zato.args.get(self.form_prefix + name)

                self.input[name] = value

        self.on_after_set_input()

# ################################################################################################################################

class Index(BaseView):
    """ A base class upon which other index views are based.
    """
    url_name = 'url_name-must-be-defined-in-a-subclass'
    template = 'template-must-be-defined-in-a-subclass-or-get-template-name'
    wrapper_type = None

    output_class = None
    clear_self_items = True
    update_request_with_self_input = True

    def __init__(self):
        super(Index, self).__init__()
        self.input = Bunch()
        self.items = []
        self.item = None
        self.clear_user_message()

    def can_invoke_admin_service(self):
        """ Returns a boolean flag indicating that we know what service to invoke, what cluster it is on
        and that all the required parameters were given in GET request. cluster_id doesn't have to be in GET,
        'cluster' will suffice.
        """
        input_elems = list(self.req.GET.keys()) + list(self.req.zato.args.keys())

        if not self.cluster_id:
            logger.info('Value missing; self.cluster_id `%s`', self.cluster_id)
            return False

        for elem in self.SimpleIO.input_required:
            if elem == 'cluster_id':
                continue
            if not elem in input_elems:
                logger.info('Elem `%s` not in input_elems `%s`', elem, input_elems)
                return False
            value = self.req.GET.get(elem)
            if not value:
                value = self.req.zato.args.get(elem)
                if not value:
                    logger.info('Elem `%s` not in self.req.zato.args `%s`', elem, self.req.zato.args)
                    return False
        return True

    def before_invoke_admin_service(self):
        pass

    def get_service_name(self, _req):
        raise NotImplementedError('May be implemented in subclasses')

    def get_initial_input(self):
        return {}

    def get_template_name(self):
        """ May be overridden by subclasses to dynamically decide which template to use,
        otherwise self.template will be employed.
        """

    def should_extract_top_level(self, _keys):
        return True

    def invoke_admin_service(self) -> 'ServiceInvokeResponse':
        if self.req.zato.get('cluster'):
            func = self.req.zato.client.invoke_async if self.async_invoke else self.req.zato.client.invoke
            service_name = self.service_name if self.service_name else self.get_service_name(self.req)
            request = self.get_initial_input()

            if self.update_request_with_self_input:
                request.update(self.input)
            else:
                logger.info('Not updating request with self.input')

            # Auto-populate the field if it exists
            if self.wrapper_type:
                request['wrapper_type'] = self.wrapper_type

            logger.info('Invoking `%s` with `%s`', service_name, request)

            return func(service_name, request)

    def should_include(self, item) -> 'bool':
        return True

    def _handle_single_item_list(self, container, item_list):
        """ Creates a new instance of the model class for each of the element received
        and fills it in with received attributes.
        """
        names = tuple(chain(self.SimpleIO.output_required, self.SimpleIO.output_optional))

        for msg_item in item_list or []:

            output_class = self.get_output_class()
            item = output_class() if output_class else self.output_class()

            # Use attributes that were definded upfront for the SimpleIO definition
            # or use everything that we received from the service.
            names = names if names else msg_item.keys()

            for name in sorted(names):
                value = getattr(msg_item, name, None)
                if value is not None:
                    value = getattr(value, 'text', '') or value
                if value or value in (0, [], {}):
                    setattr(item, name, value)

            item = self.on_before_append_item(item)

            if isinstance(item, (list, tuple)):
                func = container.extend
            else:
                func = container.append

            func(item)

    def handle_item_list(self, item_list, _ignored_is_extracted):
        """ Creates a new instance of the model class for each of the element received
        and fills it in with received attributes.
        """
        names = tuple(chain(self.SimpleIO.output_required, self.SimpleIO.output_optional))

        for msg_item in (item_list or []):

            item = self.output_class()
            for name in sorted(names):
                value = getattr(msg_item, name, None)
                if value is not None:
                    value = getattr(value, 'text', '') or value
                if value or value == 0:
                    setattr(item, name, value)

            if not self.should_include(item):
                continue

            item = self.on_before_append_item(item)

            if isinstance(item, (list, tuple)):
                func = self.items.extend
            else:
                func = self.items.append

            func(item)

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

            # The value of clear_self_items if True if we are returning a single list of elements,
            # based on self.extract_top_level_key_from_payload.
            if self.clear_self_items:
                del self.items[:]

            self.item = None
            self.set_input()

            return_data = {'cluster_id':self.cluster_id}
            output_repeated = getattr(self.SimpleIO, 'output_repeated', False)

            response = None

            if self.can_invoke_admin_service():
                self.before_invoke_admin_service()
                response = self.invoke_admin_service()

                logger.info('Response from service: `%s`', response.data)

                if response and response.ok:
                    return_data['response_inner'] = response.inner_service_response

                    if output_repeated:
                        if response and isinstance(response.data, dict):
                            response.data.pop('_meta', None)
                            keys = list(response.data.keys())
                            if self.should_extract_top_level(keys):
                                data = response.data[keys[0]]
                                is_extracted = True
                            else:
                                data = response.data
                                is_extracted = False
                        else:
                            data = response.data
                            is_extracted = False

                        # At this point, this may be just a list of elements, if self.should_extract_top_level returns True,
                        # or a dictionary of keys pointing to lists with such elements.
                        self.handle_item_list(data, is_extracted)

                    else:
                        self._handle_item(response.data)
                else:
                    self.user_message = response.details
            else:
                logger.info('can_invoke_admin_service returned False, not invoking an admin service:[%s]', self.service_name)

            template_name = self.get_template_name() or self.template

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
            return_data['zato_template_name'] = template_name

            view_specific = self.handle()
            if view_specific:
                return_data.update(view_specific)

            return_data = self.handle_return_data(return_data)

            for k, v in sorted(return_data.items()):
                logger.info('Index key/value `%s` -> `%r`', k, v)

            return get_template_response(req, template_name, return_data)

        except Exception:
            return HttpResponseServerError(format_exc())

    def handle(self, req=None, *args, **kwargs):
        return {}

# ################################################################################################################################

class CreateEdit(BaseView):
    """ Subclasses of this class will handle the creation/updates of Zato objects.
    """

    def __init__(self, *args, **kwargs):
        super(CreateEdit, self).__init__()
        self.input = Bunch()
        self.input_dict = {}

    def __call__(self, req, initial_input_dict=None, initial_return_data=None, *args, **kwargs):
        """ Handles the request, taking care of common things and delegating
        control to the subclass for fetching this view-specific data.
        """
        initial_input_dict = initial_input_dict or {}
        initial_return_data = initial_return_data or {}
        self.input_dict.clear()
        self.clear_user_message()

        try:
            super(CreateEdit, self).__call__(req, *args, **kwargs)
            self.set_input()
            self.populate_initial_input_dict(initial_input_dict)

            input_dict = {'cluster_id': self.cluster_id}
            post_id = self.req.POST.get('id')

            if post_id:
                input_dict['id'] = post_id

            input_dict.update(initial_input_dict)

            for name in chain(self.SimpleIO.input_required, self.SimpleIO.input_optional):
                if name not in input_dict and name not in self.input_dict:
                    value = self.input.get(name)
                    value = self.pre_process_item(name, value)
                    if value != SKIP_VALUE:
                        input_dict[name] = value

            self.input_dict.update(input_dict)
            self.pre_process_input_dict(self.input_dict)

            logger.info('Request self.input_dict %s', self.input_dict)
            logger.info('Request self.SimpleIO.input_required %s', self.SimpleIO.input_required)
            logger.info('Request self.SimpleIO.input_optional %s', self.SimpleIO.input_optional)
            logger.info('Request self.input %s', self.input)
            logger.info('Request self.req.GET %s', self.req.GET)
            logger.info('Request self.req.POST %s', self.req.POST)

            logger.info('Sending `%s` to `%s`', self.input_dict, self.service_name)
            response = self.req.zato.client.invoke(self.service_name, self.input_dict)

            if response.ok:
                logger.info('Received `%s` from `%s`', response.data, self.service_name)
                return_data = {
                    'message': self.success_message(response.data)
                }

                return_data.update(initial_return_data)

                for name in chain(self.SimpleIO.output_optional, self.SimpleIO.output_required):
                    if name not in initial_return_data:
                        value = getattr(response.data, name, None)
                        if value:
                            value = str(value)
                        return_data[name] = value

                self.post_process_return_data(return_data)

                logger.info('CreateEdit data for frontend `%s`', return_data)

                return HttpResponse(dumps(return_data), content_type='application/javascript')
            else:
                msg = 'response:`{}`, details.response.details:`{}`'.format(response, response.details)
                logger.error(msg)
                raise ZatoException(msg=msg)

        except Exception:
            return HttpResponseServerError(format_exc())

    def pre_process_input_dict(self, input_dict):
        pass

    def pre_process_item(self, name, value):
        return value

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

class BaseCallView(BaseView):

    method_allowed = 'POST'
    error_message = 'error_message-must-be-defined-in-a-subclass'

    def get_input_dict(self):
        raise NotImplementedError('Must be defined in subclasses')

    def build_http_response(self, response):
        return HttpResponse()

    def __call__(self, req, initial_input_dict=None, *args, **kwargs):
        initial_input_dict = initial_input_dict or {}
        try:
            super(BaseCallView, self).__call__(req, *args, **kwargs)
            input_dict = self.get_input_dict()
            input_dict.update(initial_input_dict)
            response = req.zato.client.invoke(self.service_name or self.get_service_name(), input_dict)
            http_response = self.build_http_response(response)
            return http_response
        except Exception:
            msg = '{}, e:`{}`'.format(self.error_message, format_exc())
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

class SecurityList:
    def __init__(self, needs_def_type_name_label=True):
        self.needs_def_type_name_label = needs_def_type_name_label
        self.def_items = []

    def __iter__(self):
        return iter(self.def_items)

    def append(self, def_item):
        value = '{}/{}'.format(def_item.sec_type, def_item.id)
        if self.needs_def_type_name_label:
            label = '{}/{}'.format(SEC_DEF_TYPE_NAME[def_item.sec_type], def_item.name)
        else:
            label = def_item.name
        self.def_items.append((value, label))

    @staticmethod
    def from_service(client, cluster_id, sec_type=None, needs_def_type_name_label=True):

        out = SecurityList(needs_def_type_name_label=needs_def_type_name_label)
        sec_type = sec_type if isinstance(sec_type, list) else [sec_type]

        result = client.invoke('zato.security.get-list', {
            'cluster_id': cluster_id,
        })

        for def_item in result:
            out.append(def_item)

        return out

# ################################################################################################################################

def id_only_service(req, service, id, error_template='{}', initial=None):
    try:
        request = {
            'cluster_id': req.zato.cluster_id,
        }

        if id:
            request['id'] = id

        if initial:
            request.update(initial)

        logger.info('Sending `%s` to `%s` (id_only_service)', request, service)

        result = req.zato.client.invoke(service, request)

        if not result.ok:
            raise Exception(result.details)
        else:
            return result
    except Exception as e:
        msg = error_template.format(e.args[0])
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################

def ping_connection(req, service, connection_id, connection_type='{}', ping_path=None) -> 'any_':
    error_template = 'Could not ping {}, e:`{{}}`'.format(connection_type)
    if ping_path:
        initial = {'ping_path': ping_path}
    else:
        initial = None
    response = id_only_service(req, service, connection_id, error_template, initial)
    if isinstance(response, HttpResponseServerError):
        return response
    else:

        if 'info' in response.data:
            is_success = response.data.is_success
            response_class = HttpResponse if is_success else HttpResponseServerError
            info = response.data.info
        else:
            response_class = HttpResponse
            info = 'Ping OK'

        return response_class(info)

# ################################################################################################################################

def invoke_service_with_json_response(req, service, input_dict, ok_msg, error_template='', content_type='application/javascript',
        extra=None):
    try:
        req.zato.client.invoke(service, input_dict)
    except Exception as e:
        return HttpResponseServerError(e.message, content_type=content_type)
    else:
        response = {'msg': ok_msg}
        response.update(extra or {})
        response = dumps(response)
        return HttpResponse(response, content_type=content_type)

# ################################################################################################################################

def upload_to_server(
    client,
    data,
    payload_name,
    cluster_id=1,
    service='zato.service.upload-package',
    error_msg_template='Deployment error, e:`{}`',
):

    try:

        # First, if it's Python code, check if the source code is valid
        if payload_name.endswith('.py'):
            validate_python_syntax(data)

        input_dict = {
            'cluster_id': cluster_id,
            'payload': b64encode(data),
            'payload_name': payload_name,
        }

        response = client.invoke(service, input_dict)

        out = {
            'success': True,
            'data':'OK, deployed',
            'response_time_human': response.inner.headers.get('X-Zato-Response-Time-Human')
        }

        return HttpResponse(dumps(out))

    except SyntaxError:
        out = {
            'success': False,
            'data':format_exc(),
            'response_time_human': 'default' # This is required by the frontend
        }
        return HttpResponseBadRequest(dumps(out))

    except Exception:
        msg = error_msg_template.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################

def extract_security_id(item):
    # type: (dict) -> int
    security_id = item.get('security_id') # type: str

    if not security_id:
        return
    else:
        if security_id == ZATO_NONE:
            return security_id
        else:
            security_id = security_id.split('/')
            security_id = security_id[1]
            return int(security_id)

# ################################################################################################################################

def get_http_channel_security_id(item):
    _security_id = item.security_id
    if _security_id:
        security_id = '{}/{}'.format(item.sec_type, _security_id)
    else:
        if item.sec_use_rbac:
            security_id = ZATO_SEC_USE_RBAC
        else:
            security_id = ZATO_NONE

    return security_id

# ################################################################################################################################

def invoke_action_handler(req, service_name:'str', send_attrs:'any_'=None, extra=None) -> 'any_':

    try:
        request = {
            'cluster_id': req.zato.cluster_id
        }

        send_attrs = send_attrs or {}
        for name in send_attrs:
            request[name] = req.POST.get(name, '')

        extra = extra or {}
        request.update(extra)

        logger.info('Invoking `%s` with `%s`', service_name, request)
        response = req.zato.client.invoke(service_name, request)
        logger.info('Response received `%s`', response.data)

        if response.ok:

            if 'response_data' in (response.data or ''):
                response_data = response.data['response_data']
            else:
                response_data = response.data

            logger.info('Invocation response -> `%s` (`%s`)', response_data, service_name)

            if isinstance(response_data, dict):
                response_data = dumps(response_data)
                logger.info('Returning `%s` from `%s`', response_data, service_name)
            return HttpResponse(response_data, content_type='application/javascript')
        else:
            logger.warn('Raising exception based on `%s` (`%s`)', response.details, service_name)
            raise Exception(response.details)
    except Exception:
        msg = 'Caught an exception, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################

def get_security_name_link(req, sec_type, sec_name, *, needs_type=True):

    sec_type_name = SEC_DEF_TYPE_NAME[sec_type]
    sec_type_as_link = sec_type.replace('_', '-')
    security_href = f'/zato/security/{sec_type_as_link}/?cluster={req.zato.cluster_id}&amp;query={sec_name}'
    security_link = f'<a href="{security_href}">{sec_name}</a>'
    if needs_type:
        sec_name = f'{sec_type_name}<br/>{security_link}'
    else:
        sec_name = security_link
    return sec_name

# ################################################################################################################################
# ################################################################################################################################

def get_group_list(req:'any_', group_type:'str', *, http_soap_channel_id:'str'='') -> 'anylist':

    # Get a list of all the groups that exist
    response = req.zato.client.invoke('zato.groups.get-list', {
        'group_type': group_type,
    })

    # .. extract the business data ..
    groups = response.data or []

    # .. if we have a channel ID on input, we need to indicate which groups are assigned to it ..
    if http_soap_channel_id:
        http_soap_channel = req.zato.client.invoke('zato.http-soap.get', {
            'id': http_soap_channel_id,
        })
        http_soap_channel = http_soap_channel.data
        http_soap_channel_security_groups = http_soap_channel.get('security_groups') or []

        for item in groups:
            if item.id in http_soap_channel_security_groups:
                item.is_assigned = True
            else:
                item.is_assigned = False

    # .. and return it to our caller.
    return groups

# ################################################################################################################################
# ################################################################################################################################
