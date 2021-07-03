# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from itertools import chain
from logging import DEBUG, getLogger

# Bunch
from bunch import bunchify

# gevent
from gevent import sleep

# SQLAlchemy
from sqlalchemy.exc import InternalError as SAInternalError, OperationalError as SAOperationalError

# Zato
from zato.common.api import GENERIC, SEARCH
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import Base, SecurityBase
from zato.common.util.search import SearchResults

# ################################################################################################################################

logger_zato = getLogger('zato')
logger_pubsub = getLogger('zato_pubsub')

has_debug = logger_zato.isEnabledFor(DEBUG) or logger_pubsub.isEnabledFor(DEBUG)

# ################################################################################################################################

_default_page_size = SEARCH.ZATO.DEFAULTS.PAGE_SIZE
_max_page_size = _default_page_size * 5

# All exceptions that can be raised when deadlocks occur
_DeadlockException = (SAInternalError, SAOperationalError)

# In MySQL, 1213 = 'Deadlock found when trying to get lock; try restarting transaction'
# but the underlying PyMySQL library returns only a string rather than an integer code.
_deadlock_code = 'Deadlock found when trying to get lock'

_zato_opaque_skip_attrs=set(['needs_details', 'paginate', 'cur_page', 'query'])

# ################################################################################################################################

def search(search_func, config, filter_by, session=None, cluster_id=None, *args, **kwargs):
    """ Adds search criteria to an SQLAlchemy query based on current search configuration.
    """
    try:
        cur_page = int(config.get('cur_page', 1))
    except(ValueError, TypeError):
        cur_page = 1

    try:
        page_size = min(int(config.get('page_size', _default_page_size)), _max_page_size)
    except(ValueError, TypeError):
        page_size = _default_page_size

    # We need to substract 1 because externally our API exposes human-readable numbers,
    # i.e. starting from 1, not 0, but internally the database needs 0-based slices.
    if cur_page > 0:
        cur_page -= 1

    kwargs = {
        'cur_page': cur_page,
        'page_size': page_size,
        'filter_by': filter_by,
        'where': kwargs.get('where'),
        'filter_op': kwargs.get('filter_op'),
        'data_filter': kwargs.get('data_filter'),
    }

    query = config.get('query')
    if query:
        query = query.strip().split()
        if query:
            kwargs['query'] = query

    result = search_func(session, cluster_id, *args, **kwargs)

    # Fills out all the search-related information
    result.set_data(cur_page, page_size)

    return result

# ################################################################################################################################

def sql_op_with_deadlock_retry(cid, name, func, *args, **kwargs):
    cid = cid or None
    attempts = 0

    while True:
        attempts += 1

        if has_debug:
            logger_zato.info('In sql_op_with_deadlock_retry, %s %s %s %s %r %r', attempts, cid, name, func, args, kwargs)

        try:
            # Call the SQL function that will possibly result in a deadlock
            func(*args, **kwargs)

            if has_debug:
                logger_zato.info('In sql_op_with_deadlock_retry, returning True')

            # This will return only if there is no exception in calling the SQL function
            return True

        # Catch deadlocks - it may happen because both this function and delivery tasks update the same tables
        except _DeadlockException as e:

            if has_debug:
                logger_zato.warn('Caught _DeadlockException `%s` `%s`', cid, e)

            if _deadlock_code not in e.args[0]:
                raise
            else:
                if attempts % 50 == 0:
                    msg = 'Still in deadlock for `{}` after %d attempts cid:%s args:%s'.format(name)
                    logger_zato.warn(msg, attempts, cid, args)
                    logger_pubsub.warn(msg, attempts, cid, args)

                # Sleep for a while until the next attempt
                sleep(0.005)

                # Push the counter
                attempts += 1

# ################################################################################################################################
# ################################################################################################################################

class ElemsWithOpaqueMaker(object):
    def __init__(self, elems):
        self.elems = elems

# ################################################################################################################################

    @staticmethod
    def get_opaque_data(elem):
        return elem.get(GENERIC.ATTR_NAME)

    has_opaque_data = get_opaque_data

# ################################################################################################################################

    @staticmethod
    def _set_opaque(elem, drop_opaque=False):
        opaque = ElemsWithOpaqueMaker.get_opaque_data(elem)
        opaque = loads(opaque) if opaque else {}
        elem.update(opaque)

        if drop_opaque:
            del elem[GENERIC.ATTR_NAME]

