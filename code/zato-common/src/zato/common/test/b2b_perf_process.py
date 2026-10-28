# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from collections.abc import Callable
from http.client import responses
from math import ceil
from time import time

# gevent
from gevent import sleep, spawn
from gevent.event import Event
from gevent.pywsgi import WSGIServer

# Zato
from zato.common.b2b.common.business_log import Expiry_Batch_Size
from zato.common.b2b.common.recovery import Recovery_Page_Size
from zato.common.b2b.common.scheduler import recover_pages
from zato.common.test.b2b_perf_common import Expiry_Interval_Seconds, Line_Ready, load_config, parse_start_command, PerfMode, \
    PerfPath, RecordType, resident_memory_kb
from zato.common.test.b2b_perf_party import PerfExchange
from zato.common.test.b2b_perf_support import json_response
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.b2b.ebms2.inbound_common import HTTPResponse
    from zato.common.test.b2b_perf_common import PartyConfig
    from zato.common.typing_ import callable_, stranydict
    callable_ = callable_
    datetime = datetime
    HTTPResponse = HTTPResponse
    PartyConfig = PartyConfig
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

control_func = Callable[[bytes], 'HTTPResponse']

byteslist      = list[bytes]
strcontroldict = dict[str, control_func]

# ################################################################################################################################
# ################################################################################################################################

# How many connections wait in the listen queue of a party before the kernel drops new ones.
_listen_backlog = 1024

# ################################################################################################################################
# ################################################################################################################################

class PerfParty(PerfExchange):
    """ One party of a performance run in a process of its own, which starts messages at the rate of the run
    and answers the commands of the run that starts, follows and stops it.
    """

    def __init__(self, config:'PartyConfig') -> 'None':
        super().__init__(config)

        self.control:'strcontroldict' = {
            PerfPath.Start: self._on_start,
            PerfPath.Status: self._on_status,
            PerfPath.Stop: self._on_stop,
        }

        # How many greenlets start new messages at the moment.
        self.sending = 0

        self.stopped = Event()

        address = (config.listen_host, config.port)
        self.server = WSGIServer(address, self.handle, log=None, backlog=_listen_backlog)

# ################################################################################################################################

    def handle(self, environ:'stranydict', start_response:'callable_') -> 'byteslist':
        """ Answers one HTTP request - a message, or a command of the run.
        """
        path = environ['PATH_INFO']
        request_body = environ['wsgi.input'].read()

        if handler := self.control.get(path):
            response = handler(request_body)
        else:
            content_type = environ['CONTENT_TYPE']
            response = self.receive(path, content_type, request_body)

        reason = responses[response.status_code]
        status = f'{response.status_code} {reason}'
        headers = list(response.headers.items())

        start_response(status, headers)

        out = [response.body]
        return out

# ################################################################################################################################

    def _run_schedule(self, start_at:'float', end_at:'float') -> 'None':
        """ Starts new messages at the fixed rate of the run, whatever the time the earlier ones take. A party started
        again after the run began continues with the message that is due at the moment it starts.
        """
        rate = self.config.send_rate
        interval = 1 / rate

        total_seconds = end_at - start_at
        message_count = int(total_seconds * rate)

        now = time()
        elapsed = now - start_at

        if elapsed > 0:
            first_index = ceil(elapsed / interval)
        else:
            first_index = 0

        for index in range(first_index, message_count):
            offset = index * interval
            due_at = start_at + offset
            now = time()
            delay = due_at - now

            if delay > 0:
                sleep(delay)

            self.spawn_busy(self.send_new, self.config.send_kind)

        self.sending -= 1

# ################################################################################################################################

    def _on_start(self, body:'bytes') -> 'HTTPResponse':

        command = parse_start_command(body)

        window_start = command.start_at + command.warmup_seconds
        window_end = window_start + command.duration_seconds

        self.counter.window_start = window_start
        self.counter.window_end = window_end

        if self.config.send_rate:
            self.sending += 1
            _ = spawn(self._run_schedule, command.start_at, window_end)

        out = json_response({})
        return out

