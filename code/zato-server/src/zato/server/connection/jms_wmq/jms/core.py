# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

"""
   Copyright 2006-2008 SpringSource (http://springsource.com), All Rights Reserved

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

# stdlib
import logging
import locale
from base64 import b64encode
from binascii import hexlify
from string import Template
from io import StringIO

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import basestring, unicode
from zato.common.py23_ import pickle_dumps

# Zato
from zato.server.connection.jms_wmq.jms import DEFAULT_DELIVERY_MODE, BaseException

# ################################################################################################################################

logger_zato = logging.getLogger('zato')

# ################################################################################################################################

# These attributes have special meaning to connection factories.
reserved_attributes = {
    'text', 'jms_correlation_id', 'jms_delivery_mode', 'jms_destination', 'jms_expiration',
    'jms_message_id', 'jms_priority', 'jms_redelivered', 'jms_reply_to', 'jms_timestamp', 'max_chars_printed',
    'JMS_IBM_Report_Exception', 'JMS_IBM_Report_Expiration', 'JMS_IBM_Report_COA', 'JMS_IBM_Report_COD', 'JMS_IBM_Report_PAN',
    'JMS_IBM_Report_NAN', 'JMS_IBM_Report_Pass_Msg_ID', 'JMS_IBM_Report_Pass_Correl_ID', 'JMS_IBM_Report_Discard_Msg',
    'JMSXGroupID', 'JMSXGroupSeq', 'JMS_IBM_Feedback', 'JMS_IBM_Last_Msg_In_Group', 'JMSXUserID', 'JMS_IBM_PutTime',
    'JMS_IBM_PutDate', 'JMSXAppID'
}

# ################################################################################################################################

# Magic methods are also forbidden.
reserved_attributes.update(set(dir(object) + ['__weakref__', '__dict__', '__module__']))

# ################################################################################################################################

text_message_template = """
JMS message class: jms_text
  jms_delivery_mode:  $jms_delivery_mode
  jms_expiration:     $jms_expiration
  jms_priority:       $jms_priority
  jms_message_id:     $jms_message_id
  jms_timestamp:      $jms_timestamp
  jms_correlation_id: $jms_correlation_id
  jms_destination:    $jms_destination
  jms_reply_to:       $jms_reply_to
  jms_redelivered:    $jms_redelivered
""".lstrip()

# ################################################################################################################################

class MessageConverter:
    def to_message(self, object_to_be_converted_to_a_message):
        raise NotImplementedError('Should be implemented by subclasses')

    def from_message(self, message_to_be_converted_to_an_object):
        raise NotImplementedError('Should be implemented by subclasses')

# ################################################################################################################################

class JMSTemplate:
    def __init__(self, factory=None, delivery_persistent=None, priority=None, time_to_live=None, message_converter=None,
        default_destination=None):

        self.factory = factory

        # QoS
        self.delivery_persistent = delivery_persistent
        self.priority = priority
        self.time_to_live = time_to_live

        self.message_converter = message_converter
        self.default_destination = default_destination

    def convert_and_send(self, object_, destination=None):
        if not self.message_converter:
            raise BaseException("Couldn't send the message, no message converter set")

        self.send(self.message_converter.to_message(object_), destination)

# ################################################################################################################################

    def send(self, message, destination=None):
        if isinstance(message, basestring):
            message = TextMessage(message)

        if destination:
            dest = destination
        elif self.default_destination:
            dest = self.default_destination
        else:
            raise BaseException('No destination given and no default destination set')

        message.jms_destination = dest

        self.factory.send(message, dest)

# ################################################################################################################################

    def receive(self, destination=None, timeout=1000):

        if destination:
            dest = destination
        elif self.default_destination:
            dest = self.default_destination
        else:
            raise BaseException('No destination given and no default destination set')

        return self.factory.receive(dest, timeout)

# ################################################################################################################################

    def receive_and_convert(self, destination=None, timeout=1000):
        if not self.message_converter:
            raise BaseException("Couldn't receive a message, no message converter set")

        return self.message_converter.from_message(self.receive(destination, timeout))

# ################################################################################################################################

    def open_dynamic_queue(self):
        return self.factory.open_dynamic_queue()

# ################################################################################################################################

    def close_dynamic_queue(self, dynamic_queue_name):
        self.factory.close_dynamic_queue(dynamic_queue_name)

# ################################################################################################################################

class TextMessage:

    def __init__(self, text=None, jms_correlation_id=None, jms_delivery_mode=None, jms_destination=None, jms_expiration=None,
        jms_message_id=None, jms_priority=None, jms_redelivered=None, jms_reply_to=None, jms_timestamp=None,
        max_chars_printed=100):

        self.text = text
        self.jms_correlation_id = jms_correlation_id
        self.jms_delivery_mode = jms_delivery_mode or DEFAULT_DELIVERY_MODE
        self.jms_destination = jms_destination
        self.jms_expiration = jms_expiration
        self.jms_message_id = jms_message_id
        self.jms_priority = jms_priority
        self.jms_redelivered = jms_redelivered
        self.jms_reply_to = jms_reply_to
        self.jms_timestamp = jms_timestamp
        self.max_chars_printed = max_chars_printed
        self.put_date = None
        self.put_time = None
        self.mqmd = None

# ################################################################################################################################

    def _get_basic_data(self):
        return {
            'delivery_mode': self.jms_delivery_mode,
            'expiration':self.jms_expiration,
            'priority':self.jms_priority,
            'msg_id':hexlify(self.jms_message_id),
            'put_date':self.put_date,
            'put_time':self.put_time,
            'correlation_id':hexlify(self.jms_correlation_id),
            'destination':self.jms_destination,
            'reply_to':self.jms_reply_to,
            'redelivered':self.jms_redelivered,
            'mqmd': b64encode(pickle_dumps(self.mqmd)).decode('utf8')
        }

# ################################################################################################################################

    def to_dict(self, include_text=True):
        data = self._get_basic_data()
        data['text'] = self.text if include_text else None

        for k, v in data.items():
            if isinstance(v, bytes):
                data[k] = v.decode('utf8')

        return data

# ################################################################################################################################

    def __str__(self):
        basic_data = self._get_basic_data()

        buff = StringIO()
        buff.write(Template(text_message_template).safe_substitute(basic_data))

        user_attrs = set(dir(self)) - reserved_attributes
        user_attrs = list(user_attrs)
        user_attrs.sort()

        if user_attrs:
            for user_attr in user_attrs:
                user_attr_value = getattr(self, user_attr)

                if isinstance(user_attr_value, unicode):
                    user_attr_value = user_attr_value.encode('utf-8')

                buff.write('  %s:%s\n' % (user_attr, user_attr_value))

        if self.text is not None:
            text_to_show = self.text[:self.max_chars_printed]

            if isinstance(text_to_show, unicode):
                text_to_show = text_to_show.encode('utf-8')

            buff.write(text_to_show)

            if len(text_to_show) < len(self.text):
                omitted = locale.format_string('%d', (len(self.text) - len(text_to_show)), True)
                buff.write('\nAnother ')
                buff.write(omitted)
                buff.write(' character(s) omitted')
        else:
            buff.write('<None>')

        value = buff.getvalue()
        buff.close()

        return value

# ################################################################################################################################
