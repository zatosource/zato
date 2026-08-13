# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a message published to an outgoing connection is actually handed over to it. There are two
# functions per type of connection - one that finds a connection by the id it was published to,
# and one that gives a message to what was found - each of them reaching the connection the way
# a service would, so an edit to a connection is picked up without anything here being told about
# it. A handler raises when the connection did not accept the message, which is what makes the
# pub/sub delivery loop keep the message queued and try again.

# stdlib
import os
from json import loads
from logging import getLogger
from tempfile import mkstemp

# gevent
from gevent.fileobject import FileObjectThread

# Zato
from zato.common.api import GENERIC
from zato.common.pubsub.outgoing import OutgoingType, register_outgoing_conn_type

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# How many seconds to wait for a pooled FHIR client, which covers the window
# while the connection queue is still being built at startup.
_fhir_block_timeout = 30

# A FHIR resource is created by posting it to the path its own type names.
_fhir_method = 'POST'

# The keys of the envelope a queued file transfer travels under - the bytes stay on the local disk
# and only the spool path and the remote destination go through the queue, so a file of any size
# travels without ever touching a pub/sub row.
Key_Spool_Path = 'spool_path'
Key_Remote_Path = 'remote_path'

# What a spool file's name ends with, so a stray one can be told apart in the temporary directory.
_spool_suffix = '-zato-file-delivery-spool.dat'

# ################################################################################################################################
# ################################################################################################################################

# Which generic connection type is published to as which kind of outgoing connection. A type that is
# not here has no queue, so a rename or a delete of one has nothing to move or to remove.
publishable_generic_types = {
    GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: OutgoingType.FHIR,
    GENERIC.CONNECTION.TYPE.OUTCONN_SFTP: OutgoingType.SFTP,
    GENERIC.CONNECTION.TYPE.OUTCONN_SMB: OutgoingType.SMB,
}

# ################################################################################################################################
# ################################################################################################################################

