# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime
from logging import getLogger

# gevent
from gevent.lock import RLock

# netaddr
from netaddr import IPAddress, IPNetwork

# Zato
from zato.common.rate_limiting.common import Const, DefinitionItem, FromIPNotAllowed, ObjectInfo, RateLimitReached
from zato.common.rate_limiting.limiter import Approximate, Exact

# Python 2/3 compatibility
from future.utils import iterkeys
from past.builtins import unicode

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:

    # Zato
    from zato.common.rate_limiting.limiter import BaseLimiter

    # For pyflakes
    BaseLimiter = BaseLimiter

# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class DefinitionParser(object):
    """ Parser for user-provided rate limiting definitions.
    """
    def _get_lines(self, definition):
        # type: (unicode) -> list

        out = []
        definition = definition if isinstance(definition, unicode) else definition.decode('utf8')

        for idx, line in enumerate(definition.splitlines(), 1): # type: int, unicode
            line = line.strip()

            if (not line) or line.startswith('#'):
                continue

            line = line.split('=')
            from_, rate_info = line # type: unicode, unicode

            from_ = from_.strip()
            if from_ != Const.from_any:
                from_ = IPNetwork(from_)

            rate_info = rate_info.strip()

            if rate_info == Const.rate_any:
                rate = Const.rate_any
                unit = Const.Unit.day # This is arbitrary but it does not matter because there is no rate limit in effect
            else:
                rate, unit = rate_info.split('/') # type: unicode, unicode
                rate = int(rate.strip())
                unit = unit.strip()

            all_units = Const.all_units()
            if unit not in all_units:
                raise ValueError('Unit `{}` is not one of `{}`'.format(unit, all_units))

            item = DefinitionItem()
            item.config_line = idx
            item.from_ = from_
            item.rate = rate
            item.unit = unit

            out.append(item)

        return out

    def parse(self, definition):
        # type: (unicode) -> list
        return self._get_lines(definition.strip())

# ################################################################################################################################
# ################################################################################################################################

class RateLimiting(object):
    """ Main API for the management of rate limiting functionality.
    """
    __slots__ = 'parser', 'config_store', 'lock'

    def __init__(self):
        self.parser = DefinitionParser()
        self.config_store = {}
        self.lock = RLock()

# ################################################################################################################################

    def _get_config_key(self, object_type, object_name):
        # type: (unicode, unicode) -> unicode
        return '{}:{}'.format(object_type, object_name)

# ################################################################################################################################

    def _get_config_by_object(self, object_type, object_name):
        # type: (unicode, unicode) -> BaseLimiter
        return self.config_store.get(self._get_config_key(object_type, object_name))

# ################################################################################################################################

    def _create_config(self, object_dict, definition, is_exact):
        # type: (dict, unicode, bool) -> BaseLimiter

        info = ObjectInfo()
        info.type_ = object_dict['type_']
        info.id = object_dict['id']
        info.name = object_dict['name']

        parsed = self.parser.parse(definition)
        def_first = parsed[0]
        has_from_any = def_first.from_ == Const.from_any

        config = Exact() if is_exact else Approximate()
        config.api = self
        config.object_info = info
        config.definition = parsed
        config.parent_type = object_dict['parent_type']
        config.parent_name = object_dict['parent_name']

        if has_from_any:
            config.has_from_any = has_from_any
            config.from_any_rate = def_first.rate
            config.from_any_unit = def_first.unit

        return config

# ################################################################################################################################

    def create(self, object_dict, definition, is_exact):
        # type: (dict, unicode, bool)
        config = self._create_config(object_dict, definition, is_exact)
        self.config_store[config.get_config_key()] = config

# ################################################################################################################################

    def check_limit(self, cid, object_type, object_name, from_):
        """ Checks if input object has already reached its allotted usage limit.
        """
        # type: (unicode, unicode, unicode, unicode)

        with self.lock:
            config = self._get_config_by_object(object_type, object_name)

        # It is possible that we do not have configuration for such an object,
        # in which case we will log a warning.
        if config:
            with config.lock:
                config.check_limit(cid, from_)
        else:
            logger.warn('No such rate limiting object `%s` (%s)', object_name, object_type)

# ################################################################################################################################

    def _delete(self, object_type, object_name, remove_parent):
        """ Deletes configuration for input data, optionally deleting references to it from all objects that depended on it.
        Must be called with self.lock held.
        """
        # type: (unicode, unicode, bool)

        config_key = self._get_config_key(object_type, object_name)
        del self.config_store[config_key]

        if remove_parent:
            self._set_new_parent(object_type, object_name, None, None)

# ################################################################################################################################

    def _set_new_parent(self, parent_type, old_parent_name, new_parent_type, new_parent_name):
        """ Sets new parent for all configuration entries matching the old one. Must be called with self.lock held.
        """
        # type: (unicode, unicode, unicode, unicode)

        for child_config in self.config_store.values(): # type: RateLimiterApproximate
            object_info = child_config.object_info

            # This is our own config
            if object_info.type_ == parent_type and object_info.name == old_parent_name:
                continue

            # This object has a parent, possibly it is our very configuration
            if child_config.has_parent:

                # Yes, this is our config ..
                if child_config.parent_type == parent_type and child_config.parent_name == old_parent_name:

                    # We typically want to change the parent's name but it is possible
                    # that both type and name will be None (in case we are removing a parent from a child object)
                    # which is why both are set here.
                    child_config.parent_type = new_parent_type
                    child_config.parent_name = new_parent_name

