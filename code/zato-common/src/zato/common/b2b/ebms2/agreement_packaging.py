# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SimplePart:
    part_id:         str
    mime_type:       str
    mime_parameters: str = ''
    role:            str = ''

# ################################################################################################################################

@dataclass(init=False)
class Constituent:
    idref:                   str
    excluded_from_signature: str = ''
    min_occurs:              str = ''
    max_occurs:              str = ''

constituent_list = list[Constituent]

# ################################################################################################################################

@dataclass(init=False)
class CompositeItem:
    """ A Composite or an Encapsulation of a packaging composite list.
    """
    kind:            str
    item_id:         str
    mime_type:       str
    mime_parameters: str = ''
    constituents:    'constituent_list'

    def __init__(self) -> 'None':
        self.constituents = []

composite_item_list = list[CompositeItem]
composite_list_list = list[composite_item_list]

# ################################################################################################################################

@dataclass(init=False)
class Packaging:
    packaging_id:    str
    parse:           str
    generate:        str
    composite_lists: 'composite_list_list'

    def __init__(self) -> 'None':
        self.composite_lists = []

# ################################################################################################################################

@dataclass(init=False)
class Comment:
    text:     str
    language: str = ''

# ################################################################################################################################

simple_part_list = list[SimplePart]
packaging_list = list[Packaging]
comment_list = list[Comment]

# ################################################################################################################################
# ################################################################################################################################
