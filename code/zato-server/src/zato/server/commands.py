# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime
from inspect import isclass
from logging import getLogger

# gevent
from gevent import spawn
from gevent.subprocess import run as subprocess_run, TimeoutExpired

# Humanize
from humanize import naturalsize

# Zato
from zato.common.marshal_.api import Model
from zato.common.util.platform_ import is_windows
from zato.common.typing_ import cast_
from zato.common.util import new_cid
from zato.common.util.api import get_zato_command

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from gevent.subprocess import CompletedProcess
    from zato.common.typing_ import any_
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Config:
    UsePubSub   = False
    Timeout     = 600.0 # In seconds
    Encoding    = 'utf8'
    ReplaceChar = '�' # U+FFFD � REPLACEMENT CHARACTER

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CommandResult(Model):

    cid:        'str'
    command:    'str'
    callback:   'any_' = None
    stdin:      'str'  = ''
    stdout:     'str'  = ''
    stderr:     'str'  = ''
    is_async:   'bool' = False
    use_pubsub: 'bool' = Config.UsePubSub

    is_ok:     'bool'  = False
    timeout:   'float' = Config.Timeout
    exit_code: 'int'   = -1

    len_stdout_bytes: 'int' = 0
    len_stderr_bytes: 'int' = 0

    len_stdout_human: 'str' = ''
    len_stderr_human: 'str' = ''

    encoding:     'str' = Config.Encoding
    replace_char: 'str' = Config.ReplaceChar

    is_timeout: 'bool' = False
    timeout_msg:'str '= ''

    start_time:    'datetime' = None # type: ignore
    start_time_iso:'str' = ''
    end_time:      'datetime' = None # type: ignore
    end_time_iso:  'str' = ''

    total_time:     'str' = ''
    total_time_sec: 'float' = -1.0

# ################################################################################################################################
# ################################################################################################################################

class CommandsFacade:
    """ An accessor object through which shell commands can be invoked.
    """
    server: 'ParallelServer'

    def init(self, server:'ParallelServer') -> 'None':
        self.server = server

    def _append_time_details(self, out:'CommandResult') -> 'None':

        # .. compute the command's end time ..
        out.end_time = datetime.utcnow()
        out.end_time_iso = out.end_time.isoformat()

        total_time = (out.end_time - out.start_time)
        out.total_time = str(total_time)
        out.total_time_sec = total_time.total_seconds()

# ################################################################################################################################

    def _append_result_details(
        self,
        out:         'CommandResult',
        result:      'CompletedProcess', # type: ignore
        encoding:    'str',
        replace_char:'str',
    ) -> 'None':

        # .. otherwise, we process the result received from the command ..

        # .. populate our output object with basic information ..
        out.command   = result.args
        out.exit_code = result.returncode

        # For now, we assume that only exit code 0 means success
        out.is_ok = out.exit_code == 0

        # Try to parse out string objects out of bytes. We assume that this will succeed.
        # But, if that fails, we will repeat, asking Python to give us
        # a string with the Unicode default replace character's instances inside. At this point,
        # we may still want to use our own character instead of the default one.

        # First, stdout ..
        try:
            stdout:'str' = result.stdout.decode(encoding)
        except UnicodeDecodeError:
            stdout:'str' = result.stdout.decode(encoding, 'replace') # type: str
            if replace_char != Config.ReplaceChar:
                stdout = stdout.replace(Config.ReplaceChar, replace_char)

        # .. now, stderr ..
        try:
            stderr:'str' = result.stderr.decode(encoding)
        except UnicodeDecodeError:
            stderr:'str' = result.stderr.decode(encoding, 'replace') # type: str
            if replace_char != Config.ReplaceChar:
                stderr = stderr.replace(Config.ReplaceChar, replace_char)

        out.stdout = stdout
        out.stderr = stderr

        out.encoding = encoding
        out.replace_char = replace_char

# ################################################################################################################################

    def _run(
        self,
        *,
        cid:      'str',
        command:  'str',
        callback: 'any_',
        stdin:    'any_',
        timeout:  'float',
        encoding: 'str',
        replace_char: 'str',
        use_pubsub: 'bool'
    ) -> 'CommandResult':

        # Our response to produce
        out = CommandResult()

        # Make sure stdin is a bytes object, as expected by the underlying implementation ..

        # .. make a copy because we are returning it on output 1:1 in a moment ..
        orig_stdin = stdin

        # .. now,
        if not isinstance(stdin, bytes):
            stdin = stdin.encode(encoding)

        # This is taken 1:1 from input parameters
        out.cid = cid
        out.command  = command
        out.stdin    = orig_stdin
        out.timeout  = timeout
        out.encoding = encoding

        # Invoke the subprocess ..
        try:
            # Log what we are about to do ..
            logger.info('Invoking command: `%s` (%s)', command, cid)

            # .. start measuring the response time ..
            out.start_time = datetime.utcnow()
            out.start_time_iso = out.start_time.isoformat()

            # .. this needs to be None if we do not want it
            timeout = cast_('float', timeout or None)

            # .. invoke the command ..
            result:'CompletedProcess' = subprocess_run( # type: ignore
                command, input=stdin, timeout=timeout, shell=True, capture_output=True)

            # .. if we are here, it means that there was no timeout ..

            # .. store the length of stdout and stderr in bytes, before we convert them to string objects ..
            out.len_stdout_bytes = len(result.stdout)
            out.len_stderr_bytes = len(result.stderr)

            out.len_stdout_human = naturalsize(out.len_stdout_bytes)
            out.len_stderr_human = naturalsize(out.len_stderr_bytes)

            # .. first, append end time-related details ..
            self._append_time_details(out)

            # .. now, populate details of the actual command's result ..
            self._append_result_details(out, result, encoding, replace_char)

        # .. we enter here if the command timed out ..
        except TimeoutExpired as e:

            # .. append details about how long the command took ..
            self._append_time_details(out)

            # .. populate timeout metadata ..
            out.is_timeout = True
            out.timeout_msg = str(e)

            # .. replace ' seconds' with ' sec.' to avoid expressions like '1 seconds' ..
            # .. (we assume that there will be only one such instance in the string) ..
            if out.timeout_msg.endswith(' seconds'):
                out.timeout_msg = out.timeout_msg.replace(' seconds', ' sec.')

            # .. issue information about what happened ..
            logger.warning('Timeout: %s (%s)', out.timeout_msg, cid)

        # .. we get here only if there was no timeout ..
        else:
            logger.info('Command `%s` completed in %s, exit_code -> %s; len-out=%s (%s); len-err=%s (%s); cid -> %s',
                command, out.total_time, out.exit_code,
                out.len_stdout_bytes,
                out.len_stdout_human,
                out.len_stderr_bytes,
                out.len_stderr_human,
                cid)

        # .. no matter if there was a timeout or not, we can invoke our callback, if we have any,
        # .. and return our output now ..
        finally:

            # .. run the callback ..
            if callback:
                self._run_callback(cid, callback, out, use_pubsub)

            # .. return the output, assuming that the callback did not raise an exception.
            return out

