# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import re
import time
from logging import getLogger
from typing import Any, Dict, List, Optional

# Pydantic
from pydantic import BaseModel, Field

# Zato
from zato.admin.web.views.ai.common import get_redis_client

if 0:
    from zato.common.typing_ import anydict

logger = getLogger(__name__)

Redis_Key_Prefix = 'zato.ai-chat.tool-execution.'
Redis_TTL_Seconds = 60 * 60 * 24 * 14 # 2 weeks

# ################################################################################################################################
# ################################################################################################################################

class ToolRecord(BaseModel):
    """ Record of a single tool execution.
    """
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    success: bool = False
    error: Optional[str] = None

# ################################################################################################################################

class ExecutionLog(BaseModel):
    """ Collection of tool execution records with ground-truth log generation.
    """
    records: List[ToolRecord] = Field(default_factory=list)

    def add(
        self,
        tool_name:'str',
        arguments:'dict',
        result:'Any'=None,
        success:'bool'=False,
        error:'str'=None
    ) -> 'None':
        """ Adds a tool execution record.
        """
        record = ToolRecord(
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            success=success,
            error=error
        )
        self.records.append(record)

    def clear(self) -> 'None':
        """ Clears all records.
        """
        self.records = []

    def build_ground_truth_message(self) -> 'str':
        """ Builds a ground-truth execution log message for injection into conversation.
        """
        if not self.records:
            return ''

        lines = [f'EXECUTION LOG - {len(self.records)} operation(s) executed:']

        for idx, record in enumerate(self.records, 1):
            status = 'SUCCESS' if record.success else f'FAILED ({record.error})'
            args_str = json.dumps(record.arguments, default=str)
            lines.append(f'  {idx}. {record.tool_name}({args_str}) -> {status}')
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

        out = '\n'.join(lines)
        return out

    def get_object_changes(self) -> 'List[Dict[str, Any]]':
        """ Extracts object changes for UI refresh from successful operations.
        """
        out = []

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

                out.append({
                    'action': action,
                    'object_id': object_id,
                    'object_name': object_name
                })

        return out

    def verify_response(self, response_text:'str') -> 'List[str]':
        """ Verifies that the LLM response matches the execution log.
        Returns a list of issues found, empty if response is valid.
        """
        out = []

        create_count = sum(1 for r in self.records if r.success and r.tool_name.startswith('create_'))
        update_count = sum(1 for r in self.records if r.success and r.tool_name.startswith('update_'))
        delete_count = sum(1 for r in self.records if r.success and r.tool_name.startswith('delete_'))

        for match in re.finditer(r'created?\s+(\d+)\s+\w+', response_text, re.IGNORECASE):
            claimed = int(match.group(1))
            if claimed != create_count:
                out.append(f'Claims {claimed} created, actually {create_count}')

        for match in re.finditer(r'updated?\s+(\d+)\s+\w+', response_text, re.IGNORECASE):
            claimed = int(match.group(1))
            if claimed != update_count:
                out.append(f'Claims {claimed} updated, actually {update_count}')

        for match in re.finditer(r'deleted?\s+(\d+)\s+\w+', response_text, re.IGNORECASE):
            claimed = int(match.group(1))
            if claimed != delete_count:
                out.append(f'Claims {claimed} deleted, actually {delete_count}')

        return out

    def build_deterministic_response(self) -> 'str':
        """ Builds a guaranteed-accurate response from the execution log.
        Used as fallback when verification detects fabrication.
        """
        created = [r for r in self.records if r.success and r.tool_name.startswith('create_')]
        updated = [r for r in self.records if r.success and r.tool_name.startswith('update_')]
        deleted = [r for r in self.records if r.success and r.tool_name.startswith('delete_')]
        failed = [r for r in self.records if not r.success]

        parts = []

        if created:
            parts.append(f'Created {len(created)} object(s):')
            for r in created:
                name = r.arguments.get('name', 'unknown')
                parts.append(f'- {name}')

        if updated:
            parts.append(f'Updated {len(updated)} object(s):')
            for r in updated:
                name = r.arguments.get('name', 'unknown')
                parts.append(f'- {name}')

        if deleted:
            parts.append(f'Deleted {len(deleted)} object(s):')
            for r in deleted:
                name = r.arguments.get('name', 'unknown')
                parts.append(f'- {name}')

        if failed:
            parts.append(f'{len(failed)} operation(s) failed.')

        out = '\n'.join(parts) if parts else 'No operations were performed.'
        return out

    def persist(self, session_id:'str') -> 'None':
        """ Persists all records to Redis for cross-turn recall.
        """
        if not self.records:
            return

        try:
            client = get_redis_client()
            key = Redis_Key_Prefix + session_id
            timestamp = time.time()

            for record in self.records:
                entry = {
                    'tool_name': record.tool_name,
                    'arguments': record.arguments,
                    'result': record.result,
                    'success': record.success,
                    'error': record.error,
                    'timestamp': timestamp
                }
                client.zadd(key, {json.dumps(entry, default=str): timestamp})

            client.expire(key, Redis_TTL_Seconds)
            logger.info('Persisted %d tool execution records for session %s', len(self.records), session_id)

        except Exception as e:
            logger.warning('Failed to persist tool executions: %s', e)

# ################################################################################################################################

def get_recent_executions(session_id:'str', limit:'int'=20) -> 'list':
    """ Retrieves recent tool executions for a session from Redis.
    """
    try:
        client = get_redis_client()
        key = Redis_Key_Prefix + session_id
        entries = client.zrevrange(key, 0, limit - 1)

        out = []
        for entry in entries:
            data = json.loads(entry)
            out.append(data)

        return out

    except Exception as e:
        logger.warning('Failed to retrieve tool executions: %s', e)
        return []

# ################################################################################################################################
# ################################################################################################################################
