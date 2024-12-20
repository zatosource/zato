# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import DEBUG, getLogger

# gevent
from gevent import sleep

# SQLAlchemy
from sqlalchemy.exc import InternalError as SAInternalError, OperationalError as SAOperationalError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_
    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

logger_zato = getLogger('zato')
logger_pubsub = getLogger('zato_pubsub')

has_debug = logger_zato.isEnabledFor(DEBUG) or logger_pubsub.isEnabledFor(DEBUG)

# ################################################################################################################################
# ################################################################################################################################

# All exceptions that can be raised when deadlocks occur
_DeadlockException = (SAInternalError, SAOperationalError)

# In MySQL, 1213 = 'Deadlock found when trying to get lock; try restarting transaction'
# but the underlying PyMySQL library returns only a string rather than an integer code.
_deadlock_code = 'Deadlock found when trying to get lock'

# ################################################################################################################################
# ################################################################################################################################

def sql_op_with_deadlock_retry(
    cid,     # type: str
    name,    # type: str
    func,    # type: callable_
    *args,   # type: any_
    **kwargs # type: any_
) -> 'any_':
    cid = cid or 'default-no-cid'
    attempts = 0

    while True:
        attempts += 1

        if has_debug:
            logger_zato.info('In sql_op_with_deadlock_retry, %s %s %s %s %r %r',
                attempts, cid, name, func, args, kwargs)

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
                logger_zato.warning('Caught _DeadlockException `%s` `%s`', cid, e)

            if _deadlock_code not in e.args[0]:
                raise
            else:
                if attempts % 50 == 0:
                    msg = 'Still in deadlock for `{}` after %d attempts cid:%s args:%s'.format(name)
                    logger_zato.warning(msg, attempts, cid, args)
                    logger_pubsub.warning(msg, attempts, cid, args)

                # Sleep for a while until the next attempt
                sleep(0.005)

                # Push the counter
                attempts += 1

# ################################################################################################################################

def sql_query_with_retry(query:'any_', query_name:'str', *args:'any_') -> 'None':
    """ Keeps repeating a given SQL query until it succeeds.
    """
    idx = 0
    is_ok = False

    while not is_ok:

        idx += 1

        if has_debug:
            logger_zato.info(f'{query_name} -> is_ok.{idx}:`{is_ok}`')

        is_ok = query(*args)

        if has_debug:
            logger_zato.info(f'{query_name} -> is_ok.{idx}:`{is_ok}`')

# ################################################################################################################################
# ################################################################################################################################
