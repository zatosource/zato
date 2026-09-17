# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The OperationOutcome issue codes an outgoing FHIR connection alerts on - the text a person types,
# `exception, timeout`, parsed into FHIR IssueType codes, and the count of a connection's outcomes that carry
# one of them. The codes are the ones the OperationOutcome resource carries in `issue.code` - lowercase names
# with dashes, `exception`, `not-found`, `too-costly`. The collector does not know the codes, it counts a
# connection's outcomes per code under the same key the SOAP faults use, and the sweep turns those counts into
# the one number the Operation_Outcomes rule reads, with the codes in force for that connection - its own or
# the rule's default - right before the rule matches.

from __future__ import annotations

# Zato
from zato.common.alerting.config_map import Outcome_Codes_Default
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

# What an issue code is made of after its first letter - lowercase letters and dashes, `not-found`
Code_Extra_Chars = '-'

# The key a fact carries the matching counts under - by code, e.g. {'exception': 2, 'timeout': 1}
Outcome_Code_Counts_Key = 'outcome_code_counts'

# The key of a fact the sweep derives from the counts
Outcome_Count_Key = 'outcome_count'

# ################################################################################################################################
# ################################################################################################################################

def _is_code(text:'str') -> 'bool':
    """ Whether a text is one FHIR issue code - lowercase letters with dashes between them, starting with a letter.
    """
    if not text:
        return False

    first = text[0]

    if not (first.isalpha() and first.islower()):
        return False

    for char in text:
        if not ((char.isalpha() and char.islower()) or char in Code_Extra_Chars):
            return False

    return True

# ################################################################################################################################

def parse_outcome_codes(text:'str') -> 'strlist':
    """ The issue codes of a comma-separated text, in their order, each once - `exception, not-found`
    gives `['exception', 'not-found']`. An entry that is not an issue code raises ValueError.
    """

    # Our response to produce
    out:'strlist' = []

    for raw_entry in text.split(Separator):

        entry = raw_entry.strip()

        # Two separators in a row, or a trailing one, name nothing
        if not entry:
            continue

        if not _is_code(entry):
            raise ValueError(f'Outcome code `{entry}` is not a FHIR issue code such as exception or not-found')

        if entry not in out:
            out.append(entry)

    return out

# ################################################################################################################################

def count_matching_outcomes(outcome_counts:'strintdict', codes:'strlist') -> 'strintdict':
    """ The counts of the outcomes that carry one of the codes, by code - an outcome is matched by its issue
    code as the resource carried it, so a connection naming `exception` counts `exception` outcomes and no others.
    """

    # Our response to produce
    out:'strintdict' = {}

    for code, count in outcome_counts.items():
        if code in codes:
            out[code] = count

    return out

# ################################################################################################################################

def apply_outcome_codes(fact:'stranydict', rule:'Rule', rule_values:'stranydict') -> 'stranydict':
    """ The fact as a rule reads it - for a fact carrying outcome counts and a rule whose defaults hold outcome codes,
    a copy of the fact with the outcomes matching the codes in force counted into `outcome_count`, the codes being
    the connection's own when its settings name any and the rule's default otherwise. Any other fact, or a rule
    without codes, is handed back as it is.
    """
    defaults = rule.document['defaults']

    if Outcome_Codes_Default not in defaults:
        return fact

    if not fact[Fault_Counts_Key]:
        return fact

    if Outcome_Codes_Default in rule_values:
        text = rule_values[Outcome_Codes_Default]
    else:
        text = defaults[Outcome_Codes_Default]['value']

    codes = parse_outcome_codes(text)
    matching = count_matching_outcomes(fact[Fault_Counts_Key], codes)

    # Our response to produce - the fact is shared by every rule, so the derived numbers go on a copy
    out = dict(fact)
    out[Outcome_Code_Counts_Key] = matching
    out[Outcome_Count_Key] = sum(matching.values())

    return out

# ################################################################################################################################
# ################################################################################################################################
