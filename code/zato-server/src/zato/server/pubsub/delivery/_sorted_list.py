# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pyright: reportUnknownArgumentType=false, reportUnknownVariableType=false

# stdlib
from bisect import bisect_left
from logging import getLogger
from typing import Iterator as iterator

# sortedcontainers
from sortedcontainers import SortedList as _SortedList

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.server.pubsub.delivery.message import Message

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_pubsub.task')

# ################################################################################################################################
# ################################################################################################################################

class SortedList(_SortedList):
    """ A custom subclass that knows how to remove pubsub messages from SortedList instances.
    """

    def __iter__(self) -> 'iterator[Message]':
        return super().__iter__()

# ################################################################################################################################

    def __getitem__(self, idx:'any_') -> 'any_':
        return super().__getitem__(idx)

# ################################################################################################################################

    def remove_pubsub_msg(self, msg:'Message') -> 'None':
        """ Removes a pubsub message from a SortedList instance - we cannot use the regular .remove method
        because it may triggger __cmp__ per https://github.com/grantjenks/sorted_containers/issues/81.
        """

        logger.info('In remove_pubsub_msg msg:`%s`, mxs:`%s`', msg.pub_msg_id, self._maxes)
        pos = bisect_left(self._maxes, msg)

        if pos == len(self._maxes):
            raise ValueError('{0!r} not in list (1)'.format(msg))

        for _list_idx, _list_msg in enumerate(self._lists[pos]):
            if msg.pub_msg_id == _list_msg.pub_msg_id:
                idx = _list_idx
                self._delete(pos, idx)
                break
        else:
            raise ValueError('{0!r} not in list (2)'.format(msg))

# ################################################################################################################################
# ################################################################################################################################
