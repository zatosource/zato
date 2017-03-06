# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common import SEARCH, SECRET_SHADOW, zato_namespace, ZATO_NONE
from zato.common.broker_message import MESSAGE_TYPE
from zato.common.util import get_response_value, replace_private_key
from zato.server.service import Service

# ################################################################################################################################

logger = logging.getLogger('zato_admin')
has_info = logger.isEnabledFor(logging.INFO)

# ################################################################################################################################

success_code = 0
success = '<error_code>{}</error_code>'.format(success_code)

# ################################################################################################################################

_default_page_size = SEARCH.ZATO.DEFAULTS.PAGE_SIZE.value
_max_page_size = _default_page_size * 5

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
        meta = self.output_meta['search']

        for name in self._search_attrs:
            meta[name] = getattr(result, name)

# ################################################################################################################################

class AdminService(Service):
    """ A Zato admin service, part of the Zato public API.
    """
    output_optional = ('_meta',)

    def __init__(self):
        super(AdminService, self).__init__()

# ################################################################################################################################

    def _init(self, is_http):
        if self._filter_by:
            self._search_tool = SearchTool(self._filter_by)

        self.ipc_api = self.server.ipc_api

        super(AdminService, self)._init(is_http)

# ################################################################################################################################

    def before_handle(self, has_info=has_info):
        if has_info:
            request = dict(self.request.input)
            for k, v in request.items():

                v = replace_private_key(v)

                if 'password' in k:
                    request[k] = SECRET_SHADOW

            logger.info('cid:[%s], name:[%s], SIO request:[%s]', self.cid, self.name, request)

# ################################################################################################################################

    def handle(self, *args, **kwargs):
        raise NotImplementedError('Should be overridden by subclasses')

# ################################################################################################################################

    def after_handle(self):
        payload = self.response.payload
        is_basestring = isinstance(payload, basestring)
        needs_meta = self.request.input.get('needs_meta', True)

        if needs_meta and hasattr(self, '_search_tool') and not is_basestring:
            payload.zato_meta = self._search_tool.output_meta

        logger.info(
            'cid:`%s`, name:`%s`, response:`%s`', self.cid, self.name, replace_private_key(get_response_value(self.response)))

# ################################################################################################################################

    def get_data(self, *args, **kwargs):
        raise NotImplementedError('Should be overridden by subclasses')

# ################################################################################################################################

    def _search(self, search_func, session, cluster_id, *args, **kwargs):
        """ Adds search criteria to an SQLAlchemy query based on the service's (self) search configuration.
        """
        _input = self.request.input

        # No pagination requested at all
        if not _input.get('paginate'):
            return search_func(session, cluster_id, *args)

        try:
            cur_page = int(_input.get('cur_page', 1))
        except(ValueError, TypeError):
            cur_page = 1

        try:
            page_size = min(int(_input.get('page_size', _default_page_size)), _max_page_size)
        except(ValueError, TypeError):
            page_size = _default_page_size

        # We need to substract 1 because externally our API exposes human-readable numbers,
        # i.e. starting from 1, not 0, but internally the database needs 0-based slices.
        if cur_page > 0:
            cur_page -= 1

        kwargs = {
            'cur_page': cur_page,
            'page_size': page_size,
            'filter_by': self._filter_by,
        }

        query = self.request.input.get('query')
        if query:
            query = query.strip().split()
            if query:
                kwargs['query'] = query

        result = search_func(session, cluster_id, *args, **kwargs)

        num_pages, rest = divmod(result.total, page_size)

        # Apparently there are some results in rest that did not fit a full page
        if rest:
            num_pages += 1

        result.num_pages = num_pages
        result.cur_page = cur_page + 1 # Adding 1 because, again, the external API is 1-indexed
        result.prev_page = result.cur_page - 1 if result.cur_page > 1 else None
        result.next_page = result.cur_page + 1 if result.cur_page <= result.total else None
        result.has_prev_page = result.prev_page >= 1
        result.has_next_page = result.next_page <= result.num_pages
        result.page_size = page_size

        self._search_tool.set_output_meta(result)

        return result

# ################################################################################################################################

class AdminSIO(object):
    namespace = zato_namespace

# ################################################################################################################################

class GetListAdminSIO(object):
    namespace = zato_namespace
    input_optional = ('cur_page', 'paginate', 'query')

# ################################################################################################################################

class Ping(AdminService):
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
    class SimpleIO(Ping.SimpleIO):
        response_elem = 'zato_ping2_response'

# ################################################################################################################################

class ChangePasswordBase(AdminService):
    """ A base class for handling the changing of any of the ODB passwords.
    """
    # Subclasses may wish to set it to False to special-case what they need to deal with
    password_required = True

    class SimpleIO(AdminSIO):
        input_required = ('id', 'password1', 'password2')

    def _handle(self, class_, auth_func, action, name_func=None, msg_type=MESSAGE_TYPE.TO_PARALLEL_ALL,
                *args, **kwargs):

        with closing(self.odb.session()) as session:
            password1 = self.request.input.get('password1', '')
            password2 = self.request.input.get('password2', '')

            try:
                if self.password_required:
                    if not password1:
                        raise Exception('Password must not be empty')

                    if not password2:
                        raise Exception('Password must be repeated')

                if password1 != password2:
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
                    self.request.input.password = auth.password
                    self.request.input.salt = kwargs.get('salt')

                    for attr in kwargs.get('publish_instance_attrs', []):
                        self.request.input[attr] = getattr(auth, attr, ZATO_NONE)

                    self.broker_client.publish(self.request.input, msg_type=msg_type)

            except Exception, e:
                msg = 'Could not update the password, e:[{}]'.format(format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

# ################################################################################################################################
