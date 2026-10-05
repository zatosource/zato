# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# As much of the Kafka wire format as the endpoint of an outgoing Kafka connection needs - enough to read the
# messages of a produce request, to answer one with an error, to point a client at the endpoint rather than
# at the Kafka instance behind it, and to keep every client on the versions of the protocol this covers.

# stdlib
from dataclasses import dataclass, field
from struct import Struct

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anytuple, strlist

# ################################################################################################################################
# ################################################################################################################################

# The requests the endpoint takes an interest in
Api_Produce = 0
Api_Metadata = 3
Api_Versions = 18

# The highest versions the endpoint reads and writes - from here on the format changes to one with variable-length
# fields, and a client told about these versions in the reply to its version request never sends anything newer
Max_Produce_Version = 7
Max_Metadata_Version = 8

# Versions of a request whose header carries tagged fields - a version request from this one on
Api_Versions_Flexible_From = 3

# A nullable string or array that is not there
Null_Length = -1

# The compression bits of a record batch's attributes
Compression_Mask = 0x07

# The error a refused produce request is answered with - what Kafka says of a record it does not take
Error_Invalid_Record = 87

# No error at all
Error_None = 0

# The offset of a refused message, which is to say none
No_Offset = -1

# No throttling
No_Throttle = 0

_int8 = Struct('>b')
_int16 = Struct('>h')
_int32 = Struct('>i')
_int64 = Struct('>q')

# ################################################################################################################################
# ################################################################################################################################

class Reader:
    """ Reads the fixed-width fields of the wire format from a buffer, keeping its place.
    """

    def __init__(self, data:'bytes', position:'int'=0) -> 'None':
        self.data = data
        self.position = position

# ################################################################################################################################

    def _unpack(self, spec:'Struct') -> 'int':
        out:'int' = spec.unpack_from(self.data, self.position)[0]
        self.position += spec.size

        return out

# ################################################################################################################################

    def int8(self) -> 'int':
        out = self._unpack(_int8)
        return out

    def int16(self) -> 'int':
        out = self._unpack(_int16)
        return out

    def int32(self) -> 'int':
        out = self._unpack(_int32)
        return out

    def int64(self) -> 'int':
        out = self._unpack(_int64)
        return out

# ################################################################################################################################

    def take(self, length:'int') -> 'bytes':
        """ The next so many bytes as they are.
        """
        out = self.data[self.position:self.position + length]
        self.position += length

        return out

# ################################################################################################################################

    def string(self) -> 'str | None':
        """ A length-prefixed string, None when the length says there is none.
        """
        length = self.int16()

        if length == Null_Length:
            return None

        out = self.take(length).decode('utf8')
        return out

# ################################################################################################################################

    def bytes_(self) -> 'bytes | None':
        """ A length-prefixed run of bytes, None when the length says there is none.
        """
        length = self.int32()

        if length == Null_Length:
            return None

        out = self.take(length)
        return out

# ################################################################################################################################

    def varint(self) -> 'int':
        """ A zig-zag encoded signed integer of variable length, as records use throughout.
        """
        shift = 0
        value = 0

        while True:
            byte = self.data[self.position]
            self.position += 1

            value |= (byte & 0x7f) << shift
            shift += 7

            if not byte & 0x80:
                break

        out = (value >> 1) ^ -(value & 1)
        return out

# ################################################################################################################################

    def unsigned_varint(self) -> 'int':
        """ An unsigned integer of variable length, as the counts of the newer format use.
        """
        shift = 0
        out = 0

        while True:
            byte = self.data[self.position]
            self.position += 1

            out |= (byte & 0x7f) << shift
            shift += 7

            if not byte & 0x80:
                break

        return out

# ################################################################################################################################

    def rest(self) -> 'bytes':
        """ Everything from here to the end.
        """
        out = self.data[self.position:]
        self.position = len(self.data)

        return out

# ################################################################################################################################
# ################################################################################################################################

def int16(value:'int') -> 'bytes':
    out = _int16.pack(value)
    return out

def int32(value:'int') -> 'bytes':
    out = _int32.pack(value)
    return out

def int64(value:'int') -> 'bytes':
    out = _int64.pack(value)
    return out

# ################################################################################################################################

def string(value:'str') -> 'bytes':
    """ A length-prefixed string.
    """
    encoded = value.encode('utf8')
    out = int16(len(encoded)) + encoded

    return out

# ################################################################################################################################

