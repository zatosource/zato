# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.api import GENERIC, PUBSUB
from zato.common.json_internal import json_loads
from zato.common.pubsub import PubSubMessage
from zato.common.typing_ import cast_, optional
from zato.common.util.time_ import datetime_from_ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, callable_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_pubsub.task')

# ################################################################################################################################
# ################################################################################################################################

_zato_mime_type = PUBSUB.MIMEType.Zato

# ################################################################################################################################
# ################################################################################################################################

class Message(PubSubMessage):
    """ Wrapper for messages adding __cmp__ which uses a custom comparison protocol,
    by priority, then ext_pub_time, then pub_time.
    """

    pub_time: 'float'

    def __init__(self) -> 'None':
        super(Message, self).__init__()
        self.sub_key = ''
        self.pub_msg_id = ''
        self.pub_correl_id = ''
        self.in_reply_to = None
        self.ext_client_id = ''
        self.group_id = ''
        self.position_in_group = 0
        self.ext_pub_time = 0.0
        self.data = None
        self.mime_type = '<no-mime-type-set>'
        self.expiration = 0
        self.expiration_time = 0
        self.has_gd = False
        self.pub_time_iso = ''
        self.ext_pub_time_iso = ''
        self.expiration_time_iso = ''
        self.recv_time_iso = ''

# ################################################################################################################################

    def __lt__(self, other:'Message', max_pri:'int'=9) -> 'bool':

        self_priority = max_pri - self.priority
        other_priority = max_pri - other.priority

        # If priority is different, that is most important
        if self_priority < other_priority:
            return True

        # If we received an external publication time from a publisher,
        # this has priority over the time that we established ourselves (which is checked below)
        elif self.ext_pub_time and other.ext_pub_time:
            return cast_('float', self.ext_pub_time) < cast_('float', other.ext_pub_time)

        # Finally, we need to compare the publication times as assigned
        # by ourselves. At this point no two messages are to have the same
        # publication time because if such a condition is of concern then publishers
        # should sent their own times via ext_pub_time.
        else:
            return self.pub_time < other.pub_time

# ################################################################################################################################

    def __repr__(self) -> 'str':
        return '<Msg d:{} pub:{!r} pri:{} id:{} extpub:{!r} gd:{}>'.format(
            self.data, self.pub_time, self.priority, self.pub_msg_id, self.ext_pub_time, self.has_gd)

# ################################################################################################################################

    def add_iso_times(self) -> 'None':
        """ Sets additional attributes for datetime in ISO-8601.
        """
        self.pub_time_iso = cast_('str', datetime_from_ms(self.pub_time * 1000))

        if self.ext_pub_time:
            self.ext_pub_time_iso = cast_('str', datetime_from_ms(cast_('float', self.ext_pub_time) * 1000))

        if self.expiration_time:
            self.expiration_time_iso = cast_('str', datetime_from_ms(self.expiration_time * 1000))

        if self.recv_time:
            self.recv_time_iso = cast_('str', datetime_from_ms(self.recv_time * 1000))

# ################################################################################################################################

