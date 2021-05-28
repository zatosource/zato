# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from tempfile import NamedTemporaryFile
from traceback import format_exc

# Bunch
from bunch import bunchify

# Zato
from zato.common.api import SFTP
from zato.common.json_internal import dumps
from zato.common.sftp import SFTPOutput
from zato.server.connection.connector.subprocess_.base import BaseConnectionContainer, Response

# ################################################################################################################################

if 0:
    from bunch import Bunch

    Bunch = Bunch

# ################################################################################################################################
# ################################################################################################################################

class EventsConnectionContainer(BaseConnectionContainer):

    connection_class = object
    ipc_name = conn_type = logging_file_name = 'events'

    remove_id_from_def_msg = False
    remove_name_from_def_msg = False

# ################################################################################################################################

    def _on_EVENT_PUSH(self, msg, is_reconnect=False, _utcnow=datetime.utcnow):
        out = {}

        #self.logger.warn('QQQ _on_EVENT_PUSH_EXECUTE *********************************')

        '''
        connection = self.connections[msg.id] # type: SFTPConnection
        start_time = _utcnow()

        try:
            result = connection.execute(msg.cid, msg.data, msg.log_level) # type: SFTPOutput
        except ErrorReturnCode as e:
            out['stdout'] = e.stdout
            out['stderr'] = e.stderr
        except Exception:
            out['stderr'] = format_exc()
            out['is_ok'] = False
        else:
            out.update(result.to_dict())
        finally:
            out['cid'] = msg.cid
            out['command_no'] = connection.command_no
            out['response_time'] = str(_utcnow() - start_time)
            '''

        return Response(data=dumps(out))

# ################################################################################################################################

if __name__ == '__main__':

    container = EventsConnectionContainer()
    container.run()

# ################################################################################################################################
