# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import signal
import sys
from datetime import datetime

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from types import FrameType

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Log records at the error and warning levels ..
    Error_Record_Pattern   = re.compile(r' - (?:ERROR|CRITICAL) - ')
    Warning_Record_Pattern = re.compile(r' - WARN(?:ING)? - ')

    # .. log records at the levels below them, whose traceback, when they carry one, is diagnostic detail ..
    Detail_Record_Pattern = re.compile(r' - (?:DEBUG|INFO) - ')

    # .. and all the levels as the tracing crate of the Rust components formats them, after a UTC timestamp
    # and with or without ANSI colors ..
    Tracing_Error_Record_Pattern   = re.compile(r'\d{4}-\d\d-\d\dT[\d:.]+Z(?:\x1b\[[\d;]*m)?\s+(?:\x1b\[[\d;]*m)?\s*ERROR\b')
    Tracing_Warning_Record_Pattern = re.compile(r'\d{4}-\d\d-\d\dT[\d:.]+Z(?:\x1b\[[\d;]*m)?\s+(?:\x1b\[[\d;]*m)?\s*WARN\b')
    Tracing_Detail_Record_Pattern  = re.compile(r'\d{4}-\d\d-\d\dT[\d:.]+Z(?:\x1b\[[\d;]*m)?\s+(?:\x1b\[[\d;]*m)?\s*(?:TRACE|DEBUG|INFO)\b')

    # .. a record that pytest repeats in the captured log of a failure, which is already counted, so neither the record
    # nor its traceback counts again, whatever its level ..
    Captured_Record_Pattern = re.compile(r'^(?:DEBUG|INFO|WARNING|ERROR|CRITICAL) +\S+:\S+:\d+ ')

    # .. a line of the server output that a test provokes deliberately, which is detail whatever its level,
    # identical to Expected_Record_Marker of zato.common.test.conftest_base_pubsub ..
    Expected_Record_Marker = '[Expected]'

    # .. the line that the failure_reports pytest plugin writes for each failure ..
    Failure_Marker = '>>> ZATO TEST FAILURE'

    # .. the line that pytest writes when a conftest cannot be loaded, before any plugin of the session runs ..
    Conftest_Failure_Pattern = re.compile(r'^\w+Error while loading conftest ')

    # .. the first line of a traceback ..
    Traceback_Marker = 'Traceback (most recent call last)'

    # .. the lines that join a chained traceback to the one before it, which was already classified ..
    Chained_Traceback_Markers = {
        'During handling of the above exception, another exception occurred:',
        'The above exception was the direct cause of the following exception:',
    }

    # .. a Python warning, such as a DeprecationWarning or an SAWarning ..
    Python_Warning_Pattern = re.compile(r'\b[A-Z]\w*Warning: ')

    # .. and the errors, warnings and failed tests that cargo reports.
    Cargo_Error_Pattern   = re.compile(r'^error(?:\[E\d+\])?: |^test .+ \.\.\. FAILED$')
    Cargo_Warning_Pattern = re.compile(r'^warning: ')

    # The header of any pytest section, and of the section that repeats the warnings of the session
    Section_Header_Pattern   = re.compile(r'^=+ .+ =+$')
    Warnings_Summary_Pattern = re.compile(r'^=+ warnings summary =+$')

    Timestamp_Format = '%Y-%m-%d %H:%M:%S'
    Count_Width      = 3

    Color_Error   = '\033[31m'
    Color_Warning = '\033[33m'
    Color_Reset   = '\033[0m'

    # The file, next to the log file, that holds the counts across the recipe lines of one target
    Counts_Suffix = '.counts'

    # The number of interrupts after which the output is no longer read to its end
    Interrupt_Limit       = 2
    Exit_Code_Interrupted = 130

# ################################################################################################################################
# ################################################################################################################################

class LogCounter:
    """ Reads the output of a recipe line, prefixes each line with the number of errors and warnings seen so far
    and with a timestamp, writes it to the console, in color when the console is a terminal, and appends it to the log file.
    """
    def __init__(self, log_path:'str') -> 'None':
        self.log_path = log_path
        self.counts_path = log_path + ModuleCtx.Counts_Suffix

        self.error_count   = 0
        self.warning_count = 0

        self.interrupt_count     = 0
        self.previous_is_record  = False
        self.in_warnings_summary = False
        self.is_chained          = False

        self.is_console_open = True
        self.use_color       = sys.stdout.isatty()

        self.load_counts()

# ################################################################################################################################

    def load_counts(self) -> 'None':
        """ Continues from the counts of the previous recipe lines of the same target.
        """
        if os.path.exists(self.counts_path):
            with open(self.counts_path) as counts_file:
                error_count, warning_count = counts_file.read().split()
                self.error_count   = int(error_count)
                self.warning_count = int(warning_count)

# ################################################################################################################################

    def save_counts(self) -> 'None':
        with open(self.counts_path, 'w') as counts_file:
            _ = counts_file.write(f'{self.error_count} {self.warning_count}\n')