# ################################################################################################################################

    @staticmethod
    def process_config_dict(config, drop_opaque=False):
        ElemsWithOpaqueMaker._set_opaque(config, drop_opaque)

# ################################################################################################################################

    def _process_elems(self, out, elems, _skip_class=(Base, list)):
        for elem in elems:
            if hasattr(elem, '_sa_class_manager'):
                data = {}
                for (name, _) in elem._sa_class_manager._all_sqla_attributes():
                    value = getattr(elem, name)
                    if name.startswith('__'):
                        continue
                    if isinstance(value, _skip_class):
                        continue
                    data[name] = value
            else:
                data = elem._asdict()
            elem = bunchify(data)
            ElemsWithOpaqueMaker._set_opaque(elem)
            out.append(elem)
        return out

# ################################################################################################################################

    def _elems_with_opaque_search(self):
        """ Resolves all opaque elements in search results.
        """
        search_result = self.elems[0]
        new_result = self._process_elems([], search_result.result)
        search_result.result = new_result
        return self.elems

# ################################################################################################################################

    def get(self):
        if isinstance(self.elems, tuple) and isinstance(self.elems[0], SearchResults):
            return self._elems_with_opaque_search()
        else:
            return self._process_elems([], self.elems)

# ################################################################################################################################
# ################################################################################################################################

def elems_with_opaque(elems):
    """ Turns a list of SQLAlchemy elements into a list of Bunch instances,
    each possibly with its opaque elements already extracted to the level of each Bunch.
    """
    return ElemsWithOpaqueMaker(elems).get()

# ################################################################################################################################

def parse_instance_opaque_attr(instance):
    opaque = getattr(instance, GENERIC.ATTR_NAME)
    opaque = loads(opaque) if opaque else None
    if not opaque:
        return {}
    ElemsWithOpaqueMaker.process_config_dict(opaque)
    return bunchify(opaque)

# ################################################################################################################################

def get_dict_with_opaque(instance, to_bunch=False):
    opaque = parse_instance_opaque_attr(instance)
    out = instance._asdict() if hasattr(instance, '_asdict') else instance.asdict()
    for k, v in opaque.items():
        out[k] = v
    return bunchify(out) if to_bunch else out

# ################################################################################################################################

def set_instance_opaque_attrs(instance, input, skip=None, only=None, _zato_skip=_zato_opaque_skip_attrs):
    """ Given an SQLAlchemy object instance and incoming SimpleIO-based input,
    populates all opaque values of that instance.
    """
    only = only or []
    instance_opaque_attrs = None
    instance_attrs = set(instance.asdict())
    input_attrs = set(input)

    if only:
        input_attrs = set([elem for elem in input_attrs if elem in only])
        instance_attrs = set([elem for elem in instance_attrs if elem not in only])

    # Any extra input attributes will be treated as opaque ones
    input_opaque_attrs = input_attrs - instance_attrs

    # Skip attributes related to pagination
    for name in chain(skip or [], _zato_skip):
        input_opaque_attrs.discard(name)

    # Prepare generic attributes for instance
    if GENERIC.ATTR_NAME in instance_attrs:
        instance_opaque_attrs = getattr(instance, GENERIC.ATTR_NAME)
        if instance_opaque_attrs:
            instance_opaque_attrs = loads(instance_opaque_attrs)
        else:
            instance_opaque_attrs = {}

        for name in input_opaque_attrs:
            instance_opaque_attrs[name] = input[name]

    # Set generic attributes for instance
    if instance_opaque_attrs is not None:
        setattr(instance, GENERIC.ATTR_NAME, dumps(instance_opaque_attrs))

# ################################################################################################################################

def get_security_by_id(session, security_id):
    return session.query(SecurityBase).\
           filter(SecurityBase.id==security_id).\
           one()

# ################################################################################################################################

def get_instance_by_id(session, model_class, id):
    return session.query(model_class).\
           filter(model_class.id==id).\
           one()

# ################################################################################################################################

def get_instance_by_name(session, model_class, type_, name):
    return session.query(model_class).\
           filter(model_class.type_==type_).\
           filter(model_class.name==name).\
           one()

# ################################################################################################################################
