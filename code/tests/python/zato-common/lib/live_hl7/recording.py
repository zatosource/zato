# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Zato side of an HL7 live suite as services - recording services writing what they are handed to a file,
# a service answering with an application error and a service sending through an outgoing connection.

# stdlib
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strtuple

# ################################################################################################################################
# ################################################################################################################################

# The file name the services are hot-deployed under
Service_File_Name = '_test_hl7_live.py'

# Where the recording services write what reached them, named here so the test and the services agree on it
Messages_File_Variable = 'Zato_Test_HL7_Messages_File'

# The service that refuses every message it is handed
Raising_Service = 'hl7.live.raise'

# What the refusing service says, which is what the sender reads in the ERR segment
Raising_Error_Text = 'The message cannot be processed by this department'

# The service a test sends through one of Zato's outgoing connections with
Send_Service = 'hl7.live.send'

# ################################################################################################################################
# ################################################################################################################################

class Recorder(NamedTuple):
    """ One recording service - what it is called and what the lines it writes are filed under. A recorder that
    names a destination hands the message on to it wrapped in a JSON object under the given key.
    """
    label: 'str'
    service: 'str'
    json_destination: 'str' = ''
    json_key: 'str' = ''

# ################################################################################################################################

recorder_list = list[Recorder]

# ################################################################################################################################
# ################################################################################################################################

# Substitution is by marker rather than by formatting, because the source has braces of its own that
# formatting would have to have escaped.
_module_header = '''\
# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
from traceback import format_exc

# Zato
from zato.common.hl7.exception import HL7ApplicationError
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# A hot-deployed module shares no state with the test process, so the two meet over a file
_messages_file = os.environ['@messages_file_variable@']

# ################################################################################################################################
# ################################################################################################################################

def _as_text(message):
    """ The message as text, whatever form the channel handed it over in.
    """
    if isinstance(message, bytes):
        out = message.decode('utf-8')
    else:
        out = message

    return out

# ################################################################################################################################

def _record(channel, message):
    """ Appends one received message under the label of the channel that took it. Opening the file for
    each message keeps two concurrent deliveries from overwriting one another's line.
    """
    entry = {'channel': channel, 'message': message}

    with open(_messages_file, 'a') as file_handle:
        _ = file_handle.write(json.dumps(entry) + '\\n')

# ################################################################################################################################
# ################################################################################################################################

class @raising_class@(Service):
    """ Refuses every message - the sender is answered with AE and the reason in the ERR segment.
    """
    name = '@raising_service@'

    def handle(self):
        message = _as_text(self.request.raw_request)
        _record('@raising_label@', message)

        raise HL7ApplicationError('@raising_error_text@')

# ################################################################################################################################
# ################################################################################################################################

class @send_class@(Service):
    """ Sends one message through one of the outgoing connections and returns what came back -
    the acknowledgment when there was one, the error when the send raised instead.
    """
    name = '@send_service@'

    def handle(self):
        request = self.request.raw_request

        try:
            ack = self.mllp[request['connection']].send(request['message'])
        except Exception:
            self.response.payload = {
                'is_sent': False,
                'ack_code': '',
                'ack_text': '',
                'error_text': format_exc(),
            }
            return

        self.response.payload = {
            'is_sent': True,
            'ack_code': ack.ack_code,
            'ack_text': ack.ack_text,
            'error_text': ack.error_text,
        }

# ################################################################################################################################
# ################################################################################################################################
'''

_recorder_template = '''
class @class_name@(Service):
    """ Records what the channel `@label@` took.
    """
    name = '@service@'

    def handle(self):
        message = _as_text(self.request.raw_request)
        _record('@label@', message)
@forward@
# ################################################################################################################################
# ################################################################################################################################
'''

_forward_template = '''
        self.destination['@json_destination@'] = {'@json_key@': message}
'''

# ################################################################################################################################
# ################################################################################################################################

def class_name(service_name:'str') -> 'str':
    """ A class name out of a service name - hie.shr.record becomes HieShrRecord.
    """
    parts = service_name.replace('-', '.').split('.')

    out = ''
    for part in parts:
        out += part.capitalize()

    return out

# ################################################################################################################################

def _render_recorder(recorder:'Recorder') -> 'str':
    """ One recording service.
    """
    if recorder.json_destination:
        forward = _forward_template
        forward = forward.replace('@json_destination@', recorder.json_destination)
        forward = forward.replace('@json_key@', recorder.json_key)
    else:
        forward = ''

    out = _recorder_template
    out = out.replace('@class_name@', class_name(recorder.service))
    out = out.replace('@label@', recorder.label)
    out = out.replace('@service@', recorder.service)
    out = out.replace('@forward@', forward)

    return out

# ################################################################################################################################

def build_source(recorders:'recorder_list', sources:'strtuple'=()) -> 'str':
    """ The module a suite hot-deploys - the refusing and the sending service, one recording service per recorder
    given, then the suite's own services as given, which have the module's header and its helpers at their disposal.
    """
    header = _module_header
    header = header.replace('@messages_file_variable@', Messages_File_Variable)
    header = header.replace('@raising_class@', class_name(Raising_Service))
    header = header.replace('@raising_service@', Raising_Service)
    header = header.replace('@raising_label@', Raising_Service)
    header = header.replace('@raising_error_text@', Raising_Error_Text)
    header = header.replace('@send_class@', class_name(Send_Service))
    header = header.replace('@send_service@', Send_Service)

    sections:'strlist' = [header]

    for recorder in recorders:
        sections.append(_render_recorder(recorder))

    sections.extend(sources)

    out = ''.join(sections)
    return out

# ################################################################################################################################
# ################################################################################################################################
