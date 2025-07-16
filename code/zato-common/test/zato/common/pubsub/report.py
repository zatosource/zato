# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections import defaultdict
from datetime import datetime
from itertools import groupby

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections import defaultdict
    from datetime import datetime
    from typing import Dict, List, Tuple
    
    from zato.common.test.zato.common.pubsub.models import Message, TestCollector, QueueStats

# ################################################################################################################################
# ################################################################################################################################

def _format_time(dt:'datetime') -> 'str':
    """ Format a datetime object for display in the report.
    """
    if not dt:
        return 'N/A'
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

# ################################################################################################################################
# ################################################################################################################################

def _calculate_queue_stats(collector:'TestCollector') -> 'dict':
    """ Calculate statistics for each queue based on collected messages.
    """
    # Group messages by queue
    messages_by_queue = defaultdict(list)
    
    for message in collector.messages:
        messages_by_queue[message.queue_name].append(message)
    
    # Calculate stats for each queue
    queue_stats = {}
    
    for queue_name, queue_messages in messages_by_queue.items():
        stats = {
            'count': len(queue_messages),
            'avg_size': sum(len(str(m.content)) for m in queue_messages) / len(queue_messages) if queue_messages else 0,
            'avg_priority': sum(m.priority for m in queue_messages) / len(queue_messages) if queue_messages else 0,
            'avg_expiration': sum(m.expiration for m in queue_messages) / len(queue_messages) if queue_messages else 0,
        }
        
        # Calculate processing times
        if queue_messages:
            processing_times = []
            for msg in queue_messages:
                pub_time = msg.publication_time
                recv_time = msg.received_time
                if pub_time and recv_time:
                    # Processing time in milliseconds
                    processing_time = (recv_time - pub_time).total_seconds() * 1000
                    processing_times.append(processing_time)
            
            if processing_times:
                stats['min_processing_time'] = min(processing_times)
                stats['max_processing_time'] = max(processing_times)
                stats['avg_processing_time'] = sum(processing_times) / len(processing_times)
            
        queue_stats[queue_name] = stats
    
    return queue_stats

# ################################################################################################################################
# ################################################################################################################################

def _calculate_topic_stats(collector:'TestCollector') -> 'dict':
    """ Calculate statistics for each topic based on collected messages.
    """
    # Group messages by topic
    messages_by_topic = defaultdict(list)
    
    for message in collector.messages:
        messages_by_topic[message.topic_name].append(message)
    
    # Calculate stats for each topic
    topic_stats = {}
    
    for topic_name, topic_messages in messages_by_topic.items():
        stats = {
            'count': len(topic_messages),
            'publishers': len(set(m.publisher_name for m in topic_messages)),
            'queues': len(set(m.queue_name for m in topic_messages)),
        }
        topic_stats[topic_name] = stats
    
    return topic_stats

# ################################################################################################################################
# ################################################################################################################################

def _generate_summary_section(collector:'TestCollector') -> 'str':
    """ Generate the summary section of the HTML report.
    """
    duration = collector.get_duration_seconds()
    message_rate = collector.get_message_rate()
    status = "Complete" if collector.is_complete() else "Incomplete"
    
    html = f"""
    <section class="summary">
        <h2>Test Summary</h2>
        <table>
            <tr>
                <th>Status</th>
                <td>{status}</td>
            </tr>
            <tr>
                <th>Messages Collected</th>
                <td>{collector.received_count} / {collector.expected_count}</td>
            </tr>
            <tr>
                <th>Test Duration</th>
                <td>{duration:.2f} seconds</td>
            </tr>
            <tr>
                <th>Message Rate</th>
                <td>{message_rate:.2f} messages/second</td>
            </tr>
            <tr>
                <th>Start Time</th>
                <td>{_format_time(collector.start_time)}</td>
            </tr>
            <tr>
                <th>End Time</th>
                <td>{_format_time(collector.end_time)}</td>
            </tr>
            <tr>
                <th>Duplicate Messages</th>
                <td>{collector.duplicate_count}</td>
            </tr>
            <tr>
                <th>Malformed Messages</th>
                <td>{collector.malformed_count}</td>
            </tr>
        </table>
    </section>
    """
    
    return html

