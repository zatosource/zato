# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

# The names the channels invoke, which are also what the enmasse definitions refer to
Plain_Service_Name = 'test.mllp.languages.plain'
TLS_Service_Name   = 'test.mllp.languages.tls'

# What each service records itself under, which is how a test knows the channel a message routed to
Plain_Label = 'plain'
TLS_Label   = 'tls'

# The file name the services are hot-deployed under
Service_File_Name = '_test_mllp_languages.py'

# Where the services record what reached them, named here so the test and the services agree on it
Messages_File_Variable = 'Zato_Test_MLLP_Languages_Messages_File'

# ################################################################################################################################
# ################################################################################################################################

# What a channel hands to its service is recorded rather than answered - the acknowledgment the
# sender reads back is built by the listener out of the message's own MSH line, so a service has
# nothing to return. Which of the two ran is what tells the test which channel a message routed to.
#
# The names in it are filled in below rather than written out, so that the constants above are the
# only place any of them is stated. Substitution is by marker rather than by formatting, because
# the source has braces of its own that formatting would have to have escaped.
_source_template = '''\
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

class TestMLLPLanguagesPlain(Service):
    """ What the channel taking plain connections invokes.
    """
    name = '@plain_service_name@'

    def handle(self):
        _record('@plain_label@', self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################

class TestMLLPLanguagesTLS(Service):
    """ What the channel taking connections whose certificate was verified invokes.
    """
    name = '@tls_service_name@'

    def handle(self):
        _record('@tls_label@', self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################

service_source = _source_template. \
    replace('@messages_file_variable@', Messages_File_Variable). \
    replace('@plain_service_name@', Plain_Service_Name). \
    replace('@tls_service_name@', TLS_Service_Name). \
    replace('@plain_label@', Plain_Label). \
    replace('@tls_label@', TLS_Label)

# ################################################################################################################################
# ################################################################################################################################
