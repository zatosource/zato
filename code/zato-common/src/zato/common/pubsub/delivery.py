# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One round of delivery attempts under a retry policy - what the queue of an outgoing connection and the push delivery
# of a published message both run.

# stdlib
from logging import getLogger
from random import uniform

# gevent
from gevent import sleep

# Zato
from zato.common.api import PubSub
from zato.common.util.retry import get_first_sleep_time, get_next_sleep_time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, callnone
    from zato.common.util.retry import RetryPolicy

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_round_wait = PubSub.Delivery.Retry_Round_Wait

# Why a round was stopped between two of its attempts
Interrupt_Paused  = 'paused'
Interrupt_Expired = 'expired'

_percent = 100

# ################################################################################################################################
# ################################################################################################################################

class DeliveryExhausted(Exception):
    """ Raised when a round of delivery ran out of attempts.
    """

    def __init__(self, error:'str', attempts:'int', error_class:'str') -> 'None':
        super().__init__(error)
        self.error = error
        self.attempts = attempts

        # The class name of the exception the last attempt raised.
        self.error_class = error_class

# ################################################################################################################################
# ################################################################################################################################

class SendRejected(Exception):
    """ Raised by an attempt when the endpoint turned the message down. A permanent refusal is the endpoint saying
    the message itself is wrong, so no further attempt is made with it.
    """

    def __init__(self, error:'str', response:'any_'=None, *, is_permanent:'bool'=False) -> 'None':
        super().__init__(error)
        self.error = error
        self.response = response
        self.is_permanent = is_permanent

# ################################################################################################################################
# ################################################################################################################################

class DeliveryInterrupted(Exception):
    """ Raised when a round of delivery was stopped between two of its attempts.
    """

    def __init__(self, reason:'str', attempts:'int') -> 'None':
        super().__init__(reason)
        self.reason = reason
        self.attempts = attempts

# ################################################################################################################################
# ################################################################################################################################

def get_jittered_sleep_time(policy:'RetryPolicy', sleep_time:'int') -> 'float':
    """ A sleep with the policy's jitter added, which is no time at all for a policy without jitter.
    """
    jitter = sleep_time * policy.jitter_percent / _percent
    out = sleep_time + uniform(0, jitter)

    return out

# ################################################################################################################################

def deliver_with_policy(
    policy:'RetryPolicy',
    attempts_made:'int',
    cid:'str',
    conn_name:'str',
    attempt:'callable_',
    should_continue:'callnone'=None,
    ) -> 'None':
    """ Runs attempts until one is accepted or the policy allows no more, counting from the attempts already made.
    A should_continue callable is asked before and after each wait and a reason it answers with stops the round.
    """
    attempts_allowed = 1 + policy.max_retries

    total_sleep_time = 0
    current_sleep_time = get_first_sleep_time(policy)

    def check_should_continue() -> 'None':
        if should_continue:
            if reason := should_continue():
                logger.info('Queue delivery round stopped cid=%s, conn=%s, attempts=%s, reason=%s',
                    cid, conn_name, attempts_made, reason)
                raise DeliveryInterrupted(reason, attempts_made)

    while True:

        # Every attempt after a failed one is preceded by a wait ..
        if attempts_made:

            # .. unless the round is to stop here ..
            check_should_continue()

            sleep_time = get_jittered_sleep_time(policy, current_sleep_time)
            sleep(sleep_time)

            total_sleep_time += current_sleep_time
            current_sleep_time = get_next_sleep_time(policy, current_sleep_time, total_sleep_time)

            # .. or the wait was what made it stop, e.g. the message expired during it.
            check_should_continue()

        try:
            attempt()
            return

        # An attempt that found its connection not taking anything at all stops the round rather than failing it,
        # the message stays for a round that runs once the connection does
        except DeliveryInterrupted:
            raise

        except Exception as e:
            attempts_made += 1

            # The endpoint said the message itself is wrong, which no further attempt can get past ..
            if isinstance(e, SendRejected):
                if e.is_permanent:
                    logger.info('Queue delivery round over cid=%s, conn=%s, attempts=%s, refused=%s',
                        cid, conn_name, attempts_made, e)
                    raise DeliveryExhausted(str(e), attempts_made, e.__class__.__name__) from e

            # .. both the attempt count and the total wait are caps
            has_attempts_left = attempts_made < attempts_allowed
            has_time_left = total_sleep_time < policy.backoff_threshold

            if has_attempts_left and has_time_left:
                logger.info('Queue delivery retry cid=%s, conn=%s, attempt=%s of %s, reason=%s',
                    cid, conn_name, attempts_made, attempts_allowed, e)
                continue

            logger.info('Queue delivery round over cid=%s, conn=%s, attempts=%s, reason=%s', cid, conn_name, attempts_made, e)
            raise DeliveryExhausted(str(e), attempts_made, e.__class__.__name__) from e

# ################################################################################################################################

def wait_between_rounds() -> 'None':
    """ The wait between two rounds of one message.
    """
    sleep(_round_wait)

# ################################################################################################################################
# ################################################################################################################################
