# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ctypes
import os
import struct

# Zato
from zato.common.typing_ import anydict, bytesnone, optional, strlist, tuple_

# ################################################################################################################################
# ################################################################################################################################

# What a successful MQGET of a message returns - the payload and the message descriptor fields
mq_message = tuple_[bytes, anydict]
mq_message_none = optional[mq_message]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Structure identifiers and versions
    MQCNO_Struc_ID  = b'CNO '
    MQCNO_Version_5 = 5
    MQCSP_Struc_ID  = b'CSP '
    MQCSP_Version_1 = 1
    MQOD_Struc_ID   = b'OD  '
    MQOD_Version_1  = 1
    MQMD_Struc_ID   = b'MD  '
    MQMD_Version_1  = 1
    MQPMO_Struc_ID  = b'PMO '
    MQPMO_Version_1 = 1
    MQGMO_Struc_ID  = b'GMO '
    MQGMO_Version_1 = 1

    # Connection options
    MQCNO_Client_Binding = 0x00000800

    # Authentication types
    MQCSP_Auth_User_ID_And_Pwd = 1

    # Object types and open options
    MQOT_Q                  = 1
    MQOO_Input_As_Q_Def     = 0x00000001
    MQOO_Output             = 0x00000010
    MQOO_Fail_If_Quiescing  = 0x00002000

    # Message descriptor defaults
    MQMT_Datagram             = 8
    MQMT_Request              = 1
    MQEI_Unlimited            = -1
    MQFB_None                 = 0
    MQENC_Native              = 0x00000222
    MQCCSI_UTF8               = 1208
    MQPRI_Priority_As_Q_Def   = -1
    MQPER_Not_Persistent      = 0
    MQRO_None                 = 0

    # Put and get options
    MQPMO_No_Syncpoint      = 0x00000004
    MQPMO_New_Msg_ID        = 0x00000040
    MQPMO_Fail_If_Quiescing = 0x00002000
    MQGMO_Wait              = 0x00000001
    MQGMO_No_Syncpoint      = 0x00000004
    MQGMO_Fail_If_Quiescing = 0x00002000

    # Completion and reason codes
    MQCC_OK                  = 0
    MQCC_Failed              = 2
    MQRC_No_Msg_Available    = 2033

    # Message formats
    Format_String = 'MQSTR   '
    Format_RFH2   = 'MQHRF2  '

    # How big the MQGET buffer is - matches the default IBM MQ maximum message length
    Get_Buffer_Size = 4 * 1024 * 1024

    # Field lengths of MQ character fields
    Queue_Name_Length         = 48
    Queue_Manager_Name_Length = 48

# ################################################################################################################################
# ################################################################################################################################

# Fixed-size types the MQI structures are made of
_MQLONG   = ctypes.c_int32
_MQHCONN  = ctypes.c_int32
_MQHOBJ   = ctypes.c_int32
_MQPTR    = ctypes.c_void_p

# ################################################################################################################################
# ################################################################################################################################

class _MQCNO(ctypes.Structure):
    """ Connection options for MQCONNX, version 5, up to the security parameters pointer.
    """
    _fields_ = [
        ('StrucId', ctypes.c_char * 4),
        ('Version', _MQLONG),
        ('Options', _MQLONG),
        ('ClientConnOffset', _MQLONG),
        ('ClientConnPtr', _MQPTR),
        ('ConnTag', ctypes.c_ubyte * 128),
        ('SSLConfigPtr', _MQPTR),
        ('SSLConfigOffset', _MQLONG),
        ('ConnectionId', ctypes.c_ubyte * 24),
        ('SecurityParmsOffset', _MQLONG),
        ('SecurityParmsPtr', _MQPTR),
    ]

# ################################################################################################################################

class _MQCSP(ctypes.Structure):
    """ Security parameters carrying the user ID and password, version 1.
    """
    _fields_ = [
        ('StrucId', ctypes.c_char * 4),
        ('Version', _MQLONG),
        ('AuthenticationType', _MQLONG),
        ('Reserved1', ctypes.c_ubyte * 4),
        ('CSPUserIdPtr', _MQPTR),
        ('CSPUserIdOffset', _MQLONG),
        ('CSPUserIdLength', _MQLONG),
        ('Reserved2', ctypes.c_ubyte * 8),
        ('CSPPasswordPtr', _MQPTR),
        ('CSPPasswordOffset', _MQLONG),
        ('CSPPasswordLength', _MQLONG),
    ]

# ################################################################################################################################

class _MQOD(ctypes.Structure):
    """ Object descriptor naming the queue to open, version 1.
    """
    _fields_ = [
        ('StrucId', ctypes.c_char * 4),
        ('Version', _MQLONG),
        ('ObjectType', _MQLONG),
        ('ObjectName', ctypes.c_char * 48),
        ('ObjectQMgrName', ctypes.c_char * 48),
        ('DynamicQName', ctypes.c_char * 48),
        ('AlternateUserId', ctypes.c_char * 12),
    ]

