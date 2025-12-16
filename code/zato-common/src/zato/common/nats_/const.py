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

# Header constants
NATS_HDR_Line = b'NATS/1.0'
NATS_HDR_Line_Size = len(NATS_HDR_Line)
No_Responders_Status = '503'
Ctrl_Status = '100'

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
