# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The SOAP fault codes an outgoing SOAP connection alerts on - the text a person types, `Receiver, Server`,
# parsed into fault code names, and the count of a connection's faults that carry one of them. The names are
# the ones the envelope carries, as the SOAP client hands them over - the standard local names of either version,
# `Sender`, `Receiver`, `Client`, `Server`, `VersionMismatch`, `MustUnderstand`, `DataEncodingUnknown`, and
# an endpoint's own code with its prefix, `x:Timeout`. The collector does not know the codes, it counts a
# connection's faults per code, and the sweep turns those counts into the one number the SOAP_Faults rule
# reads, with the codes in force for that connection - its own or the rule's default - right before the rule matches.

from __future__ import annotations

# Zato
from zato.common.alerting.config_map import Fault_Codes_Default

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

# What the entries of the text are separated by
Separator = ','

# An endpoint's own code is written with its prefix, `x:Timeout` - one colon, a name on each side
Prefix_Separator = ':'

# What a fault code name is made of - letters, digits, dots, dashes and underscores, the way an XML name is
Name_Extra_Chars = '._-'

# The key a fact carries the matching counts under - by code, e.g. {'Receiver': 2, 'Sender': 1}
Fault_Code_Counts_Key = 'fault_code_counts'

# The keys of a fact the sweep derives from the counts
Fault_Counts_Key = 'fault_counts'
Fault_Count_Key = 'fault_count'

# ################################################################################################################################
# ################################################################################################################################

def _is_name(text:'str') -> 'bool':
    """ Whether a text is one fault code name - letters and digits with dots, dashes and underscores between them,
    starting with a letter or an underscore, the way an XML local name does.
    """
    if not text:
        return False

    first = text[0]

    if not (first.isalpha() or first == '_'):
        return False

    for char in text:
        if not (char.isalnum() or char in Name_Extra_Chars):
            return False

    return True

# ################################################################################################################################

def _parse_entry(entry:'str') -> 'str':
    """ One entry of the text as a fault code - `Receiver` and `x:Timeout` pass, `500`, `Not Found` and `:Timeout` do not.
    """
    parts = entry.split(Prefix_Separator)

    # A name alone, or a prefix and a name - anything with more colons is not a code
    if len(parts) > 2:
        raise ValueError(f'Fault code `{entry}` is not a name such as Receiver or a prefixed one such as x:Timeout')

    for part in parts:
        if not _is_name(part):
            raise ValueError(f'Fault code `{entry}` is not a name such as Receiver or a prefixed one such as x:Timeout')

    out = entry
    return out

# ################################################################################################################################

def parse_fault_codes(text:'str') -> 'strlist':
    """ The fault codes of a comma-separated text, in their order, each once - `Receiver, Server, x:Timeout`
    gives `['Receiver', 'Server', 'x:Timeout']`. An entry that is not a fault code name raises ValueError.
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

def count_matching_faults(fault_counts:'strintdict', codes:'strlist') -> 'strintdict':
    """ The counts of the faults that carry one of the codes, by code - a fault is matched by its code as the
    envelope carried it, so a connection naming `Receiver` counts `Receiver` faults and no others.
    """

    # Our response to produce
    out:'strintdict' = {}

    for code, count in fault_counts.items():
        if code in codes:
            out[code] = count

    return out

# ################################################################################################################################

def apply_fault_codes(fact:'stranydict', rule:'Rule', rule_values:'stranydict') -> 'stranydict':
    """ The fact as a rule reads it - for a fact carrying fault counts and a rule whose defaults hold fault codes,
    a copy of the fact with the faults matching the codes in force counted into `fault_count`, the codes being
    the connection's own when its settings name any and the rule's default otherwise. Any other fact, or a rule
    without codes, is handed back as it is.
    """
    defaults = rule.document['defaults']

    if Fault_Codes_Default not in defaults:
        return fact

    if not fact[Fault_Counts_Key]:
        return fact

    if Fault_Codes_Default in rule_values:
        text = rule_values[Fault_Codes_Default]
    else:
        text = defaults[Fault_Codes_Default]['value']

    codes = parse_fault_codes(text)
    matching = count_matching_faults(fact[Fault_Counts_Key], codes)

    # Our response to produce - the fact is shared by every rule, so the derived numbers go on a copy
    out = dict(fact)
    out[Fault_Code_Counts_Key] = matching
    out[Fault_Count_Key] = sum(matching.values())

    return out

# ################################################################################################################################
# ################################################################################################################################