# ################################################################################################################################

class _MQMD(ctypes.Structure):
    """ Message descriptor, version 1.
    """
    _fields_ = [
        ('StrucId', ctypes.c_char * 4),
        ('Version', _MQLONG),
        ('Report', _MQLONG),
        ('MsgType', _MQLONG),
        ('Expiry', _MQLONG),
        ('Feedback', _MQLONG),
        ('Encoding', _MQLONG),
        ('CodedCharSetId', _MQLONG),
        ('Format', ctypes.c_char * 8),
        ('Priority', _MQLONG),
        ('Persistence', _MQLONG),
        ('MsgId', ctypes.c_ubyte * 24),
        ('CorrelId', ctypes.c_ubyte * 24),
        ('BackoutCount', _MQLONG),
        ('ReplyToQ', ctypes.c_char * 48),
        ('ReplyToQMgr', ctypes.c_char * 48),
        ('UserIdentifier', ctypes.c_char * 12),
        ('AccountingToken', ctypes.c_ubyte * 32),
        ('ApplIdentityData', ctypes.c_char * 32),
        ('PutApplType', _MQLONG),
        ('PutApplName', ctypes.c_char * 28),
        ('PutDate', ctypes.c_char * 8),
        ('PutTime', ctypes.c_char * 8),
        ('ApplOriginData', ctypes.c_char * 4),
    ]

# ################################################################################################################################

class _MQPMO(ctypes.Structure):
    """ Put-message options, version 1.
    """
    _fields_ = [
        ('StrucId', ctypes.c_char * 4),
        ('Version', _MQLONG),
        ('Options', _MQLONG),
        ('Timeout', _MQLONG),
        ('Context', _MQHOBJ),
        ('KnownDestCount', _MQLONG),
        ('UnknownDestCount', _MQLONG),
        ('InvalidDestCount', _MQLONG),
        ('ResolvedQName', ctypes.c_char * 48),
        ('ResolvedQMgrName', ctypes.c_char * 48),
    ]

# ################################################################################################################################

class _MQGMO(ctypes.Structure):
    """ Get-message options, version 1.
    """
    _fields_ = [
        ('StrucId', ctypes.c_char * 4),
        ('Version', _MQLONG),
        ('Options', _MQLONG),
        ('WaitInterval', _MQLONG),
        ('Signal1', _MQLONG),
        ('Signal2', _MQLONG),
        ('ResolvedQName', ctypes.c_char * 48),
    ]

# ################################################################################################################################
# ################################################################################################################################

def _pad(value:'str', length:'int') -> 'bytes':
    """ Pads an MQ character field with spaces to its fixed length.
    """
    out = value.encode('utf-8').ljust(length, b' ')
    return out

# ################################################################################################################################

def build_rfh2(folders:'strlist', body:'bytes') -> 'bytes':
    """ Builds an MQRFH2 byte payload with the given folders and body, in little-endian byte order,
    the same way the IBM MQ classes for JMS lay it out.
    """

    # Each folder is padded to a multiple of four bytes and preceded by its byte length ..
    name_value_area = b''

    for folder in folders:
        padded = folder.encode('utf-8')
        while len(padded) % 4 != 0:
            padded += b' '
        name_value_area += struct.pack('<i', len(padded)) + padded

    # .. the fixed part carries the total header length so the parser knows where the body starts.
    struc_length = 36 + len(name_value_area)

    fixed_part = b'RFH '
    fixed_part += struct.pack('<i', 2)                                  # Version
    fixed_part += struct.pack('<i', struc_length)                      # StrucLength
    fixed_part += struct.pack('<i', ModuleCtx.MQENC_Native)            # Encoding
    fixed_part += struct.pack('<i', ModuleCtx.MQCCSI_UTF8)             # CodedCharSetId
    fixed_part += ModuleCtx.Format_String.encode('utf-8')              # Format of the body
    fixed_part += struct.pack('<i', 0)                                 # Flags
    fixed_part += struct.pack('<i', ModuleCtx.MQCCSI_UTF8)             # NameValueCCSID

    out = fixed_part + name_value_area + body
    return out

# ################################################################################################################################
# ################################################################################################################################

class MQTestClient:
    """ A minimal ctypes-based MQI client for putting and getting test messages with full control
    over the message descriptor, e.g. the format, the reply-to queue or the correlation ID.
    """

    def __init__(
        self,
        library_path:'str',
        address:'str',
        mq_channel_name:'str',
        queue_manager:'str',
        username:'str',
        password:'str',
        ) -> 'None':

        self.queue_manager = queue_manager
        self.username = username
        self.password = password

        # The channel definition goes through the MQSERVER environment variable,
        # which the client library reads when the connection is established.
        host, _, port = address.rpartition(':')
        os.environ['MQSERVER'] = f'{mq_channel_name}/TCP/{host}({port})'

        self.library = ctypes.CDLL(library_path)
        self.connection = _MQHCONN(0)

