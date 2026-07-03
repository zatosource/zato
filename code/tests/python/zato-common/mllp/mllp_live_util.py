# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
import subprocess
import sys
import time
from pathlib import Path

# colorama
from colorama import Fore, Style, init as colorama_init

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

colorama_init(autoreset=True)

# ################################################################################################################################
# ################################################################################################################################

# Standard MLLP framing bytes
start_sequence = b'\x0b'
end_sequence   = b'\x1c\x0d'

# Path to the test server script
_test_server_script = str(Path(__file__).parent / 'mllp_test_server.py')

# How long to wait for the server to print READY
_server_startup_timeout_seconds = 10

# How long to wait for the server process to terminate after SIGTERM
_server_shutdown_timeout_seconds = 5

# ################################################################################################################################
# ################################################################################################################################
# Server process helpers
# ################################################################################################################################
# ################################################################################################################################

def start_server(**overrides:'object') -> 'tuple[subprocess.Popen, int]':
    """ Starts the MLLP test server as a subprocess and waits for the READY signal.
    Returns (process, port).
    """

    command = [sys.executable, _test_server_script, '--port', '0']

    for key, value in overrides.items():

        # Convert a Python snake_case kwarg to a CLI --kebab-case argument ..
        key_dashed = key.replace('_', '-')
        cli_key = '--' + key_dashed

        # .. boolean toggles use the --no- prefix for False ..
        if isinstance(value, bool):
            if not value:
                cli_key = '--no-' + key_dashed
            command.append(cli_key)

        # .. while everything else is passed as a value following its key.
        else:
            value_text = str(value)
            command.append(cli_key)
            command.append(value_text)

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Read stdout until we see the READY line
    deadline = time.monotonic() + _server_startup_timeout_seconds
    port = 0
    stdout = cast_('any_', process.stdout)

    for line in stdout:

        stripped_line = line.strip()
        match = re.match(r'^READY:(\d+)$', stripped_line)

        if match:
            port_text = match.group(1)
            port = int(port_text)
            break

        if time.monotonic() > deadline:
            process.kill()
            raise Exception(f'MLLP test server did not print READY within {_server_startup_timeout_seconds}s')

    if port == 0:
        process.kill()
        raise Exception('MLLP test server exited before printing READY')

    return process, port

# ################################################################################################################################

def stop_server(process:'subprocess.Popen') -> 'None':
    """ Sends SIGTERM to the server process and waits for it to exit.
    Sends SIGKILL if it does not exit in time.
    """
    process.terminate()

    try:
        _ = process.wait(timeout=_server_shutdown_timeout_seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        _ = process.wait()

# ################################################################################################################################
# ################################################################################################################################
# Sample HL7 messages
# ################################################################################################################################
# ################################################################################################################################

def sample_adt_a01(control_id:'str'='CTRL001') -> 'bytes':
    """ Returns a well-formed ADT^A01 message as bytes.
    """
    message = (
        f'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|{control_id}|P|2.5\r'
        'EVN|A01|20230101120000\r'
        'PID|||12345^^^MRN||Doe^John||19800101|M\r'
        'PV1||I|ICU^Room1'
    )

    out = message.encode('utf-8')
    return out

# ################################################################################################################################

def sample_oru_r01(control_id:'str'='CTRL002') -> 'bytes':
    """ Returns a well-formed ORU^R01 message as bytes.
    """
    message = (
        f'MSH|^~\\&|LabSys|LabFac|OrderSys|OrderFac|20230101130000||ORU^R01|{control_id}|P|2.5\r'
        'PID|||67890^^^MRN||Smith^Jane||19900515|F\r'
        'OBR|1||LAB001|CBC^Complete Blood Count\r'
        'OBX|1|NM|WBC^White Blood Count||7.5|10*3/uL|4.5-11.0|N|||F'
    )

    out = message.encode('utf-8')
    return out

# ################################################################################################################################

def sample_wellness_oru() -> 'bytes':
    """ Returns a wellness ORU^R01 message with body temperature as bytes.
    """
    message = (
        'MSH|^~\\&|VitalMon|ICU|EHR|Hospital|20260525100000||ORU^R01^ORU_R01|WLN001|P|2.9\r'
        'PID|1||PAT001^^^Hosp^MR||Garcia^Maria||19750812|F\r'
        'OBR|1||VIT001|VS^Vital Signs\r'
        'OBX|1|NM|8310-5^Body temperature^LN||36.8|Cel|36.1-37.2|N|||F'
    )

    out = message.encode('utf-8')
    return out

# ################################################################################################################################
# ################################################################################################################################
# Performance logging helper
# ################################################################################################################################
# ################################################################################################################################

# How wide the dot-padded label column is
_perf_label_width = 40

# The minimum number of dots between a label and its value
_perf_min_dots = 3

# ################################################################################################################################

def perf_log(label:'str', value:'float', unit:'str', threshold:'float'=0.0) -> 'None':
    """ Prints a colorama-formatted performance result line.

    Format: [PERF] Label ............. Value unit [PASS/FAIL]
    """

    # Build the dot-padded label ..
    dots_needed = _perf_label_width - len(label)

    if dots_needed < _perf_min_dots:
        dots_needed = _perf_min_dots

    dots = '.' * dots_needed

    prefix = f'{Fore.CYAN}{Style.BRIGHT}[PERF]{Style.RESET_ALL}'
    padded_label = f' {label} {Fore.WHITE}{Style.DIM}{dots}{Style.RESET_ALL} '

    # .. color the value red or green depending on the threshold ..
    if threshold > 0.0:

        if value < threshold:
            colored_value = f'{Fore.RED}{Style.BRIGHT}{value:,.1f}{Style.RESET_ALL}'
            suffix = f' {Fore.RED}{Style.BRIGHT}[FAIL]{Style.RESET_ALL}'
        else:
            colored_value = f'{Fore.GREEN}{Style.BRIGHT}{value:,.1f}{Style.RESET_ALL}'
            suffix = f' {Fore.GREEN}{Style.BRIGHT}[PASS]{Style.RESET_ALL}'

    # .. without a threshold, there is no pass or fail indicator ..
    else:
        colored_value = f'{Fore.GREEN}{Style.BRIGHT}{value:,.1f}{Style.RESET_ALL}'
        suffix = ''

    # .. and now we can print the whole line.
    unit_display = f' {Fore.WHITE}{unit}{Style.RESET_ALL}'
    print(f'{prefix}{padded_label}{colored_value}{unit_display}{suffix}')

# ################################################################################################################################
# ################################################################################################################################
