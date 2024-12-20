# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rate_limiting.limiter import BaseLimiter
    from zato.common.typing_ import callable_, dict_, list_, strdict
    from zato.distlock import LockManager
    callable_ = callable_
    dict_ = dict_
    BaseLimiter = BaseLimiter
    LockManager = LockManager

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class DefinitionParser:
    """ Parser for user-provided rate limiting definitions.
    """

    @staticmethod
    def get_lines(
        definition,  # type: str
        object_id,   # type: int
        object_type, # type: str
        object_name, # type: str
        parse_only=False # type: bool
    ) -> 'list_[DefinitionItem]':

        if not parse_only:
            out = []

        definition = definition if isinstance(definition, str) else definition.decode('utf8')

        for idx, orig_line in enumerate(definition.splitlines(), 1): # type: int, str
            line = orig_line.strip()

            if (not line) or line.startswith('#'):
                continue

            line = line.split('=')
            if len(line) != 2:
                raise ValueError('Invalid definition line `{}`; (idx:{})'.format(orig_line, idx))
            from_, rate_info = line # type: str, str

            from_ = from_.strip()
            if from_ != Const.from_any:
                from_ = IPNetwork(from_)

            rate_info = rate_info.strip()

            if rate_info == Const.rate_any:
                rate = Const.rate_any
                unit = Const.Unit.day # This is arbitrary but it does not matter because there is no rate limit in effect
            else:
                rate, unit = rate_info.split('/') # type: str, str
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
    def check_definition(definition:'str') -> 'list_[DefinitionItem]':
        DefinitionParser.get_lines(definition.strip(), None, None, None, True)

# ################################################################################################################################

    @staticmethod
    def check_definition_from_input(input_data:'strdict') -> 'None':
        rate_limit_def = input_data.get('rate_limit_def') or ''
        if rate_limit_def:
            DefinitionParser.check_definition(rate_limit_def)

# ################################################################################################################################

    def parse(
        self,
        definition,  # type: str
        object_id,   # type: int
        object_type, # type: str
        object_name  # type: str
    ) -> 'list_[DefinitionItem]':
        return DefinitionParser.get_lines(definition.strip(), object_id, object_type, object_name)

# ################################################################################################################################
# ################################################################################################################################

class RateLimiting:
    """ Main API for the management of rate limiting functionality.
    """
    __slots__ = 'parser', 'config_store', 'lock', 'sql_session_func', 'global_lock_func', 'cluster_id'

    def __init__(self) -> 'None':
        self.parser = DefinitionParser() # type: DefinitionParser
        self.config_store = {}           # type: dict_[str, BaseLimiter]
        self.lock = RLock()
        self.global_lock_func = None     # type: LockManager
        self.sql_session_func = None     # type: callable_
        self.cluster_id = None           # type: int

# ################################################################################################################################

    def _get_config_key(self, object_type:'str', object_name:'str') -> 'str':
        return '{}:{}'.format(object_type, object_name)

# ################################################################################################################################

    def _get_config_by_object(self, object_type:'str', object_name:'str') -> 'BaseLimiter':
        config_key = self._get_config_key(object_type, object_name)
        return self.config_store.get(config_key)

# ################################################################################################################################

    def _create_config(self, object_dict:'strdict', definition:'str', is_exact:'bool') -> 'BaseLimiter':

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

    def create(self, object_dict:'strdict', definition:'str', is_exact:'bool') -> 'None':
        config = self._create_config(object_dict, definition, is_exact)
        self.config_store[config.get_config_key()] = config

# ################################################################################################################################

    def check_limit(self, cid:'str', object_type:'str', object_name:'str', from_:'str', needs_warn:'bool'=True) -> 'None':
        """ Checks if input object has already reached its allotted usage limit.
        """
        # type: (str, str, str, str)

        with self.lock:
            config = self._get_config_by_object(object_type, object_name)

        # It is possible that we do not have configuration for such an object,
        # in which case we will log a warning.
        if config:
            with config.lock:
                config.check_limit(cid, from_)
        else:
            if needs_warn:
                logger.warning('No such rate limiting object `%s` (%s)', object_name, object_type)

# ################################################################################################################################

    def _delete_from_odb(self, object_type:'str', object_id:'int') -> 'None':
        with closing(self.sql_session_func()) as session:
            session.execute(RateLimitStateDelete().where(and_(
                RateLimitStateTable.c.object_type==object_type,
                RateLimitStateTable.c.object_id==object_id,
            )))
            session.commit()

# ################################################################################################################################

    def _delete(self, object_type:'str', object_name:'str', remove_parent:'bool') -> 'None':
        """ Deletes configuration for input data, optionally deleting references to it from all objects that depended on it.
        Must be called with self.lock held.
        """
        config_key = self._get_config_key(object_type, object_name)
        limiter = self.config_store[config_key] # type: BaseLimiter
        del self.config_store[config_key]

        if limiter.is_exact:
            self._delete_from_odb(object_type, limiter.object_info.id)

        if remove_parent:
            self._set_new_parent(object_type, object_name, None, None)

# ################################################################################################################################

    def _set_new_parent(self, parent_type:'str', old_parent_name:'str', new_parent_type:'str', new_parent_name:'str') -> 'None':
        """ Sets new parent for all configuration entries matching the old one. Must be called with self.lock held.
        """

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

    def edit(self, object_type:'str', old_object_name:'str', object_dict:'strdict', definition:'str', is_exact:'bool') -> 'None':
        """ Changes, in place, an existing configuration entry to input data.
        """

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

    def delete(self, object_type:'str', object_name:'str') -> 'None':
        """ Deletes configuration for input object and clears out parent references to it.
        """
        with self.lock:
            self._delete(object_type, object_name, True)

# ################################################################################################################################

    def _get_config(self, object_type:'str', object_name:'str') -> 'None':
        """ Returns configuration for the input object, assumming we have it at all.
        """
        config_key = self._get_config_key(object_type, object_name)
        return self.config_store.get(config_key)

# ################################################################################################################################

    def get_config(self, object_type:'str', object_name:'str') -> 'BaseLimiter':
        with self.lock:
            return self._get_config(object_type, object_name)

# ################################################################################################################################

    def has_config(self, object_type:'str', object_name:'str') -> 'bool':
        with self.lock:
            return bool(self._get_config(object_type, object_name))

# ################################################################################################################################

    def cleanup(self) -> 'None':
        """ Invoked periodically by the scheduler - goes through all configuration elements and cleans up
        all time periods that are no longer needed.
        """
        for config in self.config_store.values(): # type: BaseLimiter
            config.cleanup()

# ################################################################################################################################
# ################################################################################################################################
