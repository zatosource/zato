# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The human-readable lines the MCP detail pane says about what response shaping did to one
event - PII and secrets replacements per detector, compaction counts, content safety findings,
token cuts and the client's own filter - each count in the grammatical number it calls for.
"""

# stdlib
import json

# Zato
from zato.common.util.logging_ import count_text
from zato.common.util.safeguards.names import Detector_Nouns, Secret_Detector_Nouns

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# What each family of trace lines is labelled with in the pane
_label_pii            = 'PII removed'
_label_secrets        = 'Secrets removed'
_label_compaction     = 'Compaction'
_label_content_safety = 'Content safety'
_label_size_cap       = 'Size cap'
_label_agent_filter   = 'Agent filter'
_label_rejected       = 'Rejected'

# How each rejection kind reads on its pane line - every kind a safeguard
# or the size cap can report is here.
_reject_kind_labels = {
    'unicode': 'Unicode content',
    'markup':  'Markup content',
    'url':     'URL policy',
    'size':    'Size',
}

# ################################################################################################################################
# ################################################################################################################################

def get_trace_lines(data:'stranydict') -> 'anylist':
    """ Returns the pane lines for one MCP event's data document - one line per finding,
    in the order the stages ran, and no line at all for a stage that found nothing.
    """

    # Our response to produce
    out:'anylist' = []

    # One line per detector, each count with its own noun ..
    if pii_removed := data.get('pii_removed'):
        for detector_name in sorted(pii_removed):

            count = pii_removed[detector_name]
            singular, plural = Detector_Nouns[detector_name]
            counted = count_text(count, singular, plural)

            out.append({'label': _label_pii, 'text': f'replaced {counted}'})

    # .. one line per secrets detector too ..
    if secrets_removed := data.get('secrets_removed'):
        for detector_name in sorted(secrets_removed):

            count = secrets_removed[detector_name]
            singular, plural = Secret_Detector_Nouns[detector_name]
            counted = count_text(count, singular, plural)

            out.append({'label': _label_secrets, 'text': f'replaced {counted}'})

    # .. what compaction stripped out ..
    if nulls_removed := data.get('nulls_removed'):
        counted = count_text(nulls_removed, 'null field', 'null fields')
        out.append({'label': _label_compaction, 'text': f'removed {counted}'})

    if whitespace_chars_removed := data.get('whitespace_chars_removed'):
        counted = count_text(whitespace_chars_removed, 'whitespace character', 'whitespace characters')
        out.append({'label': _label_compaction, 'text': f'collapsed {counted}'})

    if base64_blobs_removed := data.get('base64_blobs_removed'):
        counted = count_text(base64_blobs_removed, 'base64 blob', 'base64 blobs')
        out.append({'label': _label_compaction, 'text': f'removed {counted}'})

    # .. what content safety found ..
    if unicode_chars_removed := data.get('unicode_chars_removed'):
        counted = count_text(unicode_chars_removed, 'Unicode character', 'Unicode characters')
        out.append({'label': _label_content_safety, 'text': f'removed {counted}'})

    if markup_items_removed := data.get('markup_items_removed'):
        counted = count_text(markup_items_removed, 'markup item', 'markup items')
        out.append({'label': _label_content_safety, 'text': f'removed {counted}'})

    if urls_flagged := data.get('urls_flagged'):
        counted = count_text(urls_flagged, 'URL', 'URLs')
        out.append({'label': _label_content_safety, 'text': f'flagged {counted}'})

    # .. what the size cap cut - a truncation names both sides of the cut,
    # a block only what was measured ..
    if data.get('was_truncated'):

        before = count_text(data['tokens_before'], 'token', 'tokens')
        after = count_text(data['tokens_after'], 'token', 'tokens')

        out.append({'label': _label_size_cap, 'text': f'truncated from {before} to {after}'})

    # .. the filter the agent itself asked for ..
    if agent_filter := data.get('agent_filter'):
        out.append({'label': _label_agent_filter, 'text': agent_filter})

    # .. and a rejection names its kind, with the measured size when size was the reason -
    # a size rejection always records what it measured before it blocked.
    if reject_kind := data.get('reject_kind'):

        kind_label = _reject_kind_labels[reject_kind]

        if reject_kind == 'size':
            counted = count_text(data['tokens_before'], 'token', 'tokens')
            text = f'{kind_label} - {counted}'
        else:
            text = kind_label

        out.append({'label': _label_rejected, 'text': text})

    return out

# ################################################################################################################################
# ################################################################################################################################

def attach_trace_lines(row:'stranydict', data:'str') -> 'None':
    """ Parses one MCP row's full data document and attaches the trace lines to the row -
    a row whose document holds no trace keys gets no lines and the pane says nothing extra.
    """

    # The data column always holds a JSON document for MCP events.
    document = json.loads(data)

    if trace_lines := get_trace_lines(document):
        row['trace_lines'] = trace_lines

# ################################################################################################################################
# ################################################################################################################################
