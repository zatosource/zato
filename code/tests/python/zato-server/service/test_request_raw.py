# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock

# Zato
from zato.common.typing_ import any_, cast_
from zato.server.service.reqresp import Request

# ################################################################################################################################
# ################################################################################################################################

any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class TestRequestRaw(unittest.TestCase):
    """ The raw attribute is canonical and raw_request and text are its aliases.
    """

    def _make_request(self) -> 'Request':
        service = MagicMock()
        out = Request(service)
        return out

# ################################################################################################################################

    def test_raw_starts_empty(self) -> 'None':
        request = self._make_request()

        self.assertEqual(request.raw, '')

# ################################################################################################################################

    def test_raw_reads_back_through_all_names(self) -> 'None':
        request = self._make_request()
        request.raw = '{"customer":"C-1001"}'

        self.assertEqual(request.raw, '{"customer":"C-1001"}')
        self.assertEqual(request.raw_request, '{"customer":"C-1001"}')
        self.assertEqual(request.text, '{"customer":"C-1001"}')

# ################################################################################################################################

    def test_raw_request_writes_through_to_raw(self) -> 'None':
        request = self._make_request()
        request.raw_request = 'MSH|^~\\&|SENDING_APP|SENDING_FACILITY'

        self.assertEqual(request.raw, 'MSH|^~\\&|SENDING_APP|SENDING_FACILITY')
        self.assertEqual(request.text, 'MSH|^~\\&|SENDING_APP|SENDING_FACILITY')

# ################################################################################################################################

    def test_text_writes_through_to_raw(self) -> 'None':
        request = self._make_request()
        request.text = 'UNB+UNOC:3+SENDER+RECIPIENT+260721:0130+REF-0001'

        self.assertEqual(request.raw, 'UNB+UNOC:3+SENDER+RECIPIENT+260721:0130+REF-0001')
        self.assertEqual(request.raw_request, 'UNB+UNOC:3+SENDER+RECIPIENT+260721:0130+REF-0001')

# ################################################################################################################################

    def test_raw_holds_bytes_as_they_are(self) -> 'None':
        request = self._make_request()
        request.raw = b'\x89PNG\r\n'

        self.assertEqual(request.raw, b'\x89PNG\r\n')
        self.assertEqual(request.raw_request, b'\x89PNG\r\n')

# ################################################################################################################################

    def test_to_bunch_reads_a_dict_from_raw(self) -> 'None':
        request = self._make_request()
        request.raw = {'customer': 'C-1001'}

        bunched = cast_('any_', request.to_bunch())
        self.assertEqual(bunched.customer, 'C-1001')

# ################################################################################################################################

    def test_to_bunch_parses_json_from_raw(self) -> 'None':
        request = self._make_request()
        request.raw = '{"customer":"C-1001"}'

        bunched = cast_('any_', request.to_bunch())
        self.assertEqual(bunched.customer, 'C-1001')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
