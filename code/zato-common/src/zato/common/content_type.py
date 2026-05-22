
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
    if isinstance(data, str):
        data = data.encode('utf-8')
    return magic.from_buffer(data, mime=True)

# ################################################################################################################################
# ################################################################################################################################

def _format_json(data:'str') -> 'str':
    parsed = json.loads(data)
    return json.dumps(parsed, indent=2)

# ################################################################################################################################

def _format_xml(data:'str') -> 'str':
    tree = etree.fromstring(data.encode('utf-8'))
    etree.indent(tree)
    return etree.tostring(tree, encoding='unicode', pretty_print=True)

# ################################################################################################################################

def _format_html(data:'str') -> 'str':
    parser = etree.HTMLParser()
    doc = etree.parse(io.StringIO(data), parser)
    etree.indent(doc)
    return etree.tostring(doc, encoding='unicode', method='html', pretty_print=True)

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
    if formatter := _formatters.get(content_type):
        return formatter(data)
    else:
        return data

# ################################################################################################################################
# ################################################################################################################################
