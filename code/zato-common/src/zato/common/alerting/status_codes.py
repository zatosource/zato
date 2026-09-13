# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The status codes an outgoing connection alerts on - the text a person types, `401, 403, 5xx`, parsed
# into codes and classes, and the count of a connection's responses that carry one of them. The collector
# does not know the codes, it counts a connection's responses per code, and the sweep turns those counts
# into the one number the Status_Codes rule reads, with the codes in force for that connection - its own
# or the rule's default - right before the rule matches.

from __future__ import annotations

# Zato
from zato.common.alerting.config_map import Status_Codes_Default

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.models import Rule
    from zato.common.typing_ import stranydict, strintdict, strlist
    Rule = Rule
    stranydict = stranydict
    strintdict = strintdict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# A code is three digits, `401`, and a class is its first digit followed by the class suffix, `4xx`
Status_Code_Length = 3
Class_Suffix = 'xx'

# The classes HTTP has - a first digit outside these names nothing
First_Class_Digit = '1'
Last_Class_Digit = '5'

# What the entries of the text are separated by
Separator = ','

# The key a fact carries the matching counts under - by code, e.g. {'401': 2, '503': 1}
Status_Code_Counts_Key = 'status_code_counts'

# The keys of a fact the sweep derives from the counts
Status_Counts_Key = 'status_counts'
Status_Code_Count_Key = 'status_code_count'

# ################################################################################################################################
# ################################################################################################################################

def _is_class_digit(digit:'str') -> 'bool':
    """ Whether a single character is the first digit of one of the HTTP status classes.
    """
    if not digit.isdigit():
        return False

    out = First_Class_Digit <= digit <= Last_Class_Digit
    return out

# ################################################################################################################################

def _parse_entry(entry:'str') -> 'str':
    """ One entry of the text as a code or a class - `401` and `4xx` pass, `40`, `6xx` and words do not.
    """
    if len(entry) != Status_Code_Length:
        raise ValueError(f'Status code `{entry}` is not a three-digit code or a class such as 5xx')

    if not _is_class_digit(entry[0]):
        raise ValueError(f'Status code `{entry}` does not start with a digit from {First_Class_Digit} to {Last_Class_Digit}')

    rest = entry[1:]

    if rest.isdigit():
        out = entry
    elif rest.lower() == Class_Suffix:
        out = entry[0] + Class_Suffix
    else:
        raise ValueError(f'Status code `{entry}` is not a three-digit code or a class such as 5xx')

    return out

# ################################################################################################################################

def parse_status_codes(text:'str') -> 'strlist':
    """ The codes and classes of a comma-separated text, in their order, each once - `401, 403, 4xx, 5xx`
    gives `['401', '403', '4xx', '5xx']`. An entry that is neither a three-digit code nor a class raises ValueError.
    """

    # Our response to produce
    out:'strlist' = []

    for raw_entry in text.split(Separator):

        entry = raw_entry.strip()

        # Two separators in a row, or a trailing one, name nothing
        if not entry:
            continue

        code = _parse_entry(entry)

        if code not in out:
            out.append(code)

    return out

# ################################################################################################################################

def is_matching(code:'str', codes:'strlist') -> 'bool':
    """ Whether a three-digit status code is one of the given codes or falls into one of the given classes.
    """
    if code in codes:
        return True

    status_class = code[0] + Class_Suffix
    out = status_class in codes

    return out

# ################################################################################################################################

def count_matching(status_counts:'strintdict', codes:'strlist') -> 'strintdict':
    """ The counts of the responses that carry one of the codes, by code - a response counted under `401`
    is not counted again under `4xx`, because it is the codes that are matched, one per response.
    """

    # Our response to produce
    out:'strintdict' = {}

    for code, count in status_counts.items():
        if is_matching(code, codes):
            out[code] = count

    return out

# ################################################################################################################################

def apply_status_codes(fact:'stranydict', rule:'Rule', rule_values:'stranydict') -> 'stranydict':
    """ The fact as a rule reads it - for a fact carrying status counts and a rule whose defaults hold status codes,
    a copy of the fact with the responses matching the codes in force counted into `status_code_count`, the codes
    being the connection's own when its settings name any and the rule's default otherwise. Any other fact,
    or a rule without codes, is handed back as it is.
    """
    defaults = rule.document['defaults']

    if Status_Codes_Default not in defaults:
        return fact

    if not fact[Status_Counts_Key]:
        return fact

    if Status_Codes_Default in rule_values:
        text = rule_values[Status_Codes_Default]
    else:
        text = defaults[Status_Codes_Default]['value']

    codes = parse_status_codes(text)
    matching = count_matching(fact[Status_Counts_Key], codes)

    # Our response to produce - the fact is shared by every rule, so the derived numbers go on a copy
    out = dict(fact)
    out[Status_Code_Counts_Key] = matching
    out[Status_Code_Count_Key] = sum(matching.values())

    return out

# ################################################################################################################################
# ################################################################################################################################