# ################################################################################################################################

    def on_interrupt(self, signum:'int', frame:'FrameType | None') -> 'None':
        """ Keeps reading after the first interrupt, so the output of the teardown of the tests is not lost,
        and stops at once after the second one.
        """
        self.interrupt_count += 1

        if self.interrupt_count >= ModuleCtx.Interrupt_Limit:
            self.save_counts()
            os._exit(ModuleCtx.Exit_Code_Interrupted)

# ################################################################################################################################

    def classify(self, line:'str') -> 'None':
        """ Updates the counts with what a single line of output holds.
        """
        # A pytest section header begins or ends the summary of warnings ..
        if ModuleCtx.Section_Header_Pattern.match(line):
            self.in_warnings_summary = bool(ModuleCtx.Warnings_Summary_Pattern.match(line))
            self.previous_is_record = False
            return

        # .. which repeats the warnings that were already counted ..
        if self.in_warnings_summary:
            return

        # .. a record that a test provokes deliberately is detail, and so is the traceback that it carries ..
        if ModuleCtx.Expected_Record_Marker in line:
            self.previous_is_record = True
            self.is_chained = False
            return

        stripped = line.strip()

        # .. a chained traceback continues the traceback before it, so it is classified as that one was ..
        if stripped in ModuleCtx.Chained_Traceback_Markers:
            self.is_chained = True
            return

        # .. with only the empty lines around the joining line between the two ..
        if self.is_chained and not stripped:
            return

        is_error = bool(ModuleCtx.Error_Record_Pattern.search(line)) \
            or bool(ModuleCtx.Tracing_Error_Record_Pattern.search(line)) \
            or ModuleCtx.Failure_Marker in line \
            or bool(ModuleCtx.Conftest_Failure_Pattern.match(line)) \
            or bool(ModuleCtx.Cargo_Error_Pattern.match(line))

        is_warning = bool(ModuleCtx.Warning_Record_Pattern.search(line)) \
            or bool(ModuleCtx.Tracing_Warning_Record_Pattern.search(line)) \
            or bool(ModuleCtx.Python_Warning_Pattern.search(line)) \
            or bool(ModuleCtx.Cargo_Warning_Pattern.match(line))

        is_detail = bool(ModuleCtx.Detail_Record_Pattern.search(line)) \
            or bool(ModuleCtx.Tracing_Detail_Record_Pattern.search(line)) \
            or bool(ModuleCtx.Captured_Record_Pattern.match(line))

        # .. an error record, a failure or a cargo error is an error ..
        if is_error:
            self.error_count += 1

        # .. a warning record, a Python warning or a cargo warning is a warning, including the traceback it carries ..
        elif is_warning:
            self.warning_count += 1

        # .. and a traceback is an error, unless it belongs to a log record on the same line or directly before it.
        elif ModuleCtx.Traceback_Marker in line:
            if not (self.previous_is_record or is_detail or self.is_chained):
                self.error_count += 1

        self.previous_is_record = is_error or is_warning or is_detail
        self.is_chained = False

# ################################################################################################################################

    def get_prefix(self, use_color:'bool') -> 'str':
        errors   = str(self.error_count).zfill(ModuleCtx.Count_Width)
        warnings = str(self.warning_count).zfill(ModuleCtx.Count_Width)

        if use_color:
            if self.error_count:
                errors = f'{ModuleCtx.Color_Error}{errors}{ModuleCtx.Color_Reset}'
            if self.warning_count:
                warnings = f'{ModuleCtx.Color_Warning}{warnings}{ModuleCtx.Color_Reset}'

        out = f'{errors}-{warnings}'
        return out

# ################################################################################################################################

    def write_console(self, text:'str') -> 'None':
        """ Writes to the console for as long as it is open, while the log file still receives every line.
        """
        if not self.is_console_open:
            return

        try:
            _ = sys.stdout.buffer.write(text.encode('utf8'))
            _ = sys.stdout.buffer.flush()
        except OSError:
            self.is_console_open = False

# ################################################################################################################################

    def run(self) -> 'int':
        """ Processes the output until its writers close it, and returns the exit code of the process.
        """
        _ = signal.signal(signal.SIGINT, self.on_interrupt)

        with open(self.log_path, 'a', encoding='utf8') as log_file:

            # Read each line as soon as it is complete ..
            while line := sys.stdin.buffer.readline():
                text = line.decode('utf8', errors='replace').rstrip('\n')

                # .. count what it holds ..
                self.classify(text)
                timestamp = datetime.now().strftime(ModuleCtx.Timestamp_Format)

                # .. write it to the log file without colors ..
                _ = log_file.write(f'{self.get_prefix(False)} {timestamp} {text}\n')
                log_file.flush()

                # .. and to the console, in color if the console is a terminal.
                self.write_console(f'{self.get_prefix(self.use_color)} {timestamp} {text}\n')

        self.save_counts()
        return 0

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    log_counter = LogCounter(sys.argv[1])
    sys.exit(log_counter.run())

# ################################################################################################################################
# ################################################################################################################################
