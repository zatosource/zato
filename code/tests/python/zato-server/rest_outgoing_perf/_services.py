# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The services that the channels of the suite invoke, each of which invokes one outgoing REST connection once
# and answers with the status that the target endpoint returned.
invoke_service_source = '''# -*- coding: utf-8 -*-

# Zato
from zato.server.service import Service

def _invoke(service, connection_name):
    response = service.out.rest[connection_name].conn.get(service.cid)
    service.response.status_code = response.status_code

class InvokePlain(Service):
    name = 'test.perf.outgoing.plain'

    def handle(self):
        _invoke(self, 'test.perf.outgoing.plain')

class InvokeBasic(Service):
    name = 'test.perf.outgoing.basic'

    def handle(self):
        _invoke(self, 'test.perf.outgoing.basic')

class InvokeNewConnection(Service):
    name = 'test.perf.outgoing.new-connection'

    def handle(self):
        _invoke(self, 'test.perf.outgoing.new-connection')
'''