# ################################################################################################################################

    def edit(self, object_type, old_object_name, object_dict, definition, is_exact):
        """ Changes, in place, an existing configuration entry to input data.
        """
        # type: (unicode, unicode, dict, unicode, bool)

        # Note the whole of this operation is under self.lock to make sure the update is atomic
        # from our callers' perspective.
        with self.lock:
            old_config = self._get_config_by_object(object_type, old_object_name)

            if not old_config:
                raise ValueError('Rate limiting object not found `{}` ({})'.format(old_object_name, object_type))

            # Just to be sure we are doing the right thing, compare object types, old and new
            if object_type != old_config.object_info.type_:
                raise ValueError('Unexpected object_type, old:`{}`, new:`{}` ({}) ({})'.format(
                    old_config.object_info.type_, object_type, old_object_name, object_dict))

            # Now, create a new config object ..
            new_config = self._create_config(object_dict, definition, is_exact)

            # .. move existing rate limiting data from the old config object to the new one
            new_config.rewrite_rate_data(old_config)

            # .. in case it was a rename ..
            if old_config.object_info.name != new_config.object_info.name:

                # .. make all child objects depend on the new name, in case it changed
                self._set_new_parent(object_type, old_object_name, new_config.object_info.type_, new_config.object_info.name)

                # First, delete the old configuration, but do not delete any objects that depended on it
                # because we are just editing the former, not deleting it altogether.
                self._delete(object_type, old_object_name, False)

                #
                self.config_store[new_config.get_config_key()] = new_config

# ################################################################################################################################

    def delete(self, object_type, object_name):
        """ Deletes configuration for input object and clears out parent references to it.
        """
        with self.lock:
            self._delete(object_type, object_name, True)

# ################################################################################################################################

    def cleanup(self):
        """ Invoked periodically by the scheduler - goes through all configuration elements and cleans up
        all time periods that are no longer needed.
        """
        for config in self.config_store.values(): # type: RateLimiterApproximate
            config.cleanup()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # SQLAlchemy
    from sqlalchemy import create_engine, orm

    # Zato
    from zato.common.odb.model import RateLimitState

    engine = create_engine('sqlite://')
    Session = orm.sessionmaker() # noqa
    Session.configure(bind=engine)
    session = Session()

    RateLimitState.metadata.create_all(engine)

    def get_channel_config():
        return {
            'id': 333,
            'parent_type': 'sso_user',
            'parent_name': 'Joan Doe',
            'type_': 'http_soap',
            'name': 'My Endpoint',
        }

    def get_channel_definition():
        return """
        192.168.1.123 = 11/m
        127.0.0.1/32  = 1/m
        """

    def get_sec_def_config():
        return {
            'id': 222,
            'parent_type': 'sso_user',
            'parent_name': 'Joan Doe',
            'type_': 'api_key',
            'name': 'API Key',
        }

    def get_sec_def_definition():
        return """
        127.0.0.1/32  = 1/m
        """

    def get_user_config(name_suffix=''):
        return {
            'id': 111,
            'parent_type': None,
            'parent_name': None,
            'type_': 'sso_user',
            'name': 'Joan Doe' + name_suffix,
        }

    def get_user_definition(prefix=''):
        return """
        10.210.0.0/18 = 1/h
        127.0.0.1/32  = {}1/m
        * = *
        """.format(prefix)

    user_config        = get_user_config()
    user_definition    = get_user_definition()

    channel_config     = get_channel_config()
    channel_definition = get_channel_definition()

    sec_def_config     = get_sec_def_config()
    sec_def_definition = get_sec_def_definition()

    is_exact = False
    rate_limiting = RateLimiting()

    rate_limiting.create(user_config, user_definition, is_exact)
    rate_limiting.create(channel_config, channel_definition, is_exact)
    rate_limiting.create(sec_def_config, sec_def_definition, is_exact)

    cid = 123
    rate_limiting.check_limit(cid, 'http_soap', 'My Endpoint', '127.0.0.1')

    cid = 456
    rate_limiting.check_limit(cid, 'api_key', 'API Key', '127.0.0.1')
    rate_limiting.check_limit(cid, 'api_key', 'API Key', '127.0.0.1')

    #rate_limiting.edit('sso_user', 'Joan Doe', get_user_config(' 2'), get_user_definition(2), is_exact)
    #rate_limiting.edit('sso_user', 'Joan Doe 2', get_user_config(' 3'), get_user_definition(3), is_exact)

    cid = 789
    rate_limiting.check_limit(cid, 'api_key', 'API Key', '127.0.0.1')

    cid = 111
    rate_limiting.check_limit(cid, 'api_key', 'API Key', '127.0.0.1')

    #rate_limiting.delete('sso_user', 'Joan Doe 3')
    rate_limiting.cleanup()

# ################################################################################################################################
