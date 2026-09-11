# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import JSONDecodeError

# Zato
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# Models often wrap their reply in a fenced code block despite instructions - both fences are stripped.
_fence_json = '```json'
_fence_plain = '```'

# The confidence levels an explanation may carry.
_confidence_levels = ('low', 'medium', 'high')

# ################################################################################################################################
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

def parse_explanation(text:'str', remediations:'strlist') -> 'stranydict':
    """ Parses an LLM reply into an explanation. A reply that is not the expected JSON document
    still becomes an explanation - its full text is the explanation, with no confidence
    and no remediation, so a person can always read what the model said. A remediation
    is kept only when the skill of the alert's source names its action.
    """

    # Our response to produce
    out:'stranydict' = {
        'explanation': text,
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

    # .. the explanation prose is the one required field ..
    explanation = parsed.get('explanation')

    if not explanation:
        return out

    out['explanation'] = explanation
    out['is_parsed'] = True

    # .. an unrecognized confidence level is dropped rather than passed through ..
    confidence = parsed.get('confidence')

    if confidence in _confidence_levels:
        out['confidence'] = confidence

    # .. and a remediation is accepted only when its action is one the skill allows.
    if remediation := parsed.get('remediation'):

        if isinstance(remediation, dict):

            action = remediation.get('action')

            if action in remediations:
                out['remediation'] = remediation

    return out

# ################################################################################################################################
# ################################################################################################################################
