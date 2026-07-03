# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Type stubs for the zato_hl7v2_rs Rust extension.

# stdlib
from typing import Any

# ################################################################################################################################
# ################################################################################################################################

# Fields are nested as field -> repetition -> component -> subcomponent
Fields = list[list[list[list[str]]]]

# ################################################################################################################################
# ################################################################################################################################

class ValidationError:

    path: str
    code: str
    message: str

# ################################################################################################################################
# ################################################################################################################################

class ValidationResult:

    is_valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationError]

    def __bool__(self) -> bool: ...

# ################################################################################################################################
# ################################################################################################################################

class RawSegment:

    segment_id: str
    fields: Fields

    def set_field_value(self, field_idx:int, rep_idx:int, comp_idx:int, subcomp_idx:int, value:str) -> None: ...

# ################################################################################################################################
# ################################################################################################################################

class RawGroup:

    name: str
    items: list[Any]
    is_choice: bool

# ################################################################################################################################
# ################################################################################################################################

class RawMessage:

    structure_id: str
    items: list[Any]
    extra_segments: list[RawSegment]

    def set_segment_field(self, segment_id:str, field_idx:int, rep_idx:int, comp_idx:int, subcomp_idx:int, value:str) -> None: ...

# ################################################################################################################################
# ################################################################################################################################

class ToleranceConfig:

    normalize_obx2_value_type: bool
    replace_invalid_obx2_value_type: bool
    normalize_invalid_escape_sequences: bool
    strip_embedded_cr_from_fields: bool
    normalize_unescaped_delimiters: bool
    normalize_obx8_abnormal_flags: bool
    force_standard_delimiters: bool
    fix_off_by_one_field_index: bool
    strip_placeholder_text_from_fields: bool
    normalize_coded_field_values: bool
    normalize_quadruple_quoted_empty: bool
    allow_short_encoding_characters: bool
    placeholder_patterns: list[str]
    coded_field_mappings: dict[str, dict[str, str]]

    def __init__(self) -> None: ...

# ################################################################################################################################
# ################################################################################################################################

def parse_hl7(raw_er7:str) -> RawMessage: ...

def validate(raw_er7:str) -> ValidationResult: ...

def validate_parsed(msg:RawMessage) -> ValidationResult: ...

def serialize(msg:RawMessage) -> str: ...

def validate_datatype(datatype:str, components:list[list[str]], path:str) -> ValidationResult: ...

def validate_field_length(segment_id:str, field_num:int, value:str, path:str) -> ValidationError | None: ...

def validate_cardinality(
    structure_id:str,
    segment_counts:dict[str, int],
    group_counts:dict[str, int],
    choice_children:dict[str, list[str]],
    path:str,
) -> ValidationResult: ...

def validate_table_value(table_id:int, value:str, path:str) -> ValidationResult: ...

def is_valid_table_value(table_id:int, value:str) -> bool: ...

def get_table_codes(table_id:int) -> list[str] | None: ...

def decode_escapes(value:str, esc_char:str) -> str: ...

def encode_escapes(value:str, field_sep:str, comp_sep:str, rep_sep:str, esc_char:str, subcomp_sep:str) -> str: ...

def apply_tolerance(raw:str, tolerance:ToleranceConfig) -> str: ...

def validate_segment(segment_id:str, fields:Fields, path:str) -> ValidationResult: ...

# ################################################################################################################################
# ################################################################################################################################
