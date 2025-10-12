# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from contextlib import closing
from copy import deepcopy
from json import loads
from traceback import format_exc

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import basestring

# Zato
from zato.common.api import SECRET_SHADOW, ZATO_NONE
from zato.common.broker_message import MESSAGE_TYPE, SECURITY
from zato.common.odb.model import Cluster
from zato.common.util.api import get_response_value, make_cid_public
from zato.common.util.sql import search as sql_search
from zato.server.service import AsIs, Bool, Int, Service

# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################

logger = logging.getLogger('zato_admin')

# ################################################################################################################################

success_code = 0
success = '<error_code>{}</error_code>'.format(success_code)

# ################################################################################################################################

class SearchTool:
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

class AdminSIO:
    pass

# ################################################################################################################################

class GetListAdminSIO:
    input_optional = (Int('cur_page'), Bool('paginate'), 'query')

# ################################################################################################################################

class AdminService(Service):
    """ A Zato admin service, part of the Zato public API.
    """
    output_optional = ('_meta',)
    skip_before_handle = False

    class SimpleIO(AdminSIO):
        """ This empty definition is needed in case the service should be invoked through REST.
        """

    def __init__(self):
        super(AdminService, self).__init__()

# ################################################################################################################################

    def _init(self, is_http):
        if self._filter_by:
            self._search_tool = SearchTool(self._filter_by)
        super(AdminService, self)._init(is_http)

# ################################################################################################################################

    def before_handle(self):

        # Do not run if the service explicitly tells us not to
        if self.skip_before_handle:
            return

        # Do not log BASE64-encoded messages
        if self.name == 'zato.service.invoke':
            return

        if self.server.is_admin_enabled_for_info:

            # Prefer that first because it may be a generic connection
            # in which case we want to access its opaque attributes
            # that are not available through self.request.input.
            try:
                data = self.request.raw_request
                if not isinstance(data, dict):
                    data = loads(data)
            except Exception:
                data = self.request.input
            finally:
                to_copy = {}
                for k, v in data.items():
                    to_copy[k] = v

                data = deepcopy(to_copy)

            for k in data:
                if 'password' in k:
                    data[k] = SECRET_SHADOW

            logger.info('Request; service:`%s`, data:`%s` cid:`%s`, ', self.name, data, self.cid)

# ################################################################################################################################

    def handle(self, *args, **kwargs):
        raise NotImplementedError('Should be overridden by subclasses (AdminService.handle -> {})'.format(self.name))

# ################################################################################################################################

    def _new_zato_instance_with_cluster(self, instance_class, cluster_id=None, **kwargs):

        if not cluster_id:
            cluster_id = self.request.input.get('cluster_id')
            cluster_id = cluster_id or self.server.cluster_id

        with closing(self.odb.session()) as session:
            cluster_id = cluster_id or self.request.input.cluster_id
            cluster = session.query(Cluster).\
                   filter(Cluster.id==cluster_id).\
                   one()
        return instance_class(cluster=cluster, **kwargs)

# ################################################################################################################################

    def after_handle(self):

        # Do not log BASE64-encoded messages
        if self.name == 'zato.service.invoke':
            return

        if self.server.is_admin_enabled_for_info:
            logger.info('Response; service:`%s`, data:`%s` cid:`%s`, ',
                self.name, get_response_value(self.response), self.cid)

        payload = self.response.payload
        is_text = isinstance(payload, basestring)
        needs_meta = self.request.input.get('needs_meta', True)

        if needs_meta and hasattr(self, '_search_tool'):
            if not is_text:
                payload.zato_meta = self._search_tool.output_meta

# ################################################################################################################################

    def get_data(self, *args, **kwargs):
        raise NotImplementedError('Should be overridden by subclasses (AdminService.get_data)')

# ################################################################################################################################

    def _search(self, search_func, session=None, cluster_id=None, *args, **kwargs) -> 'anylist':
        """ Adds search criteria to an SQLAlchemy query based on the service's (self) search configuration.
        """

        # Should we break the results into individual pages
        needs_pagination = self.request.input.get('paginate')

        if needs_pagination:
            result = sql_search(search_func, self.request.input, self._filter_by, session, cluster_id, *args, **kwargs)
            self._search_tool.set_output_meta(result)
        else:
            # No pagination requested at all
            result = search_func(session, cluster_id, *args)

        return result

# ################################################################################################################################

class Ping(AdminService):
    """ A ping service, useful for API testing.
    """
    name = 'demo.ping'

    def handle(self):
        pub_cid = make_cid_public(self.cid)
        self.response.payload = f'{{"is_ok":true, "cid":"{pub_cid}"}}'

        self.publish('demo.1', 'Hello!')

# ################################################################################################################################

class ServerInvoker(AdminService):

    name = 'zato.server.invoker'

    def handle(self):
        func = getattr(self.server, self.request.raw_request['func_name'])
        response = func()
        self.response.payload = response

# ################################################################################################################################

class ChangePasswordBase(AdminService):
    """ A base class for handling the changing of any of the ODB passwords.
    """
    # Subclasses may wish to set it to False to special-case what they need to deal with
    password_required = True

    class SimpleIO(AdminSIO):
        input_required = 'password1', 'password2'
        input_optional = Int('id'), 'name', 'type_'
        output_required = AsIs('id')

    def _handle(self, class_, auth_func, action, name_func=None, instance_id=None, msg_type=MESSAGE_TYPE.TO_PARALLEL_ALL,
        *args, **kwargs):

        instance_id = instance_id or self.request.input.get('id')
        instance_name = self.request.input.name

        with closing(self.odb.session()) as session:
            password1 = self.request.input.get('password1', '')
            password2 = self.request.input.get('password2', '')

            password1_decrypted = self.server.decrypt(password1) if password1 else password1
            password2_decrypted = self.server.decrypt(password2) if password2 else password2

            try:
                if self.password_required:
                    if not password1_decrypted:
                        raise Exception('Password must not be empty')

                    if not password2_decrypted:
                        raise Exception('Password must be repeated')

                if password1_decrypted != password2_decrypted:
                    raise Exception('Passwords need to be the same')

                # Construct a basic query ..
                query = session.query(class_)

                # .. look up by ID if it is given ..
                if instance_id:
                    query = query.filter(class_.id==instance_id)

                # .. try to use the name if ID is not available ..
                elif instance_name:
                    query = query.filter(class_.name==instance_name)

                # .. otherwise, we do not know how to find the instance -> raise an exception.
                else:
                    raise Exception('Either ID or name are required on input')

                # If we are here, it means that we can find the instance.
                instance = query.first()

                if not instance:
                    raise Exception('Could not find instance with id:`{}` and name:`{}` ({})'.format(
                        instance_id, instance_name, class_))

                auth_func(instance, password1_decrypted)

                session.add(instance)
                session.commit()

                if msg_type:
                    name = name_func(instance) if name_func else instance.name

                    self.request.input.id = instance_id
                    self.request.input.action = action
                    self.request.input.name = name
                    self.request.input.password = password1_decrypted
                    self.request.input.salt = kwargs.get('salt')

                    # Always return ID of the object whose password we changed
                    self.response.payload.id = instance_id

                    for attr in kwargs.get('publish_instance_attrs', []):
                        self.request.input[attr] = getattr(instance, attr, ZATO_NONE)

                    self.broker_client.publish(self.request.input)

                    if action == SECURITY.BASIC_AUTH_CHANGE_PASSWORD.value:
                        self.request.input.cid = self.cid
                        self.request.input.username = instance.username
                        self.broker_client.publish_to_pubsub(self.request.input)

            except Exception:
                self.logger.error('Could not update password, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################
