"""
HL7 v2 Batch and File support.

Provides classes for parsing and creating HL7 batch (BHS/BTS) and file (FHS/FTS) wrappers.

Structure:
    FHS|...          <- File Header (optional)
    BHS|...          <- Batch Header
    MSH|...(msg 1)...
    MSH|...(msg 2)...
    BTS|2            <- Batch Trailer (message count)
    FTS|1            <- File Trailer (batch count)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterator, List, Optional, Any

from zato_hl7v2.base import HL7Message


@dataclass
class HL7Batch:
    """Represents an HL7 batch containing multiple messages wrapped by BHS/BTS segments."""

    messages: List[HL7Message] = field(default_factory=list)
    bhs_raw: Optional[str] = None
    bts_raw: Optional[str] = None

    @property
    def message_count(self) -> int:
        return len(self.messages)

    def __iter__(self) -> Iterator[HL7Message]:
        return iter(self.messages)

    def __len__(self) -> int:
        return len(self.messages)

    def __getitem__(self, index: int) -> HL7Message:
        return self.messages[index]

    def append(self, msg: HL7Message) -> None:
        self.messages.append(msg)

    def serialize(self) -> str:
        from zato_hl7v2.v2_9 import serialize
        parts = []
        if self.bhs_raw:
            parts.append(self.bhs_raw)
        for msg in self.messages:
            parts.append(serialize(msg))
        bts = self.bts_raw if self.bts_raw else f"BTS|{len(self.messages)}"
        parts.append(bts)
        return "\r".join(parts)

    to_hl7 = serialize
    to_er7 = serialize


@dataclass
class HL7File:
    """Represents an HL7 file containing multiple batches wrapped by FHS/FTS segments."""

    batches: List[HL7Batch] = field(default_factory=list)
    fhs_raw: Optional[str] = None
    fts_raw: Optional[str] = None

    @property
    def batch_count(self) -> int:
        return len(self.batches)

    @property
    def message_count(self) -> int:
        return sum(batch.message_count for batch in self.batches)

    @property
    def messages(self) -> Iterator[HL7Message]:
        for batch in self.batches:
            yield from batch.messages

    def __iter__(self) -> Iterator[HL7Batch]:
        return iter(self.batches)

    def __len__(self) -> int:
        return len(self.batches)

    def __getitem__(self, index: int) -> HL7Batch:
        return self.batches[index]

    def append(self, batch: HL7Batch) -> None:
        self.batches.append(batch)

    def serialize(self) -> str:
        parts = []
        if self.fhs_raw:
            parts.append(self.fhs_raw)
        for batch in self.batches:
            parts.append(batch.serialize())
        fts = self.fts_raw if self.fts_raw else f"FTS|{len(self.batches)}"
        parts.append(fts)
        return "\r".join(parts)

    to_hl7 = serialize
    to_er7 = serialize


def _split_segments(raw: str) -> List[str]:
    """Split raw HL7 content into individual segment strings."""
    normalized = raw.replace("\r\n", "\r").replace("\n", "\r")
    segments = [s.strip() for s in normalized.split("\r") if s.strip()]
    return segments


def _get_segment_id(segment: str) -> str:
    """Extract segment ID from a segment string."""
    if "|" in segment:
        return segment.split("|")[0]
    return segment[:3] if len(segment) >= 3 else segment


def parse_batch(raw: str, validate: bool = True) -> HL7Batch:
    """
    Parse an HL7 batch (BHS...BTS) into an HL7Batch object.

    The input should start with BHS and end with BTS.
    Messages within the batch are delimited by MSH segments.

    Args:
        raw: Raw HL7 batch string
        validate: If True, validate messages during parsing

    Returns:
        HL7Batch containing parsed messages

    Raises:
        ValueError: If batch structure is invalid
    """
    from zato_hl7v2.v2_9 import parse_message

    segments = _split_segments(raw)
    if not segments:
        raise ValueError("Empty batch")

    first_seg_id = _get_segment_id(segments[0])

    if first_seg_id == "FHS":
        raise ValueError("Input contains FHS header - use parse_file() instead")

    if first_seg_id != "BHS":
        raise ValueError(f"Batch must start with BHS segment, found: {first_seg_id}")

    batch = HL7Batch()
    batch.bhs_raw = segments[0]

    current_message_segments: List[str] = []
    in_message = False

    for segment in segments[1:]:
        seg_id = _get_segment_id(segment)

        if seg_id == "BTS":
            if in_message and current_message_segments:
                msg_raw = "\r".join(current_message_segments)
                batch.messages.append(parse_message(msg_raw, validate=validate))
            batch.bts_raw = segment
            break
        elif seg_id == "MSH":
            if in_message and current_message_segments:
                msg_raw = "\r".join(current_message_segments)
                batch.messages.append(parse_message(msg_raw, validate=validate))
            current_message_segments = [segment]
            in_message = True
        else:
            if in_message:
                current_message_segments.append(segment)

    return batch


def parse_file(raw: str, validate: bool = True) -> HL7File:
    """
    Parse an HL7 file (FHS...FTS) into an HL7File object.

    The input should start with FHS and end with FTS.
    The file may contain multiple batches, each wrapped by BHS/BTS.

    Args:
        raw: Raw HL7 file string
        validate: If True, validate messages during parsing

    Returns:
        HL7File containing parsed batches and messages

    Raises:
        ValueError: If file structure is invalid
    """
    from zato_hl7v2.v2_9 import parse_message

    segments = _split_segments(raw)
    if not segments:
        raise ValueError("Empty file")

    first_seg_id = _get_segment_id(segments[0])

    if first_seg_id == "BHS":
        raise ValueError("Input contains BHS header without FHS - use parse_batch() instead")

    if first_seg_id != "FHS":
        raise ValueError(f"File must start with FHS segment, found: {first_seg_id}")

    hl7_file = HL7File()
    hl7_file.fhs_raw = segments[0]

    current_batch: Optional[HL7Batch] = None
    current_message_segments: List[str] = []
    in_message = False

    for segment in segments[1:]:
        seg_id = _get_segment_id(segment)

        if seg_id == "FTS":
            if current_batch is not None:
                if in_message and current_message_segments:
                    msg_raw = "\r".join(current_message_segments)
                    current_batch.messages.append(parse_message(msg_raw, validate=validate))
                hl7_file.batches.append(current_batch)
            hl7_file.fts_raw = segment
            break
        elif seg_id == "BHS":
            if current_batch is not None:
                if in_message and current_message_segments:
                    msg_raw = "\r".join(current_message_segments)
                    current_batch.messages.append(parse_message(msg_raw, validate=validate))
                hl7_file.batches.append(current_batch)
            current_batch = HL7Batch()
            current_batch.bhs_raw = segment
            current_message_segments = []
            in_message = False
        elif seg_id == "BTS":
            if current_batch is not None:
                if in_message and current_message_segments:
                    msg_raw = "\r".join(current_message_segments)
                    current_batch.messages.append(parse_message(msg_raw, validate=validate))
                current_batch.bts_raw = segment
                hl7_file.batches.append(current_batch)
                current_batch = None
                current_message_segments = []
                in_message = False
        elif seg_id == "MSH":
            if in_message and current_message_segments and current_batch is not None:
                msg_raw = "\r".join(current_message_segments)
                current_batch.messages.append(parse_message(msg_raw, validate=validate))
            current_message_segments = [segment]
            in_message = True
        else:
            if in_message:
                current_message_segments.append(segment)

    return hl7_file


def parse_batch_or_file(raw: str, validate: bool = True) -> HL7Batch | HL7File:
    """
    Parse raw HL7 content, automatically detecting if it's a batch or file.

    Args:
        raw: Raw HL7 content
        validate: If True, validate messages during parsing

    Returns:
        HL7Batch or HL7File depending on content

    Raises:
        ValueError: If content is neither a valid batch nor file
    """
    segments = _split_segments(raw)
    if not segments:
        raise ValueError("Empty content")

    first_seg_id = _get_segment_id(segments[0])

    if first_seg_id == "FHS":
        return parse_file(raw, validate=validate)
    elif first_seg_id == "BHS":
        return parse_batch(raw, validate=validate)
    else:
        raise ValueError(f"Content must start with FHS or BHS, found: {first_seg_id}")


def create_batch(
    messages: List[HL7Message],
    bhs_fields: Optional[dict] = None,
) -> HL7Batch:
    """
    Create a new HL7Batch from a list of messages.

    Args:
        messages: List of HL7Message objects to include in the batch
        bhs_fields: Optional dict of BHS field values

    Returns:
        HL7Batch ready for serialization
    """
    batch = HL7Batch()
    batch.messages = list(messages)

    bhs_parts = ["BHS", "^~\\&"]
    if bhs_fields:
        for i in range(3, 15):
            field_name = f"bhs_{i}"
            value = bhs_fields.get(field_name, "")
            bhs_parts.append(str(value) if value else "")

    batch.bhs_raw = "|".join(bhs_parts)
    batch.bts_raw = f"BTS|{len(messages)}"

    return batch


def create_file(
    batches: List[HL7Batch],
    fhs_fields: Optional[dict] = None,
) -> HL7File:
    """
    Create a new HL7File from a list of batches.

    Args:
        batches: List of HL7Batch objects to include in the file
        fhs_fields: Optional dict of FHS field values

    Returns:
        HL7File ready for serialization
    """
    hl7_file = HL7File()
    hl7_file.batches = list(batches)

    fhs_parts = ["FHS", "^~\\&"]
    if fhs_fields:
        for i in range(3, 15):
            field_name = f"fhs_{i}"
            value = fhs_fields.get(field_name, "")
            fhs_parts.append(str(value) if value else "")

    hl7_file.fhs_raw = "|".join(fhs_parts)
    hl7_file.fts_raw = f"FTS|{len(batches)}"

    return hl7_file
