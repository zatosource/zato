# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import List

# Zato
from zato.common.file_transfer.const import CriteriaMatch, ErrorCriteria, ExtendedCriteriaOperator
from zato.common.file_transfer.model import CriteriaSpec, ExtendedCriteria, ProcessingRule, Transaction

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class RuleEvaluator:

    def evaluate(
        self,
        txn:'Transaction',
        rules:'List[ProcessingRule]',
    ) -> 'ProcessingRule | None':

        sorted_rules = sorted(rules, key=lambda r: r.ordinal)

        for rule in sorted_rules:
            if not rule.is_enabled:
                continue
            if self._matches_all_criteria(txn, rule):
                return rule

        return None

    def _matches_all_criteria(self, txn:'Transaction', rule:'ProcessingRule') -> 'bool':

        if not self._match_criteria(rule.criteria_sender, txn.sender):
            return False

        if not self._match_criteria(rule.criteria_receiver, txn.receiver):
            return False

        if not self._match_doc_type_criteria(rule.criteria_doc_type, txn.doc_type_id):
            return False

        if not self._match_criteria(rule.criteria_user_status, txn.user_status):
            return False

        if not self._match_errors(rule.criteria_errors, txn.has_errors):
            return False

        if not self._match_extended_criteria(rule.criteria_extended, txn.custom_attrs):
            return False

        return True

# ################################################################################################################################

    def _match_criteria(self, criteria:'CriteriaSpec', value:'str') -> 'bool':

        match = criteria.match
        if isinstance(match, str):
            match = CriteriaMatch(match)

        if match == CriteriaMatch.Any:
            return True

        if match == CriteriaMatch.Unknown:
            return not value or value == ''

        if match == CriteriaMatch.Specific:
            if not criteria.values:
                return True
            return value in criteria.values

        return True

# ################################################################################################################################

    def _match_doc_type_criteria(self, criteria:'CriteriaSpec', doc_type_id:'str') -> 'bool':

        match = criteria.match
        if isinstance(match, str):
            match = CriteriaMatch(match)

        if match == CriteriaMatch.Any:
            return True

        if match == CriteriaMatch.Unknown:
            return not doc_type_id or doc_type_id == ''

        if match == CriteriaMatch.Specific:
            if not criteria.values:
                return True
            return doc_type_id in criteria.values

        return True

# ################################################################################################################################

    def _match_errors(self, criteria:'ErrorCriteria', has_errors:'bool') -> 'bool':

        if isinstance(criteria, str):
            criteria = ErrorCriteria(criteria)

        if criteria == ErrorCriteria.Any:
            return True

        if criteria == ErrorCriteria.No_Errors:
            return not has_errors

        if criteria == ErrorCriteria.Has_Errors:
            return has_errors

        return True

# ################################################################################################################################

    def _match_extended_criteria(
        self,
        criteria_list:'List[ExtendedCriteria]',
        custom_attrs:'dict',
    ) -> 'bool':

        for criteria in criteria_list:
            if not self._match_single_extended(criteria, custom_attrs):
                return False
        return True

    def _match_single_extended(self, criteria:'ExtendedCriteria', custom_attrs:'dict') -> 'bool':

        attr_value = custom_attrs.get(criteria.attribute)
        operator = criteria.operator

        if isinstance(operator, str):
            try:
                operator = ExtendedCriteriaOperator(operator)
            except ValueError:
                operator = criteria.operator

        if operator == ExtendedCriteriaOperator.Is_Null or operator == 'IS_NULL':
            return attr_value is None or attr_value == ''

        if operator == ExtendedCriteriaOperator.Is_Not_Null or operator == 'IS_NOT_NULL':
            return attr_value is not None and attr_value != ''

        if attr_value is None:
            return False

        attr_str = str(attr_value)
        crit_value = criteria.value

        if operator == ExtendedCriteriaOperator.Equals or operator == 'EQUALS':
            return attr_str == crit_value

        if operator == ExtendedCriteriaOperator.Not_Equals or operator == 'NOT_EQUALS':
            return attr_str != crit_value

        if operator == ExtendedCriteriaOperator.Contains or operator == 'CONTAINS':
            return crit_value in attr_str

        if operator == ExtendedCriteriaOperator.Begins_With or operator == 'BEGINS_WITH':
            return attr_str.startswith(crit_value)

        if operator == ExtendedCriteriaOperator.Ends_With or operator == 'ENDS_WITH':
            return attr_str.endswith(crit_value)

        try:
            attr_num = float(attr_value)
            crit_num = float(crit_value)

            if operator == ExtendedCriteriaOperator.Greater_Than or operator == 'GREATER_THAN':
                return attr_num > crit_num

            if operator == ExtendedCriteriaOperator.Less_Than or operator == 'LESS_THAN':
                return attr_num < crit_num

            if operator == ExtendedCriteriaOperator.Greater_Or_Equal or operator == 'GREATER_OR_EQUAL':
                return attr_num >= crit_num

            if operator == ExtendedCriteriaOperator.Less_Or_Equal or operator == 'LESS_OR_EQUAL':
                return attr_num <= crit_num

        except (ValueError, TypeError):
            pass

        return True

# ################################################################################################################################
# ################################################################################################################################
