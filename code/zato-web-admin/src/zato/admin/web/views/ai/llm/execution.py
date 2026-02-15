# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from typing import Any, Dict, List, Optional

# Pydantic
from pydantic import BaseModel, Field

# ################################################################################################################################
# ################################################################################################################################

class ToolRecord(BaseModel):
    """ Record of a single tool execution. """
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    success: bool = False
    error: Optional[str] = None

# ################################################################################################################################

class ExecutionLog(BaseModel):
    """ Collection of tool execution records with ground-truth log generation. """
    records: List[ToolRecord] = Field(default_factory=list)

    def add(self, tool_name: str, arguments: dict, result: Any = None, success: bool = False, error: str = None) -> None:
        """ Adds a tool execution record. """
        record = ToolRecord(
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            success=success,
            error=error
        )
        self.records.append(record)

    def clear(self) -> None:
        """ Clears all records. """
        self.records = []

    def build_ground_truth_message(self) -> str:
        """ Builds a ground-truth execution log message for injection into conversation. """
        if not self.records:
            return ''

        lines = [f'EXECUTION LOG - {len(self.records)} operation(s) executed:']

        for i, record in enumerate(self.records, 1):
            status = 'SUCCESS' if record.success else f'FAILED ({record.error})'
            args_str = json.dumps(record.arguments, default=str)
            lines.append(f'  {i}. {record.tool_name}({args_str}) -> {status}')
            if record.success and record.result:
                result_str = json.dumps(record.result, default=str)
                lines.append(f'     Result: {result_str}')

        succeeded = sum(1 for r in self.records if r.success)
        failed = len(self.records) - succeeded

        lines.append('')
        lines.append(f'Total: {succeeded} succeeded, {failed} failed.')
        lines.append('')
        lines.append('Base your response ONLY on the operations listed above.')
        lines.append('Do NOT claim any operation occurred that is not in this log.')

        return '\n'.join(lines)

    def get_object_changes(self) -> List[Dict[str, Any]]:
        """ Extracts object changes for UI refresh from successful operations. """
        changes = []

        for record in self.records:
            if not record.success:
                continue

            action = None
            if record.tool_name.startswith('create_'):
                action = 'create'
            elif record.tool_name.startswith('update_'):
                action = 'update'
            elif record.tool_name.startswith('delete_'):
                action = 'delete'

            if action:
                object_id = ''
                object_name = ''

                if isinstance(record.result, dict):
                    object_id = record.result.get('id', '')
                if isinstance(record.arguments, dict):
                    object_name = record.arguments.get('name', '')

                changes.append({
                    'action': action,
                    'object_id': object_id,
                    'object_name': object_name
                })

        return changes

# ################################################################################################################################
# ################################################################################################################################
