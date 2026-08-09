# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import JSONDecodeError

# Zato
from zato.common.api import Incidents
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

# Models often wrap their reply in a fenced code block despite instructions - both fences are stripped.
_fence_json = '```json'
_fence_plain = '```'

# The confidence levels a diagnosis may carry.
_confidence_levels = ('low', 'medium', 'high')

# The remediation actions a diagnosis may propose - the closed catalog the approval executes from.
_allowed_actions = (Incidents.Remediation_Resubmit,)

# ################################################################################################################################
# ################################################################################################################################

def build_prompt(instructions:'str', evidence:'stranydict') -> 'str':
    """ Combines a skill's instructions with the evidence pack into the one message the LLM receives.
    """
    evidence_json = dumps(evidence, indent=2)

    out = instructions + '\n\n# Evidence\n\n' + evidence_json
    return out

# ################################################################################################################################

def _strip_fences(text:'str') -> 'str':
    """ Removes a markdown code fence wrapped around a reply, if there is one.
    """

    # Our response to produce
    out = text.strip()

    # The opening fence may name the language ..
    if out.startswith(_fence_json):
        out = out[len(_fence_json):]

    # .. or it may be bare ..
    elif out.startswith(_fence_plain):
        out = out[len(_fence_plain):]

    # .. and the closing fence is always bare.
    if out.endswith(_fence_plain):
        out = out[:-len(_fence_plain)]

    out = out.strip()
    return out

# ################################################################################################################################

def parse_diagnosis(text:'str') -> 'stranydict':
    """ Parses an LLM reply into a diagnosis. A reply that is not the expected JSON document
    still becomes a diagnosis - its full text is the diagnosis, with no confidence
    and no remediation, so a person can always read what the model said.
    """

    # Our response to produce
    out:'stranydict' = {
        'diagnosis': text,
        'confidence': '',
        'remediation': None,
        'is_parsed': False,
    }

    # Strip the markdown fence the model may have wrapped its reply in ..
    data = _strip_fences(text)

    # .. a reply that does not parse is kept as prose ..
    try:
        parsed = loads(data)
    except JSONDecodeError:
        return out

    # .. so is one that parses into something other than an object ..
    if not isinstance(parsed, dict):
        return out

    # .. the diagnosis prose is the one required field ..
    diagnosis = parsed.get('diagnosis')

    if not diagnosis:
        return out

    out['diagnosis'] = diagnosis
    out['is_parsed'] = True

    # .. an unrecognized confidence level is dropped rather than passed through ..
    confidence = parsed.get('confidence')

    if confidence in _confidence_levels:
        out['confidence'] = confidence

    # .. and a remediation is accepted only when its action is in the catalog.
    if remediation := parsed.get('remediation'):

        if isinstance(remediation, dict):

            action = remediation.get('action')

            if action in _allowed_actions:
                out['remediation'] = remediation

    return out

# ################################################################################################################################
# ################################################################################################################################
