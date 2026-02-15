# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import re
from datetime import datetime
from enum import Enum
from logging import getLogger
from typing import Any, Dict, List, Optional

# Pydantic
from pydantic import BaseModel, Field

# Zato
from zato.admin.web.views.ai.common import get_redis_client

if 0:
    from zato.common.typing_ import anydict

logger = getLogger(__name__)

Redis_Key_Prefix_Stream = 'zato.ai-chat.events.'
Redis_Key_Prefix_State = 'zato.ai-chat.state.'
Redis_TTL_Seconds = 60 * 60 * 24 * 14 # 2 weeks

# ################################################################################################################################
# ################################################################################################################################

class QueryIntent(Enum):
    """ Intent classification for execution history queries.
    """
    Current_State = 'current_state'
    Event_History = 'event_history'
    Ambiguous = 'ambiguous'

State_Signals = [
    r'\b(what|which|show|list|how many)\b.*(exist|current|now|active|have|are there)',
    r'\bcurrent (state|status|count)',
    r'\bsummar(y|ize)\b',
]

History_Signals = [
    r'\b(what|which).*did (you|it|the)\b.*(create|update|delete|do|change|modify)',
    r'\b(show|list).*\b(log|history|events?|operations?|steps?)',
    r'\b(what|when|how).*(happened|occurred|went wrong)',
    r'\bsequence|timeline|order of\b',
]

def detect_intent(question:'str') -> 'QueryIntent':
    """ Detects whether a question asks about current state or event history.
    """
    q = question.lower()
    state_hits = sum(1 for p in State_Signals if re.search(p, q))
    history_hits = sum(1 for p in History_Signals if re.search(p, q))

    if state_hits > history_hits:
        return QueryIntent.Current_State
    if history_hits > state_hits:
        return QueryIntent.Event_History

    return QueryIntent.Ambiguous

# ################################################################################################################################
# ################################################################################################################################

class ToolRecord(BaseModel):
    """ Record of a single tool execution.
    """
    tool_name: str
    model_name: str = ''
    object_id: str = ''
    object_name: str = ''
    action: str = ''
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    success: bool = False
    error: Optional[str] = None

# ################################################################################################################################