# ################################################################################################################################

    def _run_callback(self, cid:'str', callback:'any_', result:'CommandResult', use_pubsub:'bool') -> 'None':

        # We need to import it here to avoid circular references
        from zato.server.service import Service

        # Local aliases
        is_service = isclass(callback) and issubclass(callback, Service)

        # This is a function or another callable, but not a service, and we can invoke that callable as is
        if callable(callback) and (not is_service):
            _ = callback(result)

        else:

            # We are going to publish a message to the target (service or topic) by its name ..
            if use_pubsub:
                func = self.server.publish
                data_key   = 'data'
                target_key = 'name'
                result = result.to_dict() # type: ignore

            # We are going to invoke the taret synchronously
            else:
                func = self.server.invoke
                data_key = 'request'
                target_key = 'service'

            # Extract the service's name ..
            if is_service:
                target = callback.get_name() # type: ignore

            # .. or use it directly ..
            else:
                target = callback

            # Now, we are ready to invoke the callable
            func(**{
                data_key:   result,
                target_key: target,
                'cid': cid
            }) # type: ignore

# ################################################################################################################################

    def invoke_async(
        self,
        command:'str',
        *,
        cid:         'str'   = '',
        timeout:     'float' = Config.Timeout,
        callback:    'any_'  = None,
        stdin:       'str'   = '',
        encoding:    'str'   = Config.Encoding,
        use_pubsub:  'bool'  = Config.UsePubSub,
        replace_char:'str'   = Config.ReplaceChar,
    ) -> 'CommandResult':

        # Accept input or create a new Correlation ID
        cid = cid or 'zcma' + new_cid()

        # For consistency, we return the same object that self.invoke does
        out = CommandResult()
        out.cid = cid
        out.command = command
        out.stdin = stdin
        out.timeout = timeout
        out.encoding = encoding
        out.replace_char = replace_char
        out.is_async = True
        out.is_ok = True
        out.use_pubsub = use_pubsub

        # .. run in background ..
        _ = spawn(
            self.invoke, cid=cid, command=command, callback=callback, stdin=stdin, timeout=timeout,
            use_pubsub=use_pubsub, encoding=encoding, replace_char=replace_char)

        # .. and return the basic information to our caller ..
        return out

# ################################################################################################################################

    def invoke(
        self,
        command:'str',
        *,
        cid:         'str'   = '',
        timeout:     'float' = Config.Timeout,
        callback:    'any_'  = None,
        stdin:       'str'   = '',
        encoding:    'str'   = Config.Encoding,
        use_pubsub:  'bool'  = Config.UsePubSub,
        replace_char:'str'   = Config.ReplaceChar,
    ) -> 'CommandResult':

        # Accept input or create a new Correlation ID
        cid = cid or 'zcmd' + new_cid()

        return self._run(
            cid=cid, command=command, callback=callback, stdin=stdin, timeout=timeout, encoding=encoding,
            use_pubsub=use_pubsub, replace_char=replace_char)

# ################################################################################################################################

    def run_zato_cli_async(
        self,
        command:  'str',
        callback: 'any_'  = None,
    ) -> 'CommandResult':

        # This will differ depending on our current OS
        zato_bin = 'zato.bat' if is_windows else get_zato_command()

        # Build the full command to execute
        command = f'{zato_bin} {command}'

        return self.invoke_async(command, callback=callback)

# ################################################################################################################################

    def run_enmasse_async(self, file_path:'str | Path') -> 'CommandResult':
        command = f'enmasse --import --replace --input {file_path} {self.server.base_dir} --verbose'
        result = self.run_zato_cli_async(command, callback=self._on_enmasse_completed)
        return result

# ################################################################################################################################

    def _on_enmasse_completed(self, result:'CommandResult') -> 'None':

        logger.info('Enmasse stdout -> `%s`', result.stdout.strip())
        logger.info('Enmasse stderr -> `%s`', result.stderr.strip())

# ################################################################################################################################
# ################################################################################################################################
