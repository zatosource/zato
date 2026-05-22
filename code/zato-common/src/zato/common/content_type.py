# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from __future__ import annotations

import io
import json

# lxml
from lxml import etree

# python-magic
import magic

# ################################################################################################################################
# ################################################################################################################################

def get_content_type(data:'str | bytes') -> 'str':
    """ Detects the MIME content type of the given data.
    """

    # Encode string data to bytes for magic ..
    if isinstance(data, str):
        data = data.encode('utf-8')

    # .. and return the detected MIME type.
    out = magic.from_buffer(data, mime=True)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _format_json(data:'str') -> 'str':
    """ Pretty-prints JSON data with 2-space indentation.
    """

    # Parse the raw JSON string ..
    parsed = json.loads(data)

    # .. and re-serialize it with indentation.
    out = json.dumps(parsed, indent=2)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _format_xml(data:'str') -> 'str':
    """ Pretty-prints XML data using lxml.
    """

    # Parse the XML from raw bytes ..
    data_bytes = data.encode('utf-8')
    tree = etree.fromstring(data_bytes)

    # .. indent the tree ..
    etree.indent(tree)

    # .. and serialize it back to a string.
    out = etree.tostring(tree, encoding='unicode', pretty_print=True)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _format_html(data:'str') -> 'str':
    """ Pretty-prints HTML data using lxml.
    """

    # Parse the HTML from a string reader ..
    parser = etree.HTMLParser()
    string_io = io.StringIO(data)
    doc = etree.parse(string_io, parser)

    # .. indent the tree ..
    etree.indent(doc)

    # .. and serialize it back to a string.
    out = etree.tostring(doc, encoding='unicode', method='html', pretty_print=True)
    return out

# ################################################################################################################################
# ################################################################################################################################

_formatters = {
    'application/json':      _format_json,
    'text/json':             _format_json,
    'application/geo+json':  _format_json,
    'application/ld+json':   _format_json,
    'application/vnd.api+json': _format_json,
    'application/json5':     _format_json,
    'text/xml':              _format_xml,
    'application/xml':       _format_xml,
    'application/soap+xml':  _format_xml,
    'application/rss+xml':   _format_xml,
    'application/atom+xml':  _format_xml,
    'image/svg+xml':         _format_xml,
    'text/html':             _format_html,
    'application/xhtml+xml': _format_html,
}

# ################################################################################################################################
# ################################################################################################################################

def format_content(data:'str', content_type:'str') -> 'str':
    """ Formats the given data based on its content type using the appropriate formatter.
    """

    if formatter := _formatters.get(content_type):
        out = formatter(data)
    else:
        out = data

    return out

# ################################################################################################################################
# ################################################################################################################################