class ExecutionLog(BaseModel):
    """ Dual-view execution logger using Redis Streams (events) and Hashes (state).
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
        action = ''
        if tool_name.startswith('create_'):
            action = 'created'
        elif tool_name.startswith('update_'):
            action = 'updated'
        elif tool_name.startswith('delete_'):
            action = 'deleted'

        model_name = tool_name.replace('create_', '').replace('update_', '').replace('delete_', '')
        object_name = arguments.get('name', '')
        object_id = ''
        if isinstance(result, dict):
            object_id = str(result.get('id', ''))

        record = ToolRecord(
            tool_name=tool_name,
            model_name=model_name,
            object_id=object_id,
            object_name=object_name,
            action=action,
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
        lines.append('Do NOT say "Done" or "Done." - the UI already shows completion status.')

        out = '\n'.join(lines)
        return out

    def get_object_changes(self) -> 'List[Dict[str, Any]]':
        """ Extracts object changes for UI refresh from successful operations.
        """
        out = []

        for record in self.records:
            if not record.success:
                continue

            if record.action:
                out.append({
                    'action': record.action.rstrip('d'),
                    'object_id': record.object_id,
                    'object_name': record.object_name
                })

        return out

    def verify_response(self, response_text:'str') -> 'List[str]':
        """ Verifies that the LLM response matches the execution log.
        Returns a list of issues found, empty if response is valid.
        """
        out = []

        create_count = sum(1 for r in self.records if r.success and r.action == 'created')
        update_count = sum(1 for r in self.records if r.success and r.action == 'updated')
        delete_count = sum(1 for r in self.records if r.success and r.action == 'deleted')

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
        created = [r for r in self.records if r.success and r.action == 'created']
        updated = [r for r in self.records if r.success and r.action == 'updated']
        deleted = [r for r in self.records if r.success and r.action == 'deleted']
        failed = [r for r in self.records if not r.success]

        parts = []

        if created:
            parts.append(f'Created {len(created)} object(s):')
            for r in created:
                parts.append(f'- {r.object_name}')

        if updated:
            parts.append(f'Updated {len(updated)} object(s):')
            for r in updated:
                parts.append(f'- {r.object_name}')

        if deleted:
            parts.append(f'Deleted {len(deleted)} object(s):')
            for r in deleted:
                parts.append(f'- {r.object_name}')

        if failed:
            parts.append(f'{len(failed)} operation(s) failed.')

        out = '\n'.join(parts) if parts else 'No operations were performed.'
        return out

    def persist(self, session_id:'str', conversation_turn:'int'=0) -> 'None':
        """ Persists records to Redis using dual-view architecture.
        Writes to both event stream and state snapshot atomically.
        """
        if not self.records:
            return

        try:
            client = get_redis_client()
            stream_key = Redis_Key_Prefix_Stream + session_id
            timestamp = datetime.utcnow().isoformat()

            pipe = client.pipeline(transaction=True)

            for record in self.records:
                if not record.success:
                    continue

                state_key = Redis_Key_Prefix_State + session_id + ':' + record.model_name
                entity_key = record.object_name or record.object_id

                pipe.xadd(stream_key, {
                    'tool': record.tool_name,
                    'model': record.model_name,
                    'object_id': record.object_id,
                    'object_name': record.object_name,
                    'action': record.action,
                    'details': json.dumps(record.arguments, default=str),
                    'ts': timestamp,
                    'turn': str(conversation_turn),
                })

                if record.action == 'deleted':
                    pipe.hdel(state_key, entity_key)
                else:
                    snapshot_data = {
                        **record.arguments,
                        '_action': record.action,
                        '_modified': timestamp,
                        '_tool': record.tool_name,
                        '_turn': conversation_turn,
                        '_object_id': record.object_id,
                    }
                    pipe.hset(state_key, entity_key, json.dumps(snapshot_data, default=str))

            pipe.expire(stream_key, Redis_TTL_Seconds)
            pipe.execute()

            logger.info('Persisted %d tool execution records for session %s', len(self.records), session_id)

        except Exception as e:
            logger.warning('Failed to persist tool executions: %s', e)

# ################################################################################################################################

def get_state_snapshot(session_id:'str', model_name:'str'='') -> 'dict':
    """ Retrieves current state snapshot from Redis Hashes.
    Returns deduplicated view of what currently exists.
    """
    try:
        client = get_redis_client()

        if model_name:
            state_key = Redis_Key_Prefix_State + session_id + ':' + model_name
            raw = client.hgetall(state_key)
            out = {k: json.loads(v) for k, v in raw.items()}
            return out

        pattern = Redis_Key_Prefix_State + session_id + ':*'
        out = {}
        for key in client.scan_iter(match=pattern):
            model = key.split(':')[-1]
            raw = client.hgetall(key)
            out[model] = {k: json.loads(v) for k, v in raw.items()}

        return out

    except Exception as e:
        logger.warning('Failed to retrieve state snapshot: %s', e)
        return {}

# ################################################################################################################################

def get_event_log(session_id:'str', count:'int'=50) -> 'list':
    """ Retrieves event log from Redis Stream.
    Returns chronological list of all operations.
    """
    try:
        client = get_redis_client()
        stream_key = Redis_Key_Prefix_Stream + session_id
        entries = client.xrange(stream_key, count=count)

        out = []
        for event_id, data in entries:
            entry = {
                'event_id': event_id,
                'tool': data.get('tool', ''),
                'model': data.get('model', ''),
                'object_id': data.get('object_id', ''),
                'object_name': data.get('object_name', ''),
                'action': data.get('action', ''),
                'ts': data.get('ts', ''),
                'turn': data.get('turn', ''),
            }
            details = data.get('details', '{}')
            entry['details'] = json.loads(details) if details else {}
            out.append(entry)

        return out

    except Exception as e:
        logger.warning('Failed to retrieve event log: %s', e)
        return []

# ################################################################################################################################

def build_state_context(session_id:'str') -> 'str':
    """ Builds state snapshot context for LLM injection.
    Used for 'what did you do in this conversation' questions.
    """
    snapshot = get_state_snapshot(session_id)
    if not snapshot:
        return ''

    lines = ['## Objects you created or modified in this conversation\n']

    for model_name, objects in snapshot.items():
        lines.append(f'**{model_name}** ({len(objects)} operations):')
        for obj_name, fields in objects.items():
            action = fields.pop('_action', 'unknown')
            modified = fields.pop('_modified', '')
            _ = fields.pop('_tool', '')
            _ = fields.pop('_turn', '')
            _ = fields.pop('_object_id', '')
            field_str = ', '.join(f'{k}={v}' for k, v in fields.items() if not k.startswith('_'))
            lines.append(f'  - {obj_name} [{action} at {modified}]: {field_str}')

    lines.append('')
    lines.append('This is a log of what you did in this conversation, not a list of what currently exists in the system.')
    lines.append('When answering questions about what you created/modified/deleted, refer ONLY to this list.')

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def build_history_context(session_id:'str', count:'int'=30) -> 'str':
    """ Builds event history context for LLM injection.
    Used for 'what happened' questions.
    """
    events = get_event_log(session_id, count=count)
    if not events:
        return ''

    lines = [f'## Recent operations ({len(events)} events)\n']

    for event in events:
        action = event.get('action', '')
        model = event.get('model', '')
        obj_name = event.get('object_name', '')
        tool = event.get('tool', '')
        ts = event.get('ts', '')
        lines.append(f'  - {action} {model} "{obj_name}" via {tool} at {ts}')

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def build_execution_context(session_id:'str', question:'str'='') -> 'str':
    """ Builds appropriate execution context based on question intent.
    Routes to state snapshot or event history based on detected intent.
    """
    intent = detect_intent(question) if question else QueryIntent.Current_State

    if intent == QueryIntent.Current_State:
        return build_state_context(session_id)

    if intent == QueryIntent.Event_History:
        return build_history_context(session_id)

    state = build_state_context(session_id)
    history = build_history_context(session_id, count=10)
    if state and history:
        out = f'{state}\n\n--- Recent operations ---\n{history}'
    else:
        out = state or history
    return out

# ################################################################################################################################

def clear_session_state(session_id:'str') -> 'None':
    """ Clears all execution state for a session from Redis.
    Use when starting a new conversation or when state becomes stale.
    """
    try:
        client = get_redis_client()

        stream_key = Redis_Key_Prefix_Stream + session_id
        client.delete(stream_key)

        pattern = Redis_Key_Prefix_State + session_id + ':*'
        for key in client.scan_iter(match=pattern):
            client.delete(key)

        logger.info('Cleared execution state for session %s', session_id)

    except Exception as e:
        logger.warning('Failed to clear session state: %s', e)

# ################################################################################################################################
# ################################################################################################################################
