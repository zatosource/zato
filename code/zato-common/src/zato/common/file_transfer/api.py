# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class VerifyHow:
    """ The ways a connection checks a stored file.
    """
    Size      = 'size'
    Read_Back = 'read-back'

Verify_How_List    = (VerifyHow.Size, VerifyHow.Read_Back)
Default_Verify_How = VerifyHow.Size

Verify_How_Human = {
    VerifyHow.Size:      'Size',
    VerifyHow.Read_Back: 'Read back',
}

# ################################################################################################################################
# ################################################################################################################################

# The retry settings of a schedule, zero attempts means no limit.
Default_Max_Attempts         = 5
Default_Retry_Backoff        = 60
Retry_Backoff_Max            = 3600
Default_Quarantine_Directory = 'quarantine'

# The daily expectation of a schedule, zero files means no expectation, the days are ISO weekday numbers.
Default_Expected_Files = 0
Default_Expected_By    = ''
Default_Expected_Days  = '1,2,3,4,5'

# ################################################################################################################################
# ################################################################################################################################

class Encoding:
    """ The encodings the text of a file received by a schedule can be read in, as Python codec names.
    """
    UTF_8       = 'utf-8'
    UTF_16_LE   = 'utf-16-le'
    UTF_16_BE   = 'utf-16-be'
    CP1252      = 'cp1252'
    ISO_8859_1  = 'iso-8859-1'
    ISO_8859_15 = 'iso-8859-15'
    CP1250      = 'cp1250'
    ISO_8859_2  = 'iso-8859-2'
    CP1257      = 'cp1257'
    CP1254      = 'cp1254'
    CP1253      = 'cp1253'
    ISO_8859_7  = 'iso-8859-7'
    CP1255      = 'cp1255'
    ISO_8859_8  = 'iso-8859-8'
    CP850       = 'cp850'
    CP852       = 'cp852'
    CP037       = 'cp037'
    CP500       = 'cp500'
    CP1140      = 'cp1140'

# How each encoding is named in Dashboard, in the order Dashboard offers them.
Encoding_Human = {
    Encoding.UTF_8:       'UTF-8',
    Encoding.UTF_16_BE:   'UTF-16 Big Endian',
    Encoding.UTF_16_LE:   'UTF-16 Little Endian',
    Encoding.ISO_8859_1:  'ISO-8859-1',
    Encoding.ISO_8859_2:  'ISO-8859-2',
    Encoding.ISO_8859_7:  'ISO-8859-7',
    Encoding.ISO_8859_8:  'ISO-8859-8',
    Encoding.ISO_8859_15: 'ISO-8859-15',
    Encoding.CP1250:      'Windows-1250',
    Encoding.CP1252:      'Windows-1252',
    Encoding.CP1253:      'Windows-1253',
    Encoding.CP1254:      'Windows-1254',
    Encoding.CP1255:      'Windows-1255',
    Encoding.CP1257:      'Windows-1257',
    Encoding.CP850:       'DOS 850',
    Encoding.CP852:       'DOS 852',
    Encoding.CP037:       'EBCDIC 037',
    Encoding.CP500:       'EBCDIC 500',
    Encoding.CP1140:      'EBCDIC 1140',
}

Encoding_List    = tuple(Encoding_Human)
Default_Encoding = Encoding.UTF_8

# The EBCDIC encodings, in which a line ends with the next line character, decoded as U+0085, or with a line feed.
Encoding_Next_Line = (Encoding.CP037, Encoding.CP500, Encoding.CP1140)

# ################################################################################################################################
# ################################################################################################################################