# ################################################################################################################################

    def _check(self, verb:'str', completion_code:'_MQLONG', reason:'_MQLONG') -> 'None':
        """ Raises an exception when an MQI call did not complete successfully.
        """
        if completion_code.value == ModuleCtx.MQCC_Failed:
            raise Exception(f'{verb} failed with reason code {reason.value}')

# ################################################################################################################################

    def connect(self) -> 'None':
        """ Connects to the queue manager with the configured credentials.
        """

        # The credentials travel in an MQCSP structure the connection options point to ..
        username_bytes = self.username.encode('utf-8')
        password_bytes = self.password.encode('utf-8')
        username_buffer = ctypes.create_string_buffer(username_bytes)
        password_buffer = ctypes.create_string_buffer(password_bytes)

        security = _MQCSP()
        security.StrucId = ModuleCtx.MQCSP_Struc_ID
        security.Version = ModuleCtx.MQCSP_Version_1
        security.AuthenticationType = ModuleCtx.MQCSP_Auth_User_ID_And_Pwd
        security.CSPUserIdPtr = ctypes.cast(username_buffer, _MQPTR)
        security.CSPUserIdLength = len(username_bytes)
        security.CSPPasswordPtr = ctypes.cast(password_buffer, _MQPTR)
        security.CSPPasswordLength = len(password_bytes)

        # .. and the connection options ask for a client connection with those credentials.
        options = _MQCNO()
        options.StrucId = ModuleCtx.MQCNO_Struc_ID
        options.Version = ModuleCtx.MQCNO_Version_5
        options.Options = ModuleCtx.MQCNO_Client_Binding
        options.SecurityParmsPtr = ctypes.cast(ctypes.pointer(security), _MQPTR)

        queue_manager_name = ctypes.create_string_buffer(_pad(self.queue_manager, ModuleCtx.Queue_Manager_Name_Length), 48)

        completion_code = _MQLONG(0)
        reason = _MQLONG(0)

        self.library.MQCONNX(
            queue_manager_name,
            ctypes.byref(options),
            ctypes.byref(self.connection),
            ctypes.byref(completion_code),
            ctypes.byref(reason),
        )

        self._check('MQCONNX', completion_code, reason)

# ################################################################################################################################

    def disconnect(self) -> 'None':
        """ Disconnects from the queue manager.
        """
        completion_code = _MQLONG(0)
        reason = _MQLONG(0)

        self.library.MQDISC(ctypes.byref(self.connection), ctypes.byref(completion_code), ctypes.byref(reason))

        self._check('MQDISC', completion_code, reason)

# ################################################################################################################################

    def _open_queue(self, queue:'str', open_options:'int') -> '_MQHOBJ':
        """ Opens a queue with the given options and returns its object handle.
        """
        descriptor = _MQOD()
        descriptor.StrucId = ModuleCtx.MQOD_Struc_ID
        descriptor.Version = ModuleCtx.MQOD_Version_1
        descriptor.ObjectType = ModuleCtx.MQOT_Q
        descriptor.ObjectName = _pad(queue, ModuleCtx.Queue_Name_Length)

        object_handle = _MQHOBJ(0)
        completion_code = _MQLONG(0)
        reason = _MQLONG(0)

        self.library.MQOPEN(
            self.connection,
            ctypes.byref(descriptor),
            _MQLONG(open_options),
            ctypes.byref(object_handle),
            ctypes.byref(completion_code),
            ctypes.byref(reason),
        )

        self._check('MQOPEN', completion_code, reason)

        return object_handle

# ################################################################################################################################

    def _close_queue(self, object_handle:'_MQHOBJ') -> 'None':
        """ Closes a previously opened queue.
        """
        completion_code = _MQLONG(0)
        reason = _MQLONG(0)

        self.library.MQCLOSE(
            self.connection,
            ctypes.byref(object_handle),
            _MQLONG(0),
            ctypes.byref(completion_code),
            ctypes.byref(reason),
        )

        self._check('MQCLOSE', completion_code, reason)

