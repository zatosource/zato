# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import fnmatch
import json
import re
from typing import List

# lxml
from lxml import etree

# Zato
from zato.common.file_transfer.const import RecognitionRuleType
from zato.common.file_transfer.model import DocumentType, RecognitionRule

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class RecognitionEngine:

    def recognize(
        self,
        filename:'str',
        content:'bytes',
        doc_types:'List[DocumentType]',
    ) -> 'DocumentType | None':

        for doc_type in doc_types:
            if not doc_type.is_enabled:
                continue
            if self._matches_all_rules(filename, content, doc_type.recognition_rules):
                return doc_type
        return None

    def _matches_all_rules(
        self,
        filename:'str',
        content:'bytes',
        rules:'List[RecognitionRule]',
    ) -> 'bool':

        if not rules:
            return False

        sorted_rules = sorted(rules, key=lambda r: r.priority)

        for rule in sorted_rules:
            if not self._matches_rule(filename, content, rule):
                return False
        return True

    def _matches_rule(
        self,
        filename:'str',
        content:'bytes',
        rule:'RecognitionRule',
    ) -> 'bool':

        rule_type = rule.type
        if isinstance(rule_type, str):
            rule_type = RecognitionRuleType(rule_type)

        if rule_type == RecognitionRuleType.Filename_Glob:
            return self._match_filename_glob(rule.pattern, filename)

        elif rule_type == RecognitionRuleType.Content_Regex:
            return self._match_content_regex(rule.pattern, content, rule.bytes_limit)

        elif rule_type == RecognitionRuleType.Xml_Root_Tag:
            return self._match_xml_root_tag(rule.tag, content)

        elif rule_type == RecognitionRuleType.Json_Path:
            return self._match_json_path(rule.path, content)

        elif rule_type == RecognitionRuleType.Pgp_Header:
            return self._match_pgp_header(content)

        elif rule_type == RecognitionRuleType.Edi_Segment:
            return self._match_edi_segment(rule.segment, rule.transaction_set, content)

        return False

# ################################################################################################################################

    def _match_filename_glob(self, pattern:'str', filename:'str') -> 'bool':
        return fnmatch.fnmatch(filename, pattern)

# ################################################################################################################################

    def _match_content_regex(self, pattern:'str', content:'bytes', bytes_limit:'int') -> 'bool':
        try:
            if bytes_limit and bytes_limit > 0:
                content_to_check = content[:bytes_limit]
            else:
                content_to_check = content

            try:
                text = content_to_check.decode('utf-8')
            except UnicodeDecodeError:
                text = content_to_check.decode('latin-1')

            return bool(re.search(pattern, text))
        except Exception:
            return False

# ################################################################################################################################

    def _match_xml_root_tag(self, tag:'str', content:'bytes') -> 'bool':
        try:
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                text = content.decode('latin-1')

            root = etree.fromstring(content)
            local_name = etree.QName(root).localname
            return local_name == tag
        except Exception:
            return False

# ################################################################################################################################

    def _match_json_path(self, path:'str', content:'bytes') -> 'bool':
        try:
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                text = content.decode('latin-1')

            data = json.loads(text)

            if path.startswith('$.'):
                path = path[2:]

            parts = path.split('.')
            current = data

            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                elif isinstance(current, list):
                    try:
                        idx = int(part)
                        current = current[idx]
                    except (ValueError, IndexError):
                        return False
                else:
                    return False

            return True
        except Exception:
            return False

# ################################################################################################################################

    def _match_pgp_header(self, content:'bytes') -> 'bool':
        pgp_markers = [
            b'-----BEGIN PGP MESSAGE-----',
            b'-----BEGIN PGP SIGNED MESSAGE-----',
            b'-----BEGIN PGP PUBLIC KEY BLOCK-----',
            b'-----BEGIN PGP PRIVATE KEY BLOCK-----',
        ]

        pgp_binary_markers = [
            b'\x85',
            b'\x84',
            b'\xa6',
            b'\xc6',
        ]

        for marker in pgp_markers:
            if marker in content[:1000]:
                return True

        if content and content[0:1] in pgp_binary_markers:
            return True

        return False

# ################################################################################################################################

    def _match_edi_segment(self, segment:'str', transaction_set:'str', content:'bytes') -> 'bool':
        try:
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                text = content.decode('latin-1')

            if segment == 'ISA':
                if not text.startswith('ISA'):
                    return False

            if transaction_set:
                st_pattern = f'ST\\*{transaction_set}\\*'
                if not re.search(st_pattern, text):
                    return False

            return segment in text
        except Exception:
            return False

# ################################################################################################################################
# ################################################################################################################################
