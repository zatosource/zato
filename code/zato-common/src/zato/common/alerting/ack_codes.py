# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The negative acknowledgment codes an MLLP channel alerts on - the text a person types, `AR, CR`, parsed
# into HL7 acknowledgment codes, and the count of a channel's acks that carry one of them. The codes are the
# ones an MSA segment carries in MSA-1 - `AE` and `CE` say the service failed to process the message, `AR`
# and `CR` that the message was rejected - and nothing else is a code here, since a positive ack never
# carries an application outcome. The collector does not know the codes, it counts a channel's acks per
# code under the same key the SOAP faults use, and the sweep turns those counts into the one number the
# Negative_Acks rule reads, with the codes in force for that channel - its own or the rule's default - right
# before the rule matches.

from __future__ import annotations

# Zato
from zato.common.alerting.config_map import Ack_Codes_Default
from zato.common.alerting.fault_codes import Fault_Counts_Key

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

# The negative acknowledgment codes of HL7 v2 - the application ones and the commit ones of enhanced mode
Ack_Code_Application_Error  = 'AE'
Ack_Code_Application_Reject = 'AR'
Ack_Code_Commit_Error       = 'CE'
Ack_Code_Commit_Reject      = 'CR'

negative_ack_codes = (Ack_Code_Application_Error, Ack_Code_Application_Reject, Ack_Code_Commit_Error, Ack_Code_Commit_Reject)

# The key a fact carries the matching counts under - by code, e.g. {'AE': 2, 'AR': 1}
Ack_Code_Counts_Key = 'ack_code_counts'

# The key of a fact the sweep derives from the counts
Ack_Count_Key = 'ack_count'

# ################################################################################################################################
# ################################################################################################################################

def parse_ack_codes(text:'str') -> 'strlist':
    """ The acknowledgment codes of a comma-separated text, in their order, each once and in upper case -
    `ar, CR` gives `['AR', 'CR']`. An entry that is not a negative acknowledgment code raises ValueError.
    """

    # Our response to produce
    out:'strlist' = []

    for raw_entry in text.split(Separator):

        entry = raw_entry.strip().upper()

        # Two separators in a row, or a trailing one, name nothing
        if not entry:
            continue

        if entry not in negative_ack_codes:
            raise ValueError(f'Acknowledgment code `{entry}` is not one of {", ".join(negative_ack_codes)}')

        if entry not in out:
            out.append(entry)

    return out

# ################################################################################################################################

def count_matching_acks(ack_counts:'strintdict', codes:'strlist') -> 'strintdict':
    """ The counts of the acks that carry one of the codes, by code - an ack is matched by the code its MSA
    segment carried, so a channel naming `AR` counts `AR` acks and no others.
    """

    # Our response to produce
    out:'strintdict' = {}

    for code, count in ack_counts.items():
        if code in codes:
            out[code] = count

    return out

# ################################################################################################################################

def apply_ack_codes(fact:'stranydict', rule:'Rule', rule_values:'stranydict') -> 'stranydict':
    """ The fact as a rule reads it - for a fact carrying ack counts and a rule whose defaults hold ack codes,
    a copy of the fact with the acks matching the codes in force counted into `ack_count`, the codes being
    the channel's own when its settings name any and the rule's default otherwise. Any other fact, or a rule
    without codes, is handed back as it is.
    """
    defaults = rule.document['defaults']

    if Ack_Codes_Default not in defaults:
        return fact

    if not fact[Fault_Counts_Key]:
        return fact

    if Ack_Codes_Default in rule_values:
        text = rule_values[Ack_Codes_Default]
    else:
        text = defaults[Ack_Codes_Default]['value']

    codes = parse_ack_codes(text)
    matching = count_matching_acks(fact[Fault_Counts_Key], codes)

    # Our response to produce - the fact is shared by every rule, so the derived numbers go on a copy
    out = dict(fact)
    out[Ack_Code_Counts_Key] = matching
    out[Ack_Count_Key] = sum(matching.values())

    return out

# ################################################################################################################################
# ################################################################################################################################