def frame(payload:'bytes') -> 'bytes':
    """ A payload behind the length every message on the wire opens with.
    """
    out = int32(len(payload)) + payload
    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class RequestHeader:
    """ What every request opens with.
    """
    api_key: int
    api_version: int
    correlation_id: int

    # Where the request's body starts
    body_position: int

# ################################################################################################################################

def read_request_header(payload:'bytes') -> 'RequestHeader':
    """ Reads a request's header - the kind of request, its version and the id its answer will carry. Only a version
    request can be of a version whose header has tagged fields, since every other kind is held below that.
    """
    reader = Reader(payload)

    api_key = reader.int16()
    api_version = reader.int16()
    correlation_id = reader.int32()

    _ = reader.string() # The client id

    if api_key == Api_Versions and api_version >= Api_Versions_Flexible_From:
        _skip_tagged_fields(reader)

    out = RequestHeader(api_key, api_version, correlation_id, reader.position)
    return out

# ################################################################################################################################

def _skip_tagged_fields(reader:'Reader') -> 'None':
    """ Steps over the tagged fields of the newer header format.
    """
    count = reader.unsigned_varint()

    for _ in range(count):
        _ = reader.unsigned_varint() # The tag
        length = reader.unsigned_varint()
        _ = reader.take(length)

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ProducedRecord:
    """ One record of a produce request - its value, its key and its headers, each as bytes or None.
    """
    topic: str
    partition: int
    key: 'bytes | None'
    value: 'bytes | None'
    headers: 'list[anytuple]' = field(default_factory=list)

# ################################################################################################################################

@dataclass
class ProduceRequest:
    """ A produce request as far as the endpoint reads it - what it carries and what it needs to be answered.
    """
    acks: int
    records: 'list[ProducedRecord]'

    # Every topic and partition the request writes to, in order, which is what an answer lists
    partitions: 'list[tuple[str, int]]'

# ################################################################################################################################

def read_produce_request(payload:'bytes', body_position:'int') -> 'ProduceRequest':
    """ Reads the records a produce request carries.
    """
    reader = Reader(payload, body_position)

    _ = reader.string() # The transactional id
    acks = reader.int16()
    _ = reader.int32() # The timeout

    records:'list[ProducedRecord]' = []
    partitions:'list[tuple[str, int]]' = []

    topic_count = reader.int32()

    for _ in range(topic_count):
        topic = reader.string() or ''
        partition_count = reader.int32()

        for _ in range(partition_count):
            partition = reader.int32()
            batches = reader.bytes_()

            partitions.append((topic, partition))

            if batches:
                records.extend(_read_record_batches(topic, partition, batches))

    out = ProduceRequest(acks, records, partitions)
    return out

# ################################################################################################################################

def _read_record_batches(topic:'str', partition:'int', data:'bytes') -> 'list[ProducedRecord]':
    """ Reads every record of every batch written to one partition.
    """
    out:'list[ProducedRecord]' = []
    reader = Reader(data)

    while reader.position < len(data):

        _ = reader.int64() # The base offset
        batch_length = reader.int32()
        batch_end = reader.position + batch_length

        _ = reader.int32() # The partition leader epoch
        _ = reader.int8()  # The magic byte
        _ = reader.int32() # The checksum

        attributes = reader.int16()

        if attributes & Compression_Mask:
            raise ValueError(f'A compressed batch cannot be read, attributes {attributes:#x}')

        _ = reader.int32() # The last offset delta
        _ = reader.int64() # The base timestamp
        _ = reader.int64() # The max timestamp
        _ = reader.int64() # The producer id
        _ = reader.int16() # The producer epoch
        _ = reader.int32() # The base sequence

        record_count = reader.int32()

        for _ in range(record_count):
            out.append(_read_record(topic, partition, reader))

        reader.position = batch_end

    return out

# ################################################################################################################################

def _read_record(topic:'str', partition:'int', reader:'Reader') -> 'ProducedRecord':
    """ Reads one record of a batch.
    """
    _ = reader.varint() # The record's length
    _ = reader.int8()   # The record's attributes
    _ = reader.varint() # The timestamp delta
    _ = reader.varint() # The offset delta

    key = _read_varint_bytes(reader)
    value = _read_varint_bytes(reader)

    headers:'list[anytuple]' = []
    header_count = reader.varint()

    for _ in range(header_count):
        name = _read_varint_bytes(reader) or b''
        header_value = _read_varint_bytes(reader)
        headers.append((name.decode('utf8'), header_value))

    out = ProducedRecord(topic, partition, key, value, headers)
    return out

