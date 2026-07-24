# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# redis
from redis import Redis

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# All rule engine stream keys carry this per-environment prefix so that multiple Zato environments
# sharing one Redis never consume each other's messages. The server-side listener reads the same variable.
_stream_prefix = os.environ.get('Zato_Rule_Engine_Stream_Prefix', 'zato:rule-engine')

class ModuleCtx:
    Changes_Stream = f'{_stream_prefix}:stream:changes'
    Max_Stream_Len = 10_000

# ################################################################################################################################

# What kind of write one change message announces - consumers only ever evict on them,
# so an unknown kind from a newer producer still evicts correctly.
Change_Definition_Created  = 'definition-created'
Change_Definition_Archived = 'definition-archived'
Change_Version_Created     = 'version-created'
Change_Version_Published   = 'version-published'
Change_Version_Restored    = 'version-restored'

# ################################################################################################################################
# ################################################################################################################################

class ChangePublisher:
    """ Announces rule engine writes on a Redis stream, one message per committed change.

    Server processes consume the stream and evict the RAM entries the change invalidates,
    which is what keeps their caches correct with no TTL and no polling anywhere.
    A failed announcement is logged loudly but never breaks the write it follows.
    """

    def __init__(self, redis_conn:'Redis | None'=None) -> 'None':
        if redis_conn:
            self.redis = redis_conn
        else:
            redis_host = os.environ.get('Zato_Rule_Engine_Redis_Host', 'localhost')
            redis_port = int(os.environ.get('Zato_Rule_Engine_Redis_Port', '6379'))
            redis_password = os.environ.get('Zato_Rule_Engine_Redis_Password', None)
            self.redis = Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True,
            )

# ################################################################################################################################

    def publish(self, kind:'str', definition_id:'int', name:'str', object_type:'str') -> 'None':
        """ Puts one committed change on the stream. The database write already happened,
        so a Redis failure only delays cache eviction and must never raise into the caller.
        """
        try:
            _ = self.redis.xadd(ModuleCtx.Changes_Stream, {
                'kind': kind,
                'definition_id': definition_id,
                'name': name,
                'object_type': object_type,
            }, maxlen=ModuleCtx.Max_Stream_Len)
        except Exception as exc:
            logger.warning('Rule engine change `%s` for `%s` (id=%s) could not be announced: %s',
                kind, name, definition_id, exc)

# ################################################################################################################################
# ################################################################################################################################
