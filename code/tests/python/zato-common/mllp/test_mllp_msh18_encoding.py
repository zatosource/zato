# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.hl7.mllp.preprocess import decode_with_msh18, preprocess_message
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# An MSH segment whose eighteenth field is the one that follows, seventeen fields before it
_msh_up_to_18 = 'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|CTRL_ENC|P|2.5||||||'

# An MSH segment of twelve fields, with no MSH-18 at all
_msh_short = 'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|CTRL_ENC|P|2.5'

# What MSH-18 says for Latin-1, and the name that only Latin-1 decodes
_latin1_msh18  = '8859/1'
_latin1_name   = b'M\xfcller'
_decoded_name  = 'Müller'

_default_encoding = 'utf-8'

# ################################################################################################################################
# ################################################################################################################################

class TestMSH18Encoding(TestCase):
    """ The encoding a frame is decoded with is MSH-18's when the channel reads it and the field names
    one, and the channel's own otherwise - whichever line endings the sender used.
    """

    def _frame(self, msh_line:'str', separator:'str') -> 'bytes':
        """ One admission in Latin-1, its segments ended the given way.
        """
        out = (msh_line + separator + 'PID|||12345^^^MRN||').encode('ascii') + _latin1_name
        return out

# ################################################################################################################################

    def test_msh18_is_read_with_cr_endings(self) -> 'None':
        """ The ordinary frame, ended the way HL7 says.
        """
        raw_bytes = self._frame(_msh_up_to_18 + _latin1_msh18, '\r')
        decoded = decode_with_msh18(raw_bytes, _default_encoding)

        self.assertTrue(decoded.endswith(_decoded_name))

# ################################################################################################################################

    def test_msh18_is_read_with_lf_endings(self) -> 'None':
        """ A frame with LF endings is expected input, the channel normalizing them, so an MSH-18 that
        ends its line is read all the same rather than being glued to the next segment's name.
        """
        raw_bytes = self._frame(_msh_up_to_18 + _latin1_msh18, '\n')
        decoded = decode_with_msh18(raw_bytes, _default_encoding)

        self.assertTrue(decoded.endswith(_decoded_name))

# ################################################################################################################################

    def test_msh18_is_read_with_crlf_endings(self) -> 'None':
        """ And so is one with CRLF endings.
        """
        raw_bytes = self._frame(_msh_up_to_18 + _latin1_msh18, '\r\n')
        decoded = decode_with_msh18(raw_bytes, _default_encoding)

        self.assertTrue(decoded.endswith(_decoded_name))

# ################################################################################################################################

    def test_a_later_segment_is_never_read_as_msh18(self) -> 'None':
        """ A short MSH segment has no MSH-18, so the default applies, whatever a later segment happens
        to say in the position MSH-18 would have had if the frame were one long line.
        """
        later_segment = 'PID|||1|||' + _latin1_msh18 + '|'
        raw_bytes = (_msh_short + '\n' + later_segment).encode('ascii') + _latin1_name

        decoded = decode_with_msh18(raw_bytes, _default_encoding)

        # .. decoded as UTF-8, the Latin-1 byte is a replacement character and not the name
        self.assertFalse(decoded.endswith(_decoded_name))

# ################################################################################################################################

    def test_an_empty_msh18_is_the_default(self) -> 'None':
        """ D:49 - if MSH-18 is empty, the Encoding setting is used instead.
        """
        raw_bytes = self._frame(_msh_up_to_18, '\r')
        decoded = decode_with_msh18(raw_bytes, 'iso-8859-1')

        self.assertTrue(decoded.endswith(_decoded_name))

# ################################################################################################################################

    def test_an_unknown_msh18_is_the_default(self) -> 'None':
        """ A value the map does not know is read as the channel's own.
        """
        raw_bytes = self._frame(_msh_up_to_18 + 'KLINGON', '\r')
        decoded = decode_with_msh18(raw_bytes, 'iso-8859-1')

        self.assertTrue(decoded.endswith(_decoded_name))

# ################################################################################################################################

    def test_the_toggle_off_ignores_msh18(self) -> 'None':
        """ D:49 - when off, the Encoding setting is used, whatever MSH-18 says.
        """
        raw_bytes = self._frame(_msh_up_to_18 + _latin1_msh18, '\r')

        messages = cast_('strlist', preprocess_message(raw_bytes, should_use_msh18_encoding=False,
            default_character_encoding=_default_encoding))

        self.assertFalse(messages[0].endswith(_decoded_name))

# ################################################################################################################################

    def test_the_toggle_on_reads_msh18(self) -> 'None':
        """ D:48 - when on, the encoding is read from MSH-18 of the message.
        """
        raw_bytes = self._frame(_msh_up_to_18 + _latin1_msh18, '\n')

        messages = cast_('strlist', preprocess_message(raw_bytes, should_use_msh18_encoding=True,
            default_character_encoding=_default_encoding))

        self.assertTrue(messages[0].endswith(_decoded_name))

# ################################################################################################################################
# ################################################################################################################################
