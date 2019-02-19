# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from contextlib import closing
from traceback import format_exc

# Python 2/3 compatibility
from past.builtins import basestring

# Zato
from zato.common import SECRET_SHADOW, zato_namespace, ZATO_NONE
from zato.common.broker_message import MESSAGE_TYPE
from zato.common.odb.model import Cluster
from zato.common.util import get_response_value, replace_private_key
from zato.common.util.sql import search as sql_search
from zato.server.service import Bool, Int, Service
from zato.server.service.reqresp.sio import convert_sio

# ################################################################################################################################

logger = logging.getLogger('zato_admin')
has_info = logger.isEnabledFor(logging.INFO)

# ################################################################################################################################

success_code = 0
success = '<error_code>{}</error_code>'.format(success_code)

# ################################################################################################################################

class SearchTool(object):
    """ Optionally attached to each internal service returning a list of results responsible for extraction
    and serialization of search criteria.
    """
    _search_attrs = 'num_pages', 'cur_page', 'prev_page', 'next_page', 'has_prev_page', 'has_next_page', 'page_size', 'total'

    def __init__(self, *criteria):
        self.criteria = criteria
        self.output_meta = {'search':{}}

    def __nonzero__(self):
        return self.output_meta['search'].get('num_pages')

    def set_output_meta(self, result):
        self.output_meta['search'].update(result.to_dict())

# ################################################################################################################################

class AdminSIO(object):
    namespace = zato_namespace

# ################################################################################################################################

class GetListAdminSIO(object):
    namespace = zato_namespace
    input_optional = (Int('cur_page'), Bool('paginate'), 'query')

# ################################################################################################################################

class AdminService(Service):
    """ A Zato admin service, part of the Zato public API.
    """
    output_optional = ('_meta',)

    class SimpleIO(AdminSIO):
        """ This empty definition is needed in case the service should be invoked through REST.
        """

    def __init__(self):
        super(AdminService, self).__init__()

# ################################################################################################################################

    def _init(self, is_http):
        if self._filter_by:
            self._search_tool = SearchTool(self._filter_by)
        self.ipc_api = self.server.ipc_api
        super(AdminService, self)._init(is_http)

# ################################################################################################################################

    def _convert_sio_elem(self, param_name, value):
        return convert_sio(self.cid, param_name, param_name, value, True, False, self.request.bool_parameter_prefixes,
            self.request.int_parameters, self.request.int_parameter_suffixes, False, self.server.encrypt, True)

# ################################################################################################################################

    def before_handle(self, has_info=has_info):
        if has_info:
            request = dict(self.request.input)
            for k, v in request.items():

                v = replace_private_key(v)

                if 'password' in k:
                    request[k] = SECRET_SHADOW

            logger.info('cid:`%s`, name:`%s`, request:`%s`', self.cid, self.name, request)

# ################################################################################################################################

    def handle(self, *args, **kwargs):
        raise NotImplementedError('Should be overridden by subclasses (AdminService.handle)')

# ################################################################################################################################

    def _new_zato_instance_with_cluster(self, instance_class, cluster_id=None, **kwargs):
        with closing(self.odb.session()) as session:
            cluster_id = cluster_id or self.request.input.cluster_id
            cluster = session.query(Cluster).\
                   filter(Cluster.id==cluster_id).\
                   one()
        return instance_class(cluster=cluster, **kwargs)

# ################################################################################################################################

    def after_handle(self):

        payload = self.response.payload
        is_text = isinstance(payload, basestring)
        needs_meta = self.request.input.get('needs_meta', True)

        if needs_meta and hasattr(self, '_search_tool') and not is_text:
            payload.zato_meta = self._search_tool.output_meta

        logger.info(
            'cid:`%s`, name:`%s`, response:`%r`', self.cid, self.name, replace_private_key(get_response_value(self.response)))

# ################################################################################################################################

    def get_data(self, *args, **kwargs):
        raise NotImplementedError('Should be overridden by subclasses (AdminService.get_data)')

# ################################################################################################################################

    def _search(self, search_func, session=None, cluster_id=None, *args, **kwargs):
        """ Adds search criteria to an SQLAlchemy query based on the service's (self) search configuration.
        """
        config = self.request.input

        # No pagination requested at all
        if not config.get('paginate'):
            result = search_func(session, cluster_id, *args)
        else:
            result = sql_search(search_func, self.request.input, self._filter_by, session, cluster_id, *args, **kwargs)
            self._search_tool.set_output_meta(result)

        return result

# ################################################################################################################################

class Ping(AdminService):
    """ A ping service, useful for API testing.
    """
    class SimpleIO(AdminSIO):
        output_required = ('pong',)
        response_elem = 'zato_ping_response'

    def handle(self):
        self.response.payload.pong = 'zato'

    def after_handle(self):
        """ A no-op method because zato.ping can be used in benchmarks and the parent's .before/after_handle
        would constitute about 10-15% of the overhead each. With typical admin services it is fine because
        they are rarely used but in benchmarking, this is unnecessary and misleading seeing as they do things
        that user-defined services don't do.
        """

    before_handle = after_handle

# ################################################################################################################################

class Ping2(Ping):
    """ Works exactly the same as zato.ping, added to have another service for API testing.
    """
    class SimpleIO(Ping.SimpleIO):
        response_elem = 'zato_ping2_response'

# ################################################################################################################################

class ChangePasswordBase(AdminService):
    """ A base class for handling the changing of any of the ODB passwords.
    """
    # Subclasses may wish to set it to False to special-case what they need to deal with
    password_required = True

    class SimpleIO(AdminSIO):
        input_required = (Int('id'), 'password1', 'password2')

    def _handle(self, class_, auth_func, action, name_func=None, msg_type=MESSAGE_TYPE.TO_PARALLEL_ALL,
                *args, **kwargs):

        with closing(self.odb.session()) as session:
            password1 = self.request.input.get('password1', '')
            password2 = self.request.input.get('password2', '')

            password1_decrypted = self.server.decrypt(password1)
            password2_decrypted = self.server.decrypt(password2)

            try:
                if self.password_required:
                    if not password1_decrypted:
                        raise Exception('Password must not be empty')

                    if not password2_decrypted:
                        raise Exception('Password must be repeated')

                if password1_decrypted != password2_decrypted:
                    raise Exception('Passwords need to be the same')

                auth = session.query(class_).\
                    filter(class_.id==self.request.input.id).\
                    one()

                auth_func(auth, password1)

                session.add(auth)
                session.commit()

                if msg_type:
                    name = name_func(auth) if name_func else auth.name

                    self.request.input.action = action
                    self.request.input.name = name
                    self.request.input.password = password1_decrypted
                    self.request.input.salt = kwargs.get('salt')

                    for attr in kwargs.get('publish_instance_attrs', []):
                        self.request.input[attr] = getattr(auth, attr, ZATO_NONE)

                    self.broker_client.publish(self.request.input, msg_type=msg_type)

            except Exception:
                self.logger.error('Could not update password, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################
