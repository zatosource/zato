# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import re
import time
from datetime import datetime, timedelta
from http.client import BAD_REQUEST
from os.path import expanduser
from traceback import format_exc

ansi_escape_pattern = re.compile(r'\x1b\[[0-9;]*m')

# Django
from django.http import JsonResponse, StreamingHttpResponse

# Zato
from zato.admin.web.views import method_allowed

import logging
logger = logging.getLogger(__name__)

def parse_log_line(line):
    """ Parse a log line into components.
    Format: YYYY-MM-DD HH:MM:SS,mmm - LEVEL - PID:Thread - logger:line - message
    """
    result = {
        'raw': line,
        'timestamp': None,
        'level': None,
        'pid': None,
        'thread': None,
        'logger': None,
        'message': None,
    }

    try:
        clean_line = ansi_escape_pattern.sub('', line)
        parts = clean_line.split(' - ', 4)
        if len(parts) >= 5:
            result['timestamp'] = parts[0].strip()
            level_raw = parts[1].strip().lower()
            result['level'] = level_raw.strip('[]')
            pid_thread = parts[2].strip()
            if ':' in pid_thread:
                pid_part, thread_part = pid_thread.split(':', 1)
                result['pid'] = pid_part
                result['thread'] = thread_part
            result['logger'] = parts[3].strip()
            result['message'] = parts[4].strip()
    except Exception:
        pass

    return result

