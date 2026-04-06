# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import subprocess
from pathlib import Path
from unittest import TestCase

# Test helpers
from conftest import (
    ini_path_from_test_file,
    start_server,
)

# ################################################################################################################################
# ################################################################################################################################

_dotnet_dir = Path(__file__).resolve().parent.parent.parent.parent / 'dotnet'
_exe = _dotnet_dir / 'bin' / 'publish' / 'zato-hl7-interop'

# ################################################################################################################################
# ################################################################################################################################

class DotNetInteropTestCase(TestCase):
    """ Test 16.2 - send 30 HL7 messages from a .NET nHapi client over MLLP
    and verify they are all received and acknowledged.
    """

    @classmethod
    def setUpClass(cls) -> 'None':

        if not _exe.exists():
            raise FileNotFoundError(
                f'.NET executable not found at {_exe}. '
                f'Run "make install" in {_dotnet_dir} first.'
            )

        cls.received_payloads:'list' = []
        cls.received_contexts:'list' = []

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.received_payloads.append(data)
            if zato_ctx:
                cls.received_contexts.append(zato_ctx)
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_dotnet_nhapi_sends_30_messages(self) -> 'None':

        result = subprocess.run(
            [str(_exe), self.host, str(self.port)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Parse JSON output lines ..
        lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
        self.assertTrue(len(lines) > 0, f'No output from .NET runner. stderr: {result.stderr}')

        results = [json.loads(line) for line in lines]
        self.assertEqual(len(results), 30, f'Expected 30 results, got {len(results)}')

        # .. verify each message got an AA ACK ..
        for entry in results:
            self.assertTrue(
                entry['ok'],
                f'{entry["msg_type"]} (control_id={entry["control_id"]}) failed: '
                f'ack_code={entry["ack_code"]}, error={entry.get("error", "")}'
            )

        # .. verify the server callback was invoked 30 times ..
        self.assertEqual(len(self.received_payloads), 30,
            f'Expected 30 callback invocations, got {len(self.received_payloads)}')

        # .. verify each received payload starts with MSH ..
        for idx, payload in enumerate(self.received_payloads):
            self.assertTrue(payload.startswith(b'MSH'),
                f'Payload {idx} does not start with MSH: {payload[:50]}')

# ################################################################################################################################
# ################################################################################################################################
