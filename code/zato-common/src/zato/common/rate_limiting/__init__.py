# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from logging import getLogger

# gevent
from gevent.lock import RLock

# netaddr
from netaddr import IPNetwork

# SQLAlchemy
from sqlalchemy import and_

# Zato
from zato.common.rate_limiting.common import Const, DefinitionItem, ObjectInfo
from zato.common.rate_limiting.limiter import Approximate, Exact, RateLimitStateDelete, RateLimitStateTable

# Python 2/3 compatibility
from past.builtins import unicode

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:

    # stdlib
    from typing import Callable

    # Zato
    from zato.common.rate_limiting.limiter import BaseLimiter
    from zato.distlock import LockManager

    # For pyflakes
    BaseLimiter = BaseLimiter
    Callable = Callable
    LockManager = LockManager

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class DefinitionParser(object):
    """ Parser for user-provided rate limiting definitions.
    """

    @staticmethod
    def get_lines(definition, object_id, object_type, object_name, parse_only=False):
        # type: (unicode, int, unicode, unicode, bool) -> list

        if not parse_only:
            out = []

        definition = definition if isinstance(definition, unicode) else definition.decode('utf8')

        for idx, orig_line in enumerate(definition.splitlines(), 1): # type: int, unicode
            line = orig_line.strip()

            if (not line) or line.startswith('#'):
                continue

            line = line.split('=')
            if len(line) != 2:
                raise ValueError('Invalid definition line `{}`; (idx:{})'.format(orig_line, idx))
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

            # In parse-only mode we do not build any actual output
            if parse_only:
                continue

            item = DefinitionItem()
            item.config_line = idx
            item.from_ = from_
            item.rate = rate
            item.unit = unit
            item.object_id = object_id
            item.object_type = object_type
            item.object_name = object_name

            out.append(item)

        if not parse_only:
            return out

# ################################################################################################################################

    @staticmethod
    def check_definition(definition):
        # type: (unicode)
        DefinitionParser.get_lines(definition.strip(), None, None, None, True)

# ################################################################################################################################

    @staticmethod
    def check_definition_from_input(input_data):
        # type: (dict)
        rate_limit_def = input_data.get('rate_limit_def') or ''
        if rate_limit_def:
            DefinitionParser.check_definition(rate_limit_def)

# ################################################################################################################################

    def parse(self, definition, object_id, object_type, object_name):
        # type: (unicode, int, unicode, unicode) -> list
        return DefinitionParser.get_lines(definition.strip(), object_id, object_type, object_name)

# ################################################################################################################################
# ################################################################################################################################

class RateLimiting(object):
    """ Main API for the management of rate limiting functionality.
    """
    __slots__ = 'parser', 'config_store', 'lock', 'sql_session_func', 'global_lock_func', 'cluster_id'

    def __init__(self):
        self.parser = DefinitionParser() # type: DefinitionParser
        self.config_store = {}           # type: dict
        self.lock = RLock()
        self.global_lock_func = None     # type: LockManager
        self.sql_session_func = None     # type: Callable
        self.cluster_id = None           # type: int

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

        object_id = object_dict['id']
        object_type = object_dict['type_']
        object_name = object_dict['name']

        info = ObjectInfo()
        info.id = object_id
        info.type_ = object_type
        info.name = object_name

        parsed = self.parser.parse(definition or '', object_id, object_type, object_name)

        if parsed:
            def_first = parsed[0]
            has_from_any = def_first.from_ == Const.from_any
        else:
            has_from_any = False

        config = Exact(self.cluster_id, self.sql_session_func) if is_exact else Approximate(self.cluster_id) # type: BaseLimiter
        config.is_active = object_dict['is_active']
        config.is_exact = is_exact
        config.api = self
        config.object_info = info
        config.definition = parsed
        config.parent_type = object_dict['parent_type']
        config.parent_name = object_dict['parent_name']

        if has_from_any:

            config.has_from_any = has_from_any
            config.from_any_rate = def_first.rate
            config.from_any_unit = def_first.unit

            config.from_any_object_id = object_id
            config.from_any_object_type = object_type
            config.from_any_object_name = object_name

        return config

# ################################################################################################################################

    def create(self, object_dict, definition, is_exact):
        # type: (dict, unicode, bool)
        config = self._create_config(object_dict, definition, is_exact)
        self.config_store[config.get_config_key()] = config

# ################################################################################################################################

    def check_limit(self, cid, object_type, object_name, from_, needs_warn=True):
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
            if needs_warn:
                logger.warn('No such rate limiting object `%s` (%s)', object_name, object_type)

# ################################################################################################################################

    def _delete_from_odb(self, object_type, object_id):
        with closing(self.sql_session_func()) as session:
            session.execute(RateLimitStateDelete().where(and_(
                RateLimitStateTable.c.object_type==object_type,
                RateLimitStateTable.c.object_id==object_id,
            )))
            session.commit()

# ################################################################################################################################

    def _delete(self, object_type, object_name, remove_parent):
        """ Deletes configuration for input data, optionally deleting references to it from all objects that depended on it.
        Must be called with self.lock held.
        """
        # type: (unicode, unicode, bool)

        config_key = self._get_config_key(object_type, object_name)
        limiter = self.config_store[config_key] # type: BaseLimiter
        del self.config_store[config_key]

        if limiter.is_exact:
            self._delete_from_odb(object_type, limiter.object_info.id)

        if remove_parent:
            self._set_new_parent(object_type, object_name, None, None)

# ################################################################################################################################

    def _set_new_parent(self, parent_type, old_parent_name, new_parent_type, new_parent_name):
        """ Sets new parent for all configuration entries matching the old one. Must be called with self.lock held.
        """
        # type: (unicode, unicode, unicode, unicode)

        for child_config in self.config_store.values(): # type: BaseLimiter
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

            # .. in case it was a rename ..
            if old_config.object_info.name != new_config.object_info.name:

                # .. make all child objects depend on the new name, in case it changed
                self._set_new_parent(object_type, old_object_name, new_config.object_info.type_, new_config.object_info.name)

            # First, delete the old configuration, but do not delete any objects that depended on it
            # because we are just editing the former, not deleting it altogether.
            self._delete(object_type, old_object_name, False)

            # Now, create a new key
            self.config_store[new_config.get_config_key()] = new_config

# ################################################################################################################################

    def delete(self, object_type, object_name):
        """ Deletes configuration for input object and clears out parent references to it.
        """
        # type: (unicode, unicode)
        with self.lock:
            self._delete(object_type, object_name, True)

# ################################################################################################################################

    def _get_config(self, object_type, object_name):
        """ Returns configuration for the input object, assumming we have it at all.
        """
        # type: (unicode, unicode) -> BaseLimiter
        config_key = self._get_config_key(object_type, object_name)
        return self.config_store.get(config_key)

# ################################################################################################################################

    def get_config(self, object_type, object_name):
        # type: (unicode, unicode) -> BaseLimiter
        with self.lock:
            return self._get_config(object_type, object_name)

# ################################################################################################################################

    def has_config(self, object_type, object_name):
        # type: (unicode, unicode) -> bool
        with self.lock:
            return bool(self._get_config(object_type, object_name))

# ################################################################################################################################

    def cleanup(self):
        """ Invoked periodically by the scheduler - goes through all configuration elements and cleans up
        all time periods that are no longer needed.
        """
        for config in self.config_store.values(): # type: BaseLimiter
            config.cleanup()

# ################################################################################################################################
# ################################################################################################################################
