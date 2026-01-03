# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from dataclasses import dataclass, field

@dataclass
class ContentRow:
    label: str
    widget: str
    value_key: str
    element_id: str = ''
    default_text: str = ''
    is_copyable: bool = False
    copy_id: str = ''
    spinner: bool = False
    options: list = field(default_factory=list)
    input_width: str = '100%'
