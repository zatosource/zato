# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
from dataclasses import dataclass
from json import JSONDecodeError, loads
from logging import getLogger
from xml.etree.ElementTree import fromstring, ParseError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anynone, stranydict, strnone

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anynone = anynone
    stranydict = stranydict
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ExtractionType:
    """ How an attribute value is extracted out of a message - a path into JSON, an XPath into XML,
    a header lookup or a regular expression over the raw data.
    """
    JSON_Path = 'json-path'
    XPath     = 'xpath'
    Header    = 'header'
    Regex     = 'regex'

# ################################################################################################################################

@dataclass(init=False)
class ExtractionRule:
    """ One declarative rule extracting one searchable attribute out of a message.
    """
    attr_name:  'str' = ''
    rule_type:  'str' = ''
    expression: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

# The list type extraction runs over
extraction_rule_list = list[ExtractionRule]

# ################################################################################################################################
# ################################################################################################################################

# Matches one JSON path token with optional list indexes, e.g. items[0] or items[0][2]
_json_token_pattern = re.compile(r'^([^\[\]]+)((?:\[\d+\])*)$')

# Matches each individual list index inside a token
_json_index_pattern = re.compile(r'\[(\d+)\]')

# ################################################################################################################################

def _walk_json_path(parsed:'any_', expression:'str') -> 'anynone':
    """ Walks a dotted path, with optional list indexes, into a parsed JSON document,
    e.g. $.request.customer_id or items[0].name. Returns None when any step does not match.
    """

    # The leading dollar and dot are optional ..
    if expression.startswith('$.'):
        expression = expression[2:]
    elif expression.startswith('$'):
        expression = expression[1:]

    current = parsed

    # .. each dotted token is a dictionary key, possibly followed by list indexes ..
    for token in expression.split('.'):

        match = _json_token_pattern.match(token)
        if not match:
            return None

        key = match.group(1)
        indexes = match.group(2)

        # .. the key must lead into a dictionary ..
        if not isinstance(current, dict):
            return None

        current = current.get(key)
        if current is None:
            return None

        # .. and each index must lead into a list that is long enough.
        for index_match in _json_index_pattern.finditer(indexes):
            index = int(index_match.group(1))

            if not isinstance(current, list):
                return None

            if index >= len(current):
                return None

            current = current[index]

    out = current
    return out

# ################################################################################################################################
# ################################################################################################################################

class _ExtractionContext:
    """ Carries the message through extraction, parsing it at most once per format.
    """

    def __init__(self, data:'str', headers:'stranydict') -> 'None':

        self.data = data
        self.headers = headers

        # Parsed documents are built on first use and reused by every rule of the same type
        self._parsed_json:'anynone' = None
        self._parsed_xml:'anynone' = None

        self._json_parse_attempted = False
        self._xml_parse_attempted = False

# ################################################################################################################################

    def get_parsed_json(self) -> 'anynone':
        """ Returns the message parsed as JSON, or None if it is not valid JSON.
        """
        if not self._json_parse_attempted:
            self._json_parse_attempted = True
            try:
                self._parsed_json = loads(self.data)
            except JSONDecodeError:
                self._parsed_json = None

        out = self._parsed_json
        return out

# ################################################################################################################################

    def get_parsed_xml(self) -> 'anynone':
        """ Returns the message parsed as XML, or None if it is not valid XML.
        """
        if not self._xml_parse_attempted:
            self._xml_parse_attempted = True
            try:
                self._parsed_xml = fromstring(self.data)
            except ParseError:
                self._parsed_xml = None

        out = self._parsed_xml
        return out

# ################################################################################################################################
# ################################################################################################################################

def _extract_json_path(rule:'ExtractionRule', context:'_ExtractionContext') -> 'anynone':
    """ Extracts a value by walking a JSON path into the message.
    """
    parsed = context.get_parsed_json()

    if parsed is None:
        return None

    out = _walk_json_path(parsed, rule.expression)
    return out

# ################################################################################################################################

def _extract_xpath(rule:'ExtractionRule', context:'_ExtractionContext') -> 'anynone':
    """ Extracts the text of the first element an XPath expression finds in the message.
    """
    parsed = context.get_parsed_xml()

    if parsed is None:
        return None

    element = parsed.find(rule.expression)

    if element is None:
        return None

    out = element.text
    return out

# ################################################################################################################################

def _extract_header(rule:'ExtractionRule', context:'_ExtractionContext') -> 'anynone':
    """ Extracts a value out of the message headers.
    """
    out = context.headers.get(rule.expression)
    return out

# ################################################################################################################################

def _extract_regex(rule:'ExtractionRule', context:'_ExtractionContext') -> 'anynone':
    """ Extracts a value by matching a regular expression against the raw message -
    the first capturing group if there is one, the whole match otherwise.
    """
    try:
        match = re.search(rule.expression, context.data)
    except re.error:
        logger.warning('Invalid extraction regex `%s` for attribute `%s`', rule.expression, rule.attr_name)
        return None

    if not match:
        return None

    if match.groups():
        out = match.group(1)
    else:
        out = match.group(0)

    return out

# ################################################################################################################################
# ################################################################################################################################

# Each rule type maps to its extraction function
_extractors = {
    ExtractionType.JSON_Path: _extract_json_path,
    ExtractionType.XPath:     _extract_xpath,
    ExtractionType.Header:    _extract_header,
    ExtractionType.Regex:     _extract_regex,
}

# ################################################################################################################################

def extract_attrs(
    rules:'extraction_rule_list',
    *,
    data:'str' = '',
    headers:'stranydict | None' = None,
    ) -> 'stranydict':
    """ Runs declarative extraction rules over one message, returning the attributes they found.
    Extraction is best-effort - a rule that does not match simply contributes nothing.
    """

    # Our response to produce
    out:'stranydict' = {}

    if headers is None:
        headers = {}

    context = _ExtractionContext(data, headers)

    for rule in rules:

        # Unknown rule types are configuration mistakes worth pointing out ..
        extractor = _extractors.get(rule.rule_type)

        if not extractor:
            logger.warning('Unknown extraction rule type `%s` for attribute `%s`', rule.rule_type, rule.attr_name)
            continue

        # .. and a rule only contributes when it actually found something.
        value = extractor(rule, context)

        if value is not None:
            out[rule.attr_name] = value

    return out

# ################################################################################################################################
# ################################################################################################################################
