# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
from json import JSONDecodeError

# Zato
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, stranydict, strlist
    anydict = anydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# Models often wrap their reply in a fenced code block despite instructions - both fences are stripped.
_fence_json = '```json'
_fence_plain = '```'

# The confidence levels an explanation may carry.
_confidence_levels = ('low', 'medium', 'high')

# The three keys of a reply, each read off a document that does not parse as a whole - a JSON string
# with its escapes for the two texts, an object or null for the remediation. This is the external boundary,
# a model's reply, so a reading that fails leaves the reply as prose.
_key_explanation = re.compile(r'"explanation"\s*:\s*"((?:[^"\\]|\\.)*)"')
_key_confidence = re.compile(r'"confidence"\s*:\s*"((?:[^"\\]|\\.)*)"')
_key_remediation = re.compile(r'"remediation"\s*:\s*(\{[^}]*\}|null)')

# A model may fold the confidence and remediation into the prose instead of giving them keys of their own,
# as trailing lines of the form `Confidence: high` and `Remediation: null` - both are lifted out of the prose.
_trailing_confidence = re.compile(r'\n\s*confidence\s*:\s*(low|medium|high)\s*$', re.IGNORECASE)
_trailing_remediation = re.compile(r'\n\s*remediation\s*:\s*(.*?)\s*$', re.IGNORECASE)

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

def _read_json_string(escaped:'str') -> 'str':
    """ The text a JSON string literal's contents stand for - the literal read whole when its escapes
    are sound, its raw contents when they are not.
    """
    try:
        out = loads('"' + escaped + '"')
    except JSONDecodeError:
        out = escaped

    return out

# ################################################################################################################################

def _repair(data:'str') -> 'anydict | None':
    """ A second reading of a reply that did not parse whole - the three keys are read off it one by one,
    and a reply where all three come back is the object a clean reply would have parsed into.
    None when any of them is missing.
    """
    explanation_match = _key_explanation.search(data)
    confidence_match = _key_confidence.search(data)
    remediation_match = _key_remediation.search(data)

    if explanation_match is None:
        return None

    if confidence_match is None:
        return None

    if remediation_match is None:
        return None

    # The remediation is an object or null, both of which parse on their own
    try:
        remediation = loads(remediation_match.group(1))
    except JSONDecodeError:
        return None

    out = {
        'explanation': _read_json_string(explanation_match.group(1)),
        'confidence': _read_json_string(confidence_match.group(1)),
        'remediation': remediation,
    }

    return out

# ################################################################################################################################

def _lift_trailing_lines(parsed:'anydict') -> 'None':
    """ Moves a confidence and a remediation the model wrote as the prose's last lines into keys of their own,
    when the reply carries no confidence key. The remediation line is only dropped from the prose - a remediation
    written this way is never an object the skill could act on.
    """
    if 'confidence' in parsed:
        return

    explanation = parsed['explanation']

    # The remediation line, if there is one, is the very last line ..
    remediation_match = _trailing_remediation.search(explanation)

    if remediation_match:
        explanation = explanation[:remediation_match.start()].rstrip()

    # .. and the confidence line comes right before it.
    confidence_match = _trailing_confidence.search(explanation)

    if confidence_match is None:
        return

    parsed['explanation'] = explanation[:confidence_match.start()].rstrip()
    parsed['confidence'] = confidence_match.group(1).lower()

# ################################################################################################################################

def parse_explanation(text:'str', remediations:'strlist') -> 'stranydict':
    """ Parses an LLM reply into an explanation. A reply that is not the expected JSON document
    is read a second time, key by key, and one where all three keys come back parses the same
    way a clean one does. A reply that still does not parse becomes an explanation all the same -
    its full text is the explanation, with no confidence and no remediation, so a person can always
    read what the model said. A remediation is kept only when the skill of the alert's source names its action.
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

    # .. a reply that does not parse whole is read key by key, and kept as prose when that fails too ..
    try:
        parsed = loads(data)
    except JSONDecodeError:
        parsed = _repair(data)

        if parsed is None:
            return out

    # .. so is one that parses into something other than an object ..
    if not isinstance(parsed, dict):
        return out

    # .. the explanation prose is the one required field ..
    explanation = parsed.get('explanation')

    if not explanation:
        return out

    # .. a confidence and a remediation written as the prose's last lines are lifted out of it ..
    _lift_trailing_lines(parsed)

    out['explanation'] = parsed['explanation']
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
