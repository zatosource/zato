# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from datetime import datetime, timedelta
from zato.common.odb.model import KVData as KVDataModel
from zato.common.typing_ import dataclass, optional

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.odb.api import SessionWrapper

    SessionWrapper = SessionWrapper

# ################################################################################################################################
# ################################################################################################################################

utcnow = datetime.utcnow
default_expiry_time = datetime(year=2345, month=12, day=31)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class KeyCtx:
    key: str
    value: optional[str] = None
    data_type: str = 'string'
    creation_time: datetime = None
    expiry_time: optional[datetime] = None

# ################################################################################################################################
# ################################################################################################################################

class KVDataAPI:

    def __init__(self, cluster_id, session_wrapper):
        # type: (int, SessionWrapper) -> None
        self.cluster_id = cluster_id
        self.session_wrapper = session_wrapper

# ################################################################################################################################

    def _get_session(self):
        return self.session_wrapper.session()

# ################################################################################################################################

    def get(self, key):
        # type: (str) -> optional[KeyCtx]

        # We always operate on bytes
        key = key.encode('utf8') if isinstance(key, str) else key

        # Get a new SQL session ..
        session = self._get_session()

        # .. prepare the query ..
        query = session.query(KVDataModel).\
            filter(KVDataModel.cluster_id==self.cluster_id).\
            filter(KVDataModel.key==key).\
            filter(KVDataModel.expiry_time > utcnow())

        # .. run it ..
        result = query.first() # type: KVDataModel

        # .. convert the result to a business object ..
        if result:
            ctx = KeyCtx()
            ctx.key = result.key.decode('utf8')
            ctx.value = result.value
            ctx.data_type = result.data_type
            ctx.creation_time = result.creation_time
            ctx.expiry_time = result.expiry_time

            if ctx.value:
                ctx.value = ctx.value.decode('utf8')

            return ctx

# ################################################################################################################################

    def set(self, key, value, expiry_sec=None, expiry_time=None):
        # type: (str, str, int, datetime)
        ctx = KeyCtx()
        ctx.key = key
        ctx.value = value
        ctx.expiry_time = expiry_time if expiry_time else utcnow() + timedelta(seconds=expiry_sec)

        self.set_with_ctx(ctx)

# ################################################################################################################################

    def set_with_ctx(self, ctx, data_type='string'):
        # type: (KeyCtx, str) -> None

        key = ctx.key.encode('utf8') if isinstance(ctx.key, str) else ctx.key
        value = ctx.value.encode('utf8') if isinstance(ctx.value, str) else ctx.value

        item = KVDataModel()
        item.cluster_id = self.cluster_id
        item.key = key
        item.value = value
        item.creation_time = ctx.creation_time or utcnow()
        item.expiry_time = ctx.expiry_time or default_expiry_time

        session = self._get_session()
        session.add(item)
        session.commit()

# ################################################################################################################################
# ################################################################################################################################
