# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy

# Zato
from zato.common.typing_ import any_
from zato.common.util.safeguards.common import Kind_Markup, Kind_Unicode, Kind_Url, Mode_Reject, SafeguardConfig, \
    SafeguardResult, Url_Mode_Reject
from zato.common.util.safeguards.markup import sanitize_markup
from zato.common.util.safeguards.noise import collapse_whitespace, strip_base64, strip_nulls
from zato.common.util.safeguards.pii import remove_pii
from zato.common.util.safeguards.unicode_ import normalize_unicode
from zato.common.util.safeguards.urls import apply_url_policy
from zato.common.util.truncate.measure import get_size

# ################################################################################################################################
# ################################################################################################################################

def _finalize(out:'SafeguardResult', value:'any_', work:'any_', reject_kind:'str') -> 'SafeguardResult':
    """ Fills in the final fields of a result - the worked-on value, its size and whether anything changed,
    plus the rejection fields when a stage refused the document.
    """
    out.value = work
    out.size_after = get_size(work)
    out.was_modified = work != value

    if reject_kind:
        out.was_rejected = True
        out.reject_kind = reject_kind

    return out

# ################################################################################################################################
# ################################################################################################################################

def apply_safeguards(value:'any_', config:'SafeguardConfig') -> 'SafeguardResult':
    """ Applies the enabled safeguards to a JSON-serializable value - null stripping, unicode normalization,
    base64 stripping, markup sanitization, URL policy, PII removal and whitespace collapsing, in that order -
    and returns the outcome with a full account of what happened. The input is never mutated and this function
    never raises - a rejection is expressed on the result, the caller decides what to do with it.
    """

    # Our response to produce
    out = SafeguardResult()
    out.value = value
    out.pii_removed = {}
    out.signals = {}

    size_before = get_size(value)
    out.size_before = size_before
    out.size_after = size_before

    # Everything below works on a copy - the caller's object is never mutated.
    work = deepcopy(value)

    # Null keys go first - they are structural and need no per-string work at all.
    if config.strip_nulls:
        work = strip_nulls(work, out)

    # Unicode normalization runs before every scanning stage,
    # so smuggled characters cannot split a pattern those stages need to match.
    if config.normalize_unicode:
        work = normalize_unicode(work, out)

        # Smuggled characters are a potential sign of an attack - reject mode refuses the whole document.
        if out.unicode_chars_removed:
            if config.unicode_mode == Mode_Reject:
                out = _finalize(out, value, work, Kind_Unicode)
                return out

    # Base64 blobs disappear next, before any heavier per-character scanning happens on them.
    if config.strip_base64:
        work = strip_base64(work, out)

    # Markup sanitization - active markup is a potential sign of an attack too.
    if config.sanitize_markup:
        work = sanitize_markup(work, out)

        if out.markup_items_removed:
            if config.markup_mode == Mode_Reject:
                out = _finalize(out, value, work, Kind_Markup)
                return out

    # URL policy - URLs outside the allow list are removed, neutralized or refuse the document.
    if config.url_policy_enabled:
        work = apply_url_policy(work, out, config)

        if out.urls_flagged:
            if config.url_mode == Url_Mode_Reject:
                out = _finalize(out, value, work, Kind_Url)
                return out

    # Whitespace collapses after the removal stages, whose cuts can leave runs behind,
    # and before PII scanning, so identifiers spread across wide gaps still match.
    if config.collapse_whitespace:
        work = collapse_whitespace(work, out)

    # PII removal runs last, on the already normalized, sanitized and collapsed strings.
    if config.pii_enabled:
        work = remove_pii(work, out, config)

    out = _finalize(out, value, work, '')

    return out

# ################################################################################################################################
# ################################################################################################################################
