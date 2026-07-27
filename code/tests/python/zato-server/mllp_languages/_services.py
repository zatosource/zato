# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

# The file name the services are hot-deployed under
Service_File_Name = '_test_mllp_languages.py'

# Where the services record what reached them, named here so the test and the services agree on it
Messages_File_Variable = 'Zato_Test_MLLP_Languages_Messages_File'

# ################################################################################################################################
# ################################################################################################################################

class MLLPChannel(NamedTuple):
    """ One channel a test run creates.
    """

    # What the service the channel invokes records itself under, which is how a test knows
    # which channel a message routed to
    label: 'str'

    # The service the channel invokes, which is also what the channel itself is named
    service_name: 'str'

    # What a sender puts in MSH-3 to reach this channel rather than any of the others
    sending_application: 'str'

    # Whether the channel takes a message only from a sender whose certificate was verified
    needs_certificate: 'bool'

# ################################################################################################################################

def _build_channel(label:'str', needs_certificate:'bool') -> 'MLLPChannel':
    """ Builds one channel out of its label, everything else about it following from that.
    """
    out = MLLPChannel(
        label = label,
        service_name = f'test.mllp.languages.{label}',
        sending_application = 'ZATO-TEST-' + label.upper(),
        needs_certificate = needs_certificate,
    )

    return out

# ################################################################################################################################

# The channels one test run creates. There is more than one that takes any sender because routing is
# by the sending application rather than by the port, so a run can tell messages that travelled the
# same connection apart by the channel each of them ended up at.
Plain_Channel     = _build_channel('plain', False)
Lab_Channel       = _build_channel('lab', False)
Radiology_Channel = _build_channel('radiology', False)
TLS_Channel       = _build_channel('tls', True)

# The ones a sender reaches without presenting anything, and every one of them
Open_Channels = [Plain_Channel, Lab_Channel, Radiology_Channel]
Channels      = Open_Channels + [TLS_Channel]

# ################################################################################################################################
# ################################################################################################################################

# What a channel hands to its service is recorded rather than answered - the acknowledgment the
# sender reads back is built by the listener out of the message's own MSH line, so a service has
# nothing to return. Which service ran is what tells the test which channel a message routed to.
#
# The names in it are filled in below rather than written out, so that the constants above are the
# only place any of them is stated. Substitution is by marker rather than by formatting, because
# the source has braces of its own that formatting would have to have escaped.
_header_template = '''\
# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# A hot-deployed module shares no state with the test process, so the two meet over a file
_messages_file = os.environ['@messages_file_variable@']

# ################################################################################################################################
# ################################################################################################################################

def _record(channel:'str', message:'str') -> 'None':
    """ Appends one received message under the name of the channel that took it. Opening the file
    for each message keeps two concurrent senders from overwriting one another's line.
    """
    entry = {'channel': channel, 'message': message}

    with open(_messages_file, 'a') as file_handle:
        _ = file_handle.write(json.dumps(entry) + '\\n')

# ################################################################################################################################
# ################################################################################################################################
'''

_channel_template = '''
class @class_name@(Service):
    """ What the channel reached as @sending_application@ invokes.
    """
    name = '@service_name@'

    def handle(self):
        _record('@label@', self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################

def _build_source() -> 'str':
    """ Builds the module that is hot-deployed, one service in it for each channel.
    """
    out = _header_template.replace('@messages_file_variable@', Messages_File_Variable)

    for channel in Channels:

        class_name = 'TestMLLPLanguages' + channel.label.capitalize()

        out += _channel_template. \
            replace('@class_name@', class_name). \
            replace('@sending_application@', channel.sending_application). \
            replace('@service_name@', channel.service_name). \
            replace('@label@', channel.label)

    return out

# ################################################################################################################################

service_source = _build_source()

# ################################################################################################################################
# ################################################################################################################################
