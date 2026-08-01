# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import threading
import time

# Zato
from hl7_client.java_receiver import JavaMLLPReceiver
from hl7_client.mllp_receiver import MLLPReceiver
from hl7_client.ports import find_free_port
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# What the two third-party receiving stacks this suite runs against are named. A test asks for one
# of them by name and gets a listener it can point an outgoing connection at without having to know
# which of the two it ended up with.
Receiver_Hl7apy = 'hl7apy'
Receiver_Hapi   = 'hapi'

# Both of them, which is what a test that has to hold for either is parametrized over
Receiver_Names = [Receiver_Hl7apy, Receiver_Hapi]

# What every listener here binds to
Host = '127.0.0.1'

# How long a listener is given to have recorded a message that was acknowledged. The acknowledgment
# is written by the listener before the record of the delivery reaches this process, so a test that
# read the record the instant an acknowledgment arrived could be looking a moment too early.
Delivery_Timeout = 10.0

# How often the record of what arrived is checked while waiting for it
_Delivery_Poll_Interval = 0.05

# How long a raw listener waits for a sender to say something before it gives up on the connection
_Raw_Read_Timeout = 30.0

# How many bytes a raw listener reads at a time
_Raw_Read_Size = 4096

# ################################################################################################################################
# ################################################################################################################################

def build_receiver(name:'str', **kwargs:'any_') -> 'any_':
    """ Builds one of the two third-party receiving stacks. Both offer a port, an address, a record
    of what arrived and a start and a stop, so a test only names which of them it wants.
    """
    if name == Receiver_Hl7apy:
        out = MLLPReceiver(**kwargs)

    elif name == Receiver_Hapi:
        out = JavaMLLPReceiver(**kwargs)

    else:
        raise Exception(f'No such receiver: {name}')

    return out

# ################################################################################################################################

def wait_for_deliveries(receiver:'any_', expected_count:'int', timeout:'float'=Delivery_Timeout) -> 'None':
    """ Waits until a listener has recorded the number of messages expected of it, so that a test
    asserting on what arrived is never looking before the record of it was written.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        if len(receiver.deliveries) >= expected_count:
            return

        time.sleep(_Delivery_Poll_Interval)

    raise Exception(
        f'The receiver recorded {len(receiver.deliveries)} of the {expected_count} messages expected within {timeout}s')

# ################################################################################################################################

def next_delivery(receiver:'any_', previous_count:'int', timeout:'float'=Delivery_Timeout) -> 'str':
    """ Waits for one more message than the listener had recorded before and returns it. Counting
    from where a test was rather than from zero is what keeps it independent of how many times a
    connection had to be tried before it was ready to send through.
    """
    wait_for_deliveries(receiver, previous_count + 1, timeout)

    out = receiver.deliveries[previous_count].text
    return out

# ################################################################################################################################
# ################################################################################################################################

class RawSocketReceiver:
    """ A listener that takes a connection and then behaves badly on purpose - it either never
    answers or closes half-way through a frame. Neither is HL7, which is why neither belongs in a
    receiving stack that speaks it, and both are what a sender is on its own against in the field.
    """

    def __init__(self, is_closing_early:'bool'=False) -> 'None':

        # Whether a connection is dropped once something has been read off it, which is the frame
        # that ends nowhere, as against one that is accepted and then left in silence
        self.is_closing_early = is_closing_early

        self.port = find_free_port()

        # How many connections were accepted, which is what says whether a sender that reported a
        # failure had got as far as connecting
        self.connection_count = 0

        self._listener:'socket.socket | None' = None
        self._is_running = False
        self._thread:'threading.Thread | None' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts taking connections.
        """
        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listener.bind((Host, self.port))
        self._listener.listen(16)

        # The accept loop has to come back around often enough to notice that it was stopped, since
        # nothing else interrupts a blocking accept
        self._listener.settimeout(0.2)

        self._is_running = True

        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()

# ################################################################################################################################

    def _accept_loop(self) -> 'None':
        """ Takes every connection offered and hands it to whichever bad ending this listener is for.
        """
        listener = cast_('socket.socket', self._listener)

        while self._is_running:

            try:
                connection, _ = listener.accept()
            except socket.timeout:
                continue
            except OSError:

                # The listener was closed underneath the loop, which is how a stop ends it
                return

            self.connection_count += 1

            handler_thread = threading.Thread(target=self._handle, args=(connection,), daemon=True)
            handler_thread.start()

# ################################################################################################################################

    def _handle(self, connection:'socket.socket') -> 'None':
        """ Sees one connection through to its bad ending.
        """
        connection.settimeout(_Raw_Read_Timeout)

        try:

            # A listener that closes half-way through waits until the sender has started saying
            # something, because a connection dropped before then is a refusal rather than a frame
            # that ends nowhere
            if self.is_closing_early:
                _ = connection.recv(_Raw_Read_Size)
                connection.close()
                return

            # A listener that never answers reads everything the sender has to say and then says
            # nothing back, which is what a send timeout is measured against
            while self._is_running:
                chunk = connection.recv(_Raw_Read_Size)

                if not chunk:
                    return

        except OSError:

            # A sender that gave up first closed the connection, which is the outcome rather than
            # a problem with this listener
            pass

        finally:
            connection.close()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops taking connections, leaving the port free for a later start.
        """
        self._is_running = False

        if self._listener:
            self._listener.close()
            self._listener = None

# ################################################################################################################################

    @property
    def address(self) -> 'str':
        """ Where an outgoing connection is pointed to reach this listener.
        """
        out = f'{Host}:{self.port}'
        return out

# ################################################################################################################################
# ################################################################################################################################
