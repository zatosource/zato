# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import re

# lxml
from lxml import etree

# Zato
from zato.common.file_transfer.const import AttributeType, ExtractionQueryType
from zato.common.file_transfer.model import DocumentType, ExtractionResult, ExtractionRule

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class ExtractionEngine:

    def extract(self, content:'bytes', doc_type:'DocumentType') -> 'ExtractionResult':

        result = ExtractionResult()

        try:
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                text = content.decode('latin-1')
        except Exception:
            text = ''

        for rule in doc_type.extraction_rules:
            value = self._extract_value(content, text, rule)

            if value is None:
                if rule.required:
                    result.errors.append(f'Required attribute {rule.attribute} could not be extracted')
                continue

            attr_type = rule.attr_type
            if isinstance(attr_type, str):
                attr_type = AttributeType(attr_type)

            if attr_type == AttributeType.System:
                if hasattr(result, rule.attribute):
                    setattr(result, rule.attribute, value)
            else:
                result.custom_attrs[rule.attribute] = value

        return result

    def _extract_value(self, content:'bytes', text:'str', rule:'ExtractionRule') -> 'any_':

        query_type = rule.query_type
        if isinstance(query_type, str):
            query_type = ExtractionQueryType(query_type)

        if query_type == ExtractionQueryType.Xpath:
            return self._extract_xpath(rule.query, content)

        elif query_type == ExtractionQueryType.Jsonpath:
            return self._extract_jsonpath(rule.query, text)

        elif query_type == ExtractionQueryType.Regex:
            return self._extract_regex(rule.query, text, rule.line)

        elif query_type == ExtractionQueryType.Fixed:
            return rule.value

        return None

# ################################################################################################################################

    def _extract_xpath(self, query:'str', content:'bytes') -> 'str | None':
        try:
            root = etree.fromstring(content)

            nsmap = {}
            for prefix, uri in root.nsmap.items():
                if prefix:
                    nsmap[prefix] = uri
                else:
                    nsmap['default'] = uri

            if nsmap and not any(prefix in query for prefix in nsmap.keys()):
                if 'default' in nsmap:
                    local_name = etree.QName(root).localname
                    if f'/{local_name}' in query or query.startswith(f'{local_name}/') or query.startswith(f'/{local_name}'):
                        pass

            result = root.xpath(query, namespaces=nsmap if nsmap else None)

            if isinstance(result, list):
                if not result:
                    return None
                first = result[0]
                if hasattr(first, 'text'):
                    return first.text
                return str(first)
            return str(result) if result else None
        except Exception:
            return None

# ################################################################################################################################

    def _extract_jsonpath(self, query:'str', text:'str') -> 'any_':
        try:
            data = json.loads(text)

            if query.startswith('$.'):
                query = query[2:]

            parts = query.split('.')
            current = data

            for part in parts:
                if '[' in part and ']' in part:
                    match = re.match(r'(\w+)\[(\d+)\]', part)
                    if match:
                        key = match.group(1)
                        idx = int(match.group(2))
                        if isinstance(current, dict) and key in current:
                            current = current[key]
                            if isinstance(current, list) and idx < len(current):
                                current = current[idx]
                            else:
                                return None
                        else:
                            return None
                    else:
                        return None
                elif isinstance(current, dict) and part in current:
                    current = current[part]
                elif isinstance(current, list):
                    try:
                        idx = int(part)
                        current = current[idx]
                    except (ValueError, IndexError):
                        return None
                else:
                    return None

            return current
        except Exception:
            return None

# ################################################################################################################################

    def _extract_regex(self, query:'str', text:'str', line:'int') -> 'str | None':
        try:
            if line and line > 0:
                lines = text.split('\n')
                if line <= len(lines):
                    text_to_search = lines[line - 1]
                else:
                    return None
            else:
                text_to_search = text

            match = re.search(query, text_to_search)
            if match:
                if match.groups():
                    return match.group(1)
                return match.group(0)
            return None
        except Exception:
            return None

# ################################################################################################################################
# ################################################################################################################################
