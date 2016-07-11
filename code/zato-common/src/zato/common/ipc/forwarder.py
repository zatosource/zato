# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import zmq

def main():

    try:
        context = zmq.Context(1)
        # Socket facing clients
        frontend = context.socket(zmq.SUB)
        frontend.bind("ipc:///tmp/zato-ipc-server1-sub")
        
        frontend.setsockopt(zmq.SUBSCRIBE, b"")
        
        # Socket facing services
        backend = context.socket(zmq.PUB)
        backend.bind("ipc:///tmp/zato-ipc-server1-pub")

        zmq.device(zmq.FORWARDER, frontend, backend)
    except Exception, e:
        print("bringing down zmq device", e)
    finally:
        frontend.close()
        backend.close()
        context.term()

if __name__ == "__main__":
    main()

'''
# gevent
from gevent import sleep, spawn, spawn_later

# ZeroMQ
import zmq.green as zmq

# Zato
from zato.common.ipc import IPCBase

# ################################################################################################################################

class Forwarder(IPCBase):
    """ Sends outgoing IPC messages to any party listening for them.
    """
    socket_method = 'bind'
    socket_type = zmq.PUB

    def send(self):
        self.socket.send_pyobj(str(self.pid) * 5)

    def send_forever(self):
        while True:
            sleep(0.1)
            self.send()

# ################################################################################################################################

if __name__ == '__main__':

    name = 'server1'
    p = Publisher(name, 1)
    p.send_forever()
    '''