# ################################################################################################################################

    def put(
        self,
        queue:'str',
        data:'bytes',
        *,
        format:'str' = ModuleCtx.Format_String,
        message_type:'int' = ModuleCtx.MQMT_Datagram,
        reply_to_queue:'str' = '',
        reply_to_queue_manager:'str' = '',
        ) -> 'bytes':
        """ Puts one message on a queue and returns the message ID the queue manager generated.
        """

        # Describe the message, including the reply-to fields when the caller expects a reply ..
        descriptor = _MQMD()
        descriptor.StrucId = ModuleCtx.MQMD_Struc_ID
        descriptor.Version = ModuleCtx.MQMD_Version_1
        descriptor.Report = ModuleCtx.MQRO_None
        descriptor.MsgType = message_type
        descriptor.Expiry = ModuleCtx.MQEI_Unlimited
        descriptor.Feedback = ModuleCtx.MQFB_None
        descriptor.Encoding = ModuleCtx.MQENC_Native
        descriptor.CodedCharSetId = ModuleCtx.MQCCSI_UTF8
        descriptor.Format = format.encode('utf-8')
        descriptor.Priority = ModuleCtx.MQPRI_Priority_As_Q_Def
        descriptor.Persistence = ModuleCtx.MQPER_Not_Persistent
        descriptor.ReplyToQ = _pad(reply_to_queue, ModuleCtx.Queue_Name_Length)
        descriptor.ReplyToQMgr = _pad(reply_to_queue_manager, ModuleCtx.Queue_Manager_Name_Length)

        put_options = _MQPMO()
        put_options.StrucId = ModuleCtx.MQPMO_Struc_ID
        put_options.Version = ModuleCtx.MQPMO_Version_1
        put_options.Options = ModuleCtx.MQPMO_No_Syncpoint | ModuleCtx.MQPMO_New_Msg_ID | ModuleCtx.MQPMO_Fail_If_Quiescing

        # .. open the queue for output, put the message and close the queue again.
        object_handle = self._open_queue(queue, ModuleCtx.MQOO_Output | ModuleCtx.MQOO_Fail_If_Quiescing)

        buffer = ctypes.create_string_buffer(data, len(data))
        completion_code = _MQLONG(0)
        reason = _MQLONG(0)

        self.library.MQPUT(
            self.connection,
            object_handle,
            ctypes.byref(descriptor),
            ctypes.byref(put_options),
            _MQLONG(len(data)),
            buffer,
            ctypes.byref(completion_code),
            ctypes.byref(reason),
        )

        self._check('MQPUT', completion_code, reason)
        self._close_queue(object_handle)

        out = bytes(descriptor.MsgId)
        return out

# ################################################################################################################################

    def get(
        self,
        queue:'str',
        *,
        wait_ms:'int',
        correlation_id:'bytesnone' = None,
        ) -> 'mq_message_none':
        """ Gets one message off a queue, waiting up to the given interval.
        Returns None when no message arrived, otherwise the payload and the descriptor fields.
        """

        # A non-zero correlation ID in the descriptor acts as a selection filter ..
        descriptor = _MQMD()
        descriptor.StrucId = ModuleCtx.MQMD_Struc_ID
        descriptor.Version = ModuleCtx.MQMD_Version_1
        descriptor.Encoding = ModuleCtx.MQENC_Native

        if correlation_id:
            correlation_array = (ctypes.c_ubyte * 24).from_buffer_copy(correlation_id)
            descriptor.CorrelId = correlation_array

        get_options = _MQGMO()
        get_options.StrucId = ModuleCtx.MQGMO_Struc_ID
        get_options.Version = ModuleCtx.MQGMO_Version_1
        get_options.Options = ModuleCtx.MQGMO_Wait | ModuleCtx.MQGMO_No_Syncpoint | ModuleCtx.MQGMO_Fail_If_Quiescing
        get_options.WaitInterval = wait_ms

        # .. open the queue for input and wait for a matching message.
        object_handle = self._open_queue(queue, ModuleCtx.MQOO_Input_As_Q_Def | ModuleCtx.MQOO_Fail_If_Quiescing)

        buffer = ctypes.create_string_buffer(ModuleCtx.Get_Buffer_Size)
        data_length = _MQLONG(0)
        completion_code = _MQLONG(0)
        reason = _MQLONG(0)

        self.library.MQGET(
            self.connection,
            object_handle,
            ctypes.byref(descriptor),
            ctypes.byref(get_options),
            _MQLONG(ModuleCtx.Get_Buffer_Size),
            buffer,
            ctypes.byref(data_length),
            ctypes.byref(completion_code),
            ctypes.byref(reason),
        )

        self._close_queue(object_handle)

        # No message within the wait interval is a regular outcome for a test to assert on
        if reason.value == ModuleCtx.MQRC_No_Msg_Available:
            return None

        self._check('MQGET', completion_code, reason)

        payload = buffer.raw[:data_length.value]

        fields = {
            'message_id': bytes(descriptor.MsgId),
            'correlation_id': bytes(descriptor.CorrelId),
            'format': descriptor.Format.decode('utf-8').strip(),
        }

        out = (payload, fields)
        return out

# ################################################################################################################################
# ################################################################################################################################
