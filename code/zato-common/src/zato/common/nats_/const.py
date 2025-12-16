# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

# Protocol constants
CRLF = b'\r\n'
CRLF_LEN = 2
SPC = b' '

# Protocol operations
INFO_OP = b'INFO'
CONNECT_OP = b'CONNECT'
PUB_OP = b'PUB'
HPUB_OP = b'HPUB'
SUB_OP = b'SUB'
UNSUB_OP = b'UNSUB'
MSG_OP = b'MSG'
HMSG_OP = b'HMSG'
PING_OP = b'PING'
PONG_OP = b'PONG'
OK_OP = b'+OK'
ERR_OP = b'-ERR'

# Pre-built protocol messages
PING_CMD = PING_OP + CRLF
PONG_CMD = PONG_OP + CRLF

# Default values
Default_Host = '127.0.0.1'
Default_Port = 4222
Default_Timeout = 5.0
Default_Buffer_Size = 32768
Default_Max_Payload = 1048576
Default_Inbox_Prefix = b'_INBOX'
Default_Protocol_Version = 1
Default_Num_Replicas = 1
Default_Max_Waiting = 512
Default_Max_Ack_Pending = 1000

# Time values (in nanoseconds)
Nanoseconds_Per_Second = 1_000_000_000
Default_Ack_Wait_Ns = 30_000_000_000       # 30 seconds
Default_Duplicate_Window_Ns = 120_000_000_000  # 2 minutes

# Limit markers
No_Limit = -1

# Client info
Client_Lang = 'python3'
Client_Version = '1.0.0'

# Stream configuration defaults
Stream_Retention_Limits = 'limits'
Stream_Retention_Interest = 'interest'
Stream_Retention_WorkQueue = 'workqueue'

Stream_Storage_File = 'file'
Stream_Storage_Memory = 'memory'

Stream_Discard_Old = 'old'
Stream_Discard_New = 'new'

# Consumer configuration defaults
Consumer_Deliver_All = 'all'
Consumer_Deliver_Last = 'last'
Consumer_Deliver_New = 'new'
Consumer_Deliver_ByStartSeq = 'by_start_sequence'
Consumer_Deliver_ByStartTime = 'by_start_time'

Consumer_Ack_None = 'none'
Consumer_Ack_All = 'all'
Consumer_Ack_Explicit = 'explicit'

Consumer_Replay_Instant = 'instant'
Consumer_Replay_Original = 'original'

# Header constants
NATS_HDR_Line = b'NATS/1.0'
NATS_HDR_Line_Size = len(NATS_HDR_Line)

# Status codes
Status_No_Messages = '404'
Status_Timeout = '408'
Status_Conflict = '409'
Status_Control = '100'
Status_No_Responders = '503'

# JetStream error codes
Err_Consumer_Already_Exists = 10148

# JetStream API prefix
JS_API_Prefix = '$JS.API'

# JetStream API subjects
JS_API_Account_Info = JS_API_Prefix + '.INFO'
JS_API_Stream_Create = JS_API_Prefix + '.STREAM.CREATE.{stream}'
JS_API_Stream_Update = JS_API_Prefix + '.STREAM.UPDATE.{stream}'
JS_API_Stream_Delete = JS_API_Prefix + '.STREAM.DELETE.{stream}'
JS_API_Stream_Info = JS_API_Prefix + '.STREAM.INFO.{stream}'
JS_API_Stream_List = JS_API_Prefix + '.STREAM.LIST'
JS_API_Stream_Names = JS_API_Prefix + '.STREAM.NAMES'
JS_API_Stream_Purge = JS_API_Prefix + '.STREAM.PURGE.{stream}'
JS_API_Stream_Msg_Get = JS_API_Prefix + '.STREAM.MSG.GET.{stream}'
JS_API_Stream_Msg_Delete = JS_API_Prefix + '.STREAM.MSG.DELETE.{stream}'

JS_API_Consumer_Create = JS_API_Prefix + '.CONSUMER.CREATE.{stream}'
JS_API_Consumer_Create_Durable = JS_API_Prefix + '.CONSUMER.DURABLE.CREATE.{stream}.{consumer}'
JS_API_Consumer_Delete = JS_API_Prefix + '.CONSUMER.DELETE.{stream}.{consumer}'
JS_API_Consumer_Info = JS_API_Prefix + '.CONSUMER.INFO.{stream}.{consumer}'
JS_API_Consumer_List = JS_API_Prefix + '.CONSUMER.LIST.{stream}'
JS_API_Consumer_Msg_Next = JS_API_Prefix + '.CONSUMER.MSG.NEXT.{stream}.{consumer}'

# JetStream acknowledgments
JS_Ack = b'+ACK'
JS_Nak = b'-NAK'
JS_Progress = b'+WPI'
JS_Term = b'+TERM'

# ################################################################################################################################
# ################################################################################################################################