def filter_by_time_range(timestamp_str, time_range):
    """ Check if timestamp falls within the specified time range.
    time_range can be: 15m, 1h, 4h, 1d, 2d, 7d, or a custom range like 'start,end'
    """
    if not timestamp_str or not time_range or time_range == 'live':
        return True

    try:
        log_time = datetime.strptime(timestamp_str.split(',')[0], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return True

    now = datetime.now()

    if time_range == '15m':
        cutoff = now - timedelta(minutes=15)
    elif time_range == '1h':
        cutoff = now - timedelta(hours=1)
    elif time_range == '4h':
        cutoff = now - timedelta(hours=4)
    elif time_range == '1d':
        cutoff = now - timedelta(days=1)
    elif time_range == '2d':
        cutoff = now - timedelta(days=2)
    elif time_range == '7d':
        cutoff = now - timedelta(days=7)
    elif time_range == '15d':
        cutoff = now - timedelta(days=15)
    elif time_range == '1M':
        cutoff = now - timedelta(days=30)
    elif ',' in time_range:
        try:
            start_str, end_str = time_range.split(',')
            start_time = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
            return start_time <= log_time <= end_time
        except ValueError:
            return True
    else:
        return True

    return log_time >= cutoff

@method_allowed('GET')
def stream_logs(req):
    """ Stream log file contents via SSE. """

    file_path = req.GET.get('path', '')
    levels = req.GET.get('levels', '')
    time_range = req.GET.get('time_range', 'live')
    from_end = req.GET.get('from_end', '500')

    if not file_path:
        return JsonResponse({'success': False, 'error': 'Missing path parameter'}, status=BAD_REQUEST)

    file_path = expanduser(file_path)

    if not os.path.isfile(file_path):
        return JsonResponse({'success': False, 'error': 'File not found'}, status=BAD_REQUEST)

    level_filter = set()
    if levels:
        level_filter = set(levels.lower().split(','))

    try:
        from_end_lines = int(from_end)
    except ValueError:
        from_end_lines = 500

    def generate_events():
        logger.info('[log-viewer] generate_events started for file_path=%s', file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                logger.info('[log-viewer] file opened successfully')

                f.seek(0, 2)
                file_size = f.tell()
                logger.info('[log-viewer] file_size=%s, from_end_lines=%s', file_size, from_end_lines)

                if from_end_lines > 0 and file_size > 0:
                    chunk_size = 8192
                    lines_found = []
                    position = file_size

                    while position > 0 and len(lines_found) < from_end_lines + 1:
                        read_size = min(chunk_size, position)
                        position -= read_size
                        f.seek(position)
                        chunk = f.read(read_size)
                        lines_found = chunk.splitlines() + lines_found

                    initial_lines = lines_found[-from_end_lines:] if len(lines_found) > from_end_lines else lines_found
                    logger.info('[log-viewer] initial_lines count=%s', len(initial_lines))

                    yielded_initial = 0
                    for line in initial_lines:
                        if not line.strip():
                            continue

                        parsed = parse_log_line(line)

                        if level_filter and parsed['level'] and parsed['level'] not in level_filter:
                            continue

                        if not filter_by_time_range(parsed['timestamp'], time_range):
                            continue

                        yielded_initial += 1
                        yield 'data: {}\n\n'.format(json.dumps(parsed))

                    logger.info('[log-viewer] yielded %s initial lines', yielded_initial)

                f.seek(0, 2)
                last_position = f.tell()
                logger.info('[log-viewer] starting tail loop at position=%s', last_position)
                poll_count = 0

                while True:
                    poll_count += 1
                    if poll_count == 1:
                        logger.info('[log-viewer] first poll iteration starting')

                    f.seek(0, 2)
                    end_position = f.tell()

                    diff = end_position - last_position
                    if poll_count <= 3 or poll_count % 100 == 0 or diff > 0:
                        logger.info('[log-viewer] poll_count=%s, last_position=%s, end_position=%s, diff=%s',
                            poll_count, last_position, end_position, diff)

                    if end_position < last_position:
                        logger.info('[log-viewer] file truncated, resetting to start')
                        last_position = 0
                        f.seek(0)
                    elif end_position > last_position:
                        f.seek(last_position)

                    new_lines = 0
                    filtered_level = 0
                    filtered_time = 0
                    while True:
                        line = f.readline()
                        if not line:
                            break

                        last_position = f.tell()
                        line = line.rstrip('\n\r')

                        if not line.strip():
                            continue

                        parsed = parse_log_line(line)

                        if level_filter and parsed['level'] and parsed['level'] not in level_filter:
                            filtered_level += 1
                            if filtered_level <= 5:
                                logger.info('[log-viewer] filtered: level=%r not in %r, line=%r', parsed['level'], level_filter, line[:120])
                            continue

                        if not filter_by_time_range(parsed['timestamp'], time_range):
                            filtered_time += 1
                            continue

                        new_lines += 1
                        yield 'data: {}\n\n'.format(json.dumps(parsed))

                    if new_lines > 0 or filtered_level > 0 or filtered_time > 0:
                        logger.info('[log-viewer] new_lines=%s, filtered_level=%s, filtered_time=%s, level_filter=%s',
                            new_lines, filtered_level, filtered_time, level_filter)

                    try:
                        yield ': keepalive\n\n'
                    except Exception as yield_err:
                        logger.info('[log-viewer] yield failed: %s', yield_err)
                        break
                    time.sleep(0.3)

        except GeneratorExit:
            logger.info('[log-viewer] generator exit (client disconnected)')
        except Exception:
            error_msg = format_exc()
            logger.warning('[log-viewer] error streaming logs: %s', error_msg)
            yield 'event: error\ndata: {}\n\n'.format(error_msg.replace('\n', '\\n'))

    response = StreamingHttpResponse(generate_events(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response

@method_allowed('GET')
def get_log_history(req):
    """ Get historical log lines with filtering. """

    file_path = req.GET.get('path', '')
    levels = req.GET.get('levels', '')
    time_range = req.GET.get('time_range', '')
    limit = req.GET.get('limit', '1000')

    if not file_path:
        return JsonResponse({'success': False, 'error': 'Missing path parameter'}, status=BAD_REQUEST)

    file_path = expanduser(file_path)

    if not os.path.isfile(file_path):
        return JsonResponse({'success': False, 'error': 'File not found'}, status=BAD_REQUEST)

    level_filter = set()
    if levels:
        level_filter = set(levels.lower().split(','))

    try:
        max_lines = int(limit)
    except ValueError:
        max_lines = 1000

    try:
        lines = []
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.rstrip('\n\r')
                if not line.strip():
                    continue

                parsed = parse_log_line(line)

                if level_filter and parsed['level'] and parsed['level'] not in level_filter:
                    continue

                if not filter_by_time_range(parsed['timestamp'], time_range):
                    continue

                lines.append(line)

                if len(lines) >= max_lines:
                    break

        return JsonResponse({'success': True, 'lines': lines})

    except Exception:
        error_msg = format_exc()
        logger.warning('Error reading logs: %s', error_msg)
        return JsonResponse({'success': False, 'error': str(error_msg)}, status=BAD_REQUEST)