# ################################################################################################################################

def _read_varint_bytes(reader:'Reader') -> 'bytes | None':
    """ A run of bytes behind a variable-length count, None when the count says there is none.
    """
    length = reader.varint()

    if length < 0:
        return None

    out = reader.take(length)
    return out

# ################################################################################################################################

def build_produce_response(correlation_id:'int', partitions:'list[tuple[str, int]]', error_code:'int') -> 'bytes':
    """ An answer to a produce request that gives every partition it wrote to the same error - what the endpoint
    sends when it refuses the request, framed and ready for the wire.
    """
    by_topic:'dict[str, list[int]]' = {}

    for topic, partition in partitions:
        by_topic.setdefault(topic, []).append(partition)

    body = int32(correlation_id)
    body += int32(len(by_topic))

    for topic, partition_list in by_topic.items():
        body += string(topic)
        body += int32(len(partition_list))

        for partition in partition_list:
            body += int32(partition)
            body += int16(error_code)
            body += int64(No_Offset) # The base offset
            body += int64(No_Offset) # The append time
            body += int64(No_Offset) # The log start offset

    body += int32(No_Throttle)

    out = frame(body)
    return out

# ################################################################################################################################
# ################################################################################################################################

def is_metadata_request_for_everything(payload:'bytes', body_position:'int') -> 'bool':
    """ Whether a metadata request asks about every topic there is - what a ping does, and what nothing a client
    does on its own ever asks for, since a client only ever names the topics it knows.
    """
    reader = Reader(payload, body_position)
    topic_count = reader.int32()

    out = topic_count == Null_Length
    return out

# ################################################################################################################################

def rewrite_metadata_response(payload:'bytes', host:'str', port:'int') -> 'bytes':
    """ Points every Kafka instance a metadata response lists at the endpoint instead, so a client keeps
    talking through it rather than to the instance behind it. Everything else is kept as it was.
    """
    reader = Reader(payload)

    out = int32(reader.int32()) # The correlation id
    out += int32(reader.int32()) # The throttle time

    instance_count = reader.int32()
    out += int32(instance_count)

    for _ in range(instance_count):
        out += int32(reader.int32()) # The node id

        _ = reader.string()
        _ = reader.int32()

        out += string(host)
        out += int32(port)

        rack = reader.string()

        if rack is None:
            out += int16(Null_Length)
        else:
            out += string(rack)

    out += reader.rest()

    return out

# ################################################################################################################################
# ################################################################################################################################

def cap_api_versions_response(payload:'bytes', request_version:'int') -> 'bytes':
    """ Lowers the highest versions a reply to a version request offers for the requests this module reads and
    writes, so that a client never sends them in a newer format. Every field keeps its width, so the reply is
    patched in place.
    """
    data = bytearray(payload)
    reader = Reader(payload)

    _ = reader.int32() # The correlation id
    error_code = reader.int16()

    # A reply that is an error lists nothing to cap
    if error_code != Error_None:
        return payload

    is_flexible = request_version >= Api_Versions_Flexible_From

    if is_flexible:
        count = reader.unsigned_varint() - 1
    else:
        count = reader.int32()

    for _ in range(count):
        api_key = reader.int16()
        _ = reader.int16() # The lowest version

        max_position = reader.position
        max_version = reader.int16()

        cap = _version_cap(api_key)

        if cap is not None and max_version > cap:
            data[max_position:max_position + _int16.size] = int16(cap)

        if is_flexible:
            _skip_tagged_fields(reader)

    out = bytes(data)
    return out

# ################################################################################################################################

def _version_cap(api_key:'int') -> 'int | None':
    """ The highest version this module reads and writes of a kind of request, None for one it leaves alone.
    """
    if api_key == Api_Produce:
        return Max_Produce_Version

    if api_key == Api_Metadata:
        return Max_Metadata_Version

    return None

# ################################################################################################################################
# ################################################################################################################################

def describe_records(records:'list[ProducedRecord]') -> 'strlist':
    """ The values of records as text, for log lines.
    """
    out = []

    for record in records:
        if record.value is None:
            out.append('<tombstone>')
        else:
            out.append(record.value.decode('utf8', errors='replace'))

    return out

# ################################################################################################################################
# ################################################################################################################################