# ################################################################################################################################

    def _on_status(self, body:'bytes') -> 'HTTPResponse':

        outstanding = self.send_log.outstanding(1)
        open_count = len(outstanding)

        data:'stranydict' = {
            'open': open_count,
            'busy': self.busy,
            'sending': self.sending,
        }

        out = json_response(data)
        return out

# ################################################################################################################################

    def _on_stop(self, body:'bytes') -> 'HTTPResponse':

        record:'stranydict' = {
            'type': RecordType.Summary,
            'role': self.config.role,
            'statements': self.counter.statements,
            'commits': self.counter.commits,
            'total_statements': self.counter.total_statements,
            'body_selects': self.counter.body_selects,
            'resends': self.resends,
        }

        self.write(record)
        self.stopped.set()

        out = json_response({})
        return out

# ################################################################################################################################

    def _expire(self) -> 'None':
        """ Ends the business transactions whose deadline passed, once each interval, and records the deadline of each
        with the moment the check that found it started. The checks start at fixed moments, so the time a check takes
        does not delay the next one.
        """
        next_check_at = time()

        while not self.stopped.is_set():

            checked_at = time()
            now = self.clock.now()

            messages = self.business_log.due(now, Expiry_Batch_Size)
            self.business_log.record_timed_out_all(messages)

            for message in messages:

                # A transaction is due only through a deadline, so it always has one.
                deadline = cast_('datetime', message.earliest_deadline)

                record:'stranydict' = {
                    'type': RecordType.Timed_Out,
                    'id': message.message_id,
                    'deadline': deadline.timestamp(),
                    'checked_at': checked_at,
                }

                self.write(record)

            next_check_at += Expiry_Interval_Seconds
            now_seconds = time()
            delay = next_check_at - now_seconds

            if delay > 0:
                sleep(delay)

# ################################################################################################################################

    def recover(self) -> 'None':
        """ Continues from what the audit log holds - the business transactions, the exchanges that have not ended
        and the received messages whose delivery was not confirmed.
        """
        _ = self.business_log.recover()
        _ = recover_pages(self.send_log.recover_page, self.schedule_recovered, Recovery_Page_Size, 0)
        _ = recover_pages(self.receive_log.pending_page, self.deliver_recovered, Recovery_Page_Size, 0)

# ################################################################################################################################

    def run(self) -> 'None':
        """ Exchanges messages until the run stops the party.
        """
        self.recover()

        self.scheduler.start()
        self.server.start()

        _ = spawn(self._expire)

        print(Line_Ready, flush=True)

        _ = self.stopped.wait()

        self.server.stop()
        self.scheduler.stop()
        self.writer.stop()
        self.records.close()

# ################################################################################################################################

    def measure_recovery(self) -> 'None':
        """ Reads what the audit log has to recover and records how long that took, in how many statements,
        and the resident memory of the process afterwards.
        """
        started_at = time()

        transactions = self.business_log.recover()
        exchanges = self.send_log.recover()

        ended_at = time()
        duration = ended_at - started_at
        pid = os.getpid()
        rss_kb = resident_memory_kb(pid)

        record:'stranydict' = {
            'type': RecordType.Recovery,
            'duration_seconds': duration,
            'statements': self.counter.total_statements,
            'transactions': transactions,
            'exchanges': exchanges,
            'rss_kb': rss_kb,
        }

        self.write(record)

        self.writer.stop()
        self.records.close()

# ################################################################################################################################
# ################################################################################################################################

def run_party(party_class:'type[PerfParty]') -> 'None':
    """ Runs one party of the given class with the configuration file the command line names.
    """
    config_path = sys.argv[1]
    config = load_config(config_path)

    party = party_class(config)

    if config.mode == PerfMode.Recover:
        party.measure_recovery()
    else:
        party.run()

# ################################################################################################################################

def main() -> 'None':
    run_party(PerfParty)

# ################################################################################################################################
# ################################################################################################################################