# ################################################################################################################################
# ################################################################################################################################

def _generate_queue_stats_section(collector:'TestCollector') -> 'str':
    """ Generate the queue statistics section of the HTML report.
    """
    queue_stats = _calculate_queue_stats(collector)
    
    if not queue_stats:
        return "<section><h2>Queue Statistics</h2><p>No queue data available.</p></section>"
    
    html = """
    <section class="queue-stats">
        <h2>Queue Statistics</h2>
        <table>
            <thead>
                <tr>
                    <th>Queue Name</th>
                    <th>Message Count</th>
                    <th>Avg Processing Time (ms)</th>
                    <th>Min Processing Time (ms)</th>
                    <th>Max Processing Time (ms)</th>
                    <th>Avg Message Size</th>
                    <th>Avg Priority</th>
                    <th>Avg Expiration</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for queue_name, stats in queue_stats.items():
        avg_proc_time = stats.get('avg_processing_time', 'N/A')
        min_proc_time = stats.get('min_processing_time', 'N/A')
        max_proc_time = stats.get('max_processing_time', 'N/A')
        
        if avg_proc_time != 'N/A':
            avg_proc_time = f"{avg_proc_time:.2f}"
        if min_proc_time != 'N/A':
            min_proc_time = f"{min_proc_time:.2f}"
        if max_proc_time != 'N/A':
            max_proc_time = f"{max_proc_time:.2f}"
            
        html += f"""
            <tr>
                <td>{queue_name}</td>
                <td>{stats['count']}</td>
                <td>{avg_proc_time}</td>
                <td>{min_proc_time}</td>
                <td>{max_proc_time}</td>
                <td>{stats['avg_size']:.1f} bytes</td>
                <td>{stats['avg_priority']:.1f}</td>
                <td>{stats['avg_expiration']:.1f} sec</td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
    </section>
    """
    
    return html

# ################################################################################################################################
# ################################################################################################################################

def _generate_topic_stats_section(collector:'TestCollector') -> 'str':
    """ Generate the topic statistics section of the HTML report.
    """
    topic_stats = _calculate_topic_stats(collector)
    
    if not topic_stats:
        return "<section><h2>Topic Statistics</h2><p>No topic data available.</p></section>"
    
    html = """
    <section class="topic-stats">
        <h2>Topic Statistics</h2>
        <table>
            <thead>
                <tr>
                    <th>Topic Name</th>
                    <th>Message Count</th>
                    <th>Publishers</th>
                    <th>Queues</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for topic_name, stats in topic_stats.items():
        html += f"""
            <tr>
                <td>{topic_name}</td>
                <td>{stats['count']}</td>
                <td>{stats['publishers']}</td>
                <td>{stats['queues']}</td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
    </section>
    """
    
    return html

# ################################################################################################################################
# ################################################################################################################################

def generate_html_report(collector:'TestCollector') -> 'str':
    """ Generate a complete HTML report from the test collector data.
    """
    html_template = """<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>PubSub Test Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }
            h1, h2 { color: #0066cc; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .summary { margin-bottom: 30px; }
            .warning { color: #cc4400; }
            .success { color: #007700; }
        </style>
    </head>
    <body>
        <h1>PubSub Test Report</h1>
        <p>Generated on: {timestamp}</p>
        
        {summary_section}
        
        {queue_stats_section}
        
        {topic_stats_section}
    </body>
    </html>
    """
    
    # Generate sections
    summary_section = _generate_summary_section(collector)
    queue_stats_section = _generate_queue_stats_section(collector)
    topic_stats_section = _generate_topic_stats_section(collector)
    
    # Format the template
    html = html_template.format(
        timestamp=_format_time(datetime.utcnow()),
        summary_section=summary_section,
        queue_stats_section=queue_stats_section,
        topic_stats_section=topic_stats_section
    )
    
    return html

# ################################################################################################################################
# ################################################################################################################################