def _locate_rest(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ Finds an outgoing REST connection by its id, which is what the connection keeps through a rename.
    """
    item = server.config_manager.config_store.out_plain_http.get_by_id(conn_id)

    # A connection that was deleted is no longer anywhere to be found
    if not item:
        return ()

    out = (item.config['name'], item.conn)
    return out

# ################################################################################################################################

def _deliver_to_rest(server:'ParallelServer', cid:'str', wrapper:'any_', data:'str') -> 'None':
    """ Hands one message over to an outgoing REST connection.
    """

    # The method, address, headers, query string and credentials all come from the connection itself ..
    response = wrapper.rest_invoke(cid, data)

    # .. and a response that was not accepted comes back rather than being raised, so it becomes an exception here.
    _ = response.raise_for_status()

# ################################################################################################################################

def _locate_fhir(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ Finds an outgoing HL7 FHIR connection by its id. These connections live in a dict keyed by name,
    so the id is what each of them is compared by.
    """
    for item in server.config_manager.outconn_hl7_fhir.values():
        if item['id'] == conn_id:
            out = (item['name'], item.conn)
            return out

    return ()

# ################################################################################################################################

def _deliver_to_fhir(server:'ParallelServer', cid:'str', wrapper:'any_', data:'str') -> 'None':
    """ Hands one message over to an outgoing HL7 FHIR connection, as a resource of the type the document names.
    """

    # A FHIR resource travels as a document, so what arrives here as text is that document in its JSON form ..
    resource = loads(data)

    # .. and a resource is created under the path its own type names ..
    path = resource['resourceType']

    # .. through a client taken from the connection's own pool, blocking to cover the window
    # .. while that pool is still being built.
    with wrapper.client(should_block=True, block_timeout=_fhir_block_timeout) as client:
        _ = client._do_request(_fhir_method, path, data=resource)

# ################################################################################################################################

def _locate_sftp(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ Finds an outgoing SFTP connection by its id. These connections live in a dict keyed by name,
    so the id is what each of them is compared by.
    """
    for item in server.config_manager.outconn_sftp.values():
        if item['id'] == conn_id:
            out = (item['name'], item['conn'])
            return out

    return ()

# ################################################################################################################################

def _locate_smb(server:'ParallelServer', conn_id:'int') -> 'anytuple':
    """ Finds an outgoing SMB connection by its id. These connections live in a dict keyed by name,
    so the id is what each of them is compared by.
    """
    for item in server.config_manager.outconn_smb.values():
        if item['id'] == conn_id:
            out = (item['name'], item['conn'])
            return out

    return ()

# ################################################################################################################################

def spool_file_payload(data:'bytes') -> 'str':
    """ Writes the bytes of one queued file transfer to a local spool file, returning its path -
    what the publication puts in its envelope in place of the bytes themselves. The write runs
    in its own thread so as not to block the event loop.
    """
    spool_fd, spool_path = mkstemp(suffix=_spool_suffix)
    os.close(spool_fd)

    thread_file = FileObjectThread(spool_path, 'wb')
    _ = thread_file.write(data)
    thread_file.close()

    return spool_path

# ################################################################################################################################

def _read_spool_file(spool_path:'str') -> 'bytes':
    """ Reads the bytes one queued file transfer spooled to the local disk - the queue itself carries
    only the spool path, so a file of any size travels without ever touching a pub/sub row.
    The read runs in its own thread so as not to block the event loop.
    """
    thread_file = FileObjectThread(spool_path, 'rb')
    out = thread_file.read()
    thread_file.close()

    return out

# ################################################################################################################################

def _deliver_to_sftp(server:'ParallelServer', cid:'str', wrapper:'any_', data:'str') -> 'None':
    """ Hands one queued file over to an outgoing SFTP connection - the bytes come from the local
    spool file the publication left behind and go to the remote path it named. The write overwrites,
    so a retry after a partial upload starts clean, and the connection's own audit event is what
    records the attempt. The spool file outlives every failed attempt and goes away only
    once the file has actually been written out.
    """

    # Imported here to avoid circular imports
    from zato.server.connection.sftp import SFTPConnection

    envelope = loads(data)

    payload = _read_spool_file(envelope[Key_Spool_Path])

    conn = SFTPConnection(cid, wrapper)
    conn.write(payload, envelope[Key_Remote_Path], overwrite=True)

    # Only a delivered file's spool is removed - a failed delivery raised above,
    # keeping the bytes in place for the retry.
    os.remove(envelope[Key_Spool_Path])

# ################################################################################################################################

def _deliver_to_smb(server:'ParallelServer', cid:'str', wrapper:'any_', data:'str') -> 'None':
    """ Hands one queued file over to an outgoing SMB connection, the same way the SFTP handler
    does - SMB writes always overwrite, so a retry after a partial upload starts clean.
    """

    # Imported here to avoid circular imports
    from zato.server.connection.smb import SMBConnection

    envelope = loads(data)

    payload = _read_spool_file(envelope[Key_Spool_Path])

    conn = SMBConnection(cid, wrapper)
    conn.write(payload, envelope[Key_Remote_Path])

    # Only a delivered file's spool is removed - a failed delivery raised above,
    # keeping the bytes in place for the retry.
    os.remove(envelope[Key_Spool_Path])

# ################################################################################################################################
# ################################################################################################################################

def register_delivery_handlers() -> 'None':
    """ Makes every type of outgoing connection that can be published to publishable.
    """
    register_outgoing_conn_type(OutgoingType.REST, _locate_rest, _deliver_to_rest)
    register_outgoing_conn_type(OutgoingType.FHIR, _locate_fhir, _deliver_to_fhir)

    # File deliveries are recorded as file-outgoing audit events by the connections themselves,
    # so their queue topics write no pub/sub events of their own.
    register_outgoing_conn_type(OutgoingType.SFTP, _locate_sftp, _deliver_to_sftp, is_audit_log_active=False)
    register_outgoing_conn_type(OutgoingType.SMB, _locate_smb, _deliver_to_smb, is_audit_log_active=False)

# ################################################################################################################################
# ################################################################################################################################