class GDMessage(Message):
    """ A guaranteed delivery message initialized from SQL data.
    """
    is_gd_message = True

    def __init__(self,
            sub_key,    # type: str
            topic_name, # type: str
            msg,        # type: anydict
            _gen_attr=GENERIC.ATTR_NAME,    # type: str
            _loads=json_loads,              # type: callable_
            _zato_mime_type=_zato_mime_type # type: str
        ) -> 'None':

        # logger.info('Building task message (gd) from `%s`', msg)

        super(GDMessage, self).__init__()
        self.endp_msg_queue_id = msg['endp_msg_queue_id']
        self.sub_key = sub_key
        self.pub_msg_id = msg['pub_msg_id']
        self.pub_correl_id = msg['pub_correl_id']
        self.in_reply_to = msg['in_reply_to']
        self.ext_client_id = msg['ext_client_id']
        self.group_id = msg['group_id']
        self.position_in_group = msg['position_in_group']
        self.pub_time = msg['pub_time']
        self.ext_pub_time = msg['ext_pub_time']
        self.mime_type = msg['mime_type']
        self.priority = msg['priority']
        self.expiration = msg['expiration']
        self.expiration_time = msg['expiration_time']
        self.has_gd = True
        self.topic_name = topic_name
        self.size = msg['size']
        self.published_by_id = msg['published_by_id']
        self.sub_pattern_matched = msg['sub_pattern_matched']
        self.user_ctx = msg['user_ctx']
        self.zato_ctx = msg['zato_ctx']

        # Assign data but note that we may still need to modify it
        # depending on what zato_ctx contains.
        self.data = msg['data']

        # This is optional ..
        if self.zato_ctx:
            self.zato_ctx = _loads(self.zato_ctx) # type: anydict # type: ignore[no-redef]

        if self.zato_ctx.get('zato_mime_type') == _zato_mime_type:
            self.data = json_loads(self.data)

        # Load opaque attributes, if any were provided on input
        opaque = getattr(msg, _gen_attr, None)
        if opaque:
            opaque = _loads(opaque)
            for key, value in opaque.items():
                setattr(self, key, value)

        # Add times in ISO-8601 for external subscribers
        self.add_iso_times()

        # logger.info('Built task message (gd) from `%s`', self.pub_msg_id)

# ################################################################################################################################

class NonGDMessage(Message):
    """ A non-guaranteed delivery message initialized from a Python dict.
    """
    is_gd_message = False

    def __init__(self,
            sub_key,     # type: str
            server_name, # type: str
            server_pid,  # type: int
            msg,         # type: anydict
            _def_priority=PUBSUB.PRIORITY.DEFAULT,  # type: int
            _def_mime_type=PUBSUB.DEFAULT.MIME_TYPE # type: str
        ) -> 'None':

        # logger.info('Building task message (ngd) from `%s`', msg)

        super(NonGDMessage, self).__init__()
        self.sub_key = sub_key
        self.server_name = server_name
        self.server_pid = server_pid
        self.pub_msg_id = msg['pub_msg_id']
        self.pub_correl_id = msg.get('pub_correl_id', '')
        self.in_reply_to = msg.get('in_reply_to', '')
        self.ext_client_id = msg.get('ext_client_id', '')
        self.group_id = msg.get('group_id', '')
        self.position_in_group = msg.get('position_in_group', 0)
        self.pub_time = msg['pub_time']
        self.ext_pub_time = msg.get('ext_pub_time')
        self.data = msg['data']
        self.mime_type = msg.get('mime_type') or _def_mime_type
        self.priority = msg.get('priority') or _def_priority
        self.expiration = msg['expiration']
        self.expiration_time = msg['expiration_time']
        self.has_gd = False
        self.topic_name = msg['topic_name']
        self.size = msg['size']
        self.published_by_id = msg['published_by_id']
        self.pub_pattern_matched = msg['pub_pattern_matched']
        self.reply_to_sk = msg['reply_to_sk']
        self.deliver_to_sk = msg['deliver_to_sk']
        self.user_ctx = msg.get('user_ctx')
        self.zato_ctx = msg.get('zato_ctx', {})

        # msg.sub_pattern_matched is a shared dictionary of patterns for each subscriber - we .pop from it
        # so as not to keep this dictionary's contents for no particular reason. Since there can be only
        # one delivery task for each sub_key, we can .pop rightaway.
        sub_pattern_matched = msg['sub_pattern_matched'] # type: anydict
        self.sub_pattern_matched = sub_pattern_matched.pop(self.sub_key)

        # Add times in ISO-8601 for external subscribers
        self.add_iso_times()

        # logger.info('Built task message (ngd) `%s`', self.to_dict(add_id_attrs=True))

# ################################################################################################################################
# ################################################################################################################################

msgnone = optional['Message']

# ################################################################################################################################
# ################################################################################################################################
