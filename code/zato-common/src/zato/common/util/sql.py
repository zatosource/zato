# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import loads
from logging import getLogger

# Bunch
from bunch import bunchify

# gevent
from gevent import sleep

# SQLAlchemy
from sqlalchemy.exc import InternalError as SAInternalError

# Zato
from zato.common import GENERIC, SEARCH
from zato.common.util.search import SearchResults

# ################################################################################################################################

logger_zato = getLogger('zato')
logger_pubsub = getLogger('zato_pubsub')

# ################################################################################################################################

_default_page_size = SEARCH.ZATO.DEFAULTS.PAGE_SIZE.value
_max_page_size = _default_page_size * 5

# In MySQL, 1213 = 'Deadlock found when trying to get lock; try restarting transaction'
# but the underlying PyMySQL library returns only a string rather than an integer code.
_deadlock_code = 'Deadlock found when trying to get lock'

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
        'where': kwargs.get('where')
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
    is_ok = False
    attempts = 0

    while not is_ok:
        attempts = 1

        try:
            # Call the SQL function that will possibly result in a deadlock
            func(*args, **kwargs)

            # This will return only if there is no exception in calling the SQL function
            return True

        # Catch deadlocks - it may happen because both this function and delivery tasks update the same tables
        except SAInternalError as e:
            if _deadlock_code not in e.message:
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

class ElemsWithOpaqueMaker(object):
    def __init__(self, elems):
        self.elems = elems

    @staticmethod
    def _set_opaque(elem):
        opaque = elem.get(GENERIC.ATTR_NAME)
        opaque = loads(opaque) if opaque else {}
        elem.update(opaque)

# ################################################################################################################################

    @staticmethod
    def process_config_dict(config):
        ElemsWithOpaqueMaker._set_opaque(config)

# ################################################################################################################################

    def _process_elems(self, out, elems):
        for elem in elems:
            if hasattr(elem, '_sa_class_manager'):
                data = {}
                for (name, _) in elem._sa_class_manager._all_sqla_attributes():
                    data[name] = getattr(elem, name)
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

def elems_with_opaque(elems):
    """ Turns a list of SQLAlchemy elements into a list of Bunch instances,
    each possibly with its opaque elements already extracted to the level of each Bunch.
    """
    return ElemsWithOpaqueMaker(elems).get()

# ################################################################################################################################

