# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

class CCSIDConfig:
    """ This is a mapping of CCSID to character encodings used by Python, e.g. CCSID 1208 -> utf-8 in Python.
    In runtime, if a given CCSID cannot be looked up, Zato will assume 1208 = UTF-8.
    Details: https://en.wikipedia.org/wiki/CCSID
    """

    default_ccsid = 1208
    default_encoding = 'utf8'

    encoding_map = {
        273: 'cp273',
        367: 'ascii',
        424: 'cp424',
        437: 'cp437',
        500: 'cp500',
        737: 'cp737',
        775: 'cp775',
        813: 'iso8859_7',
        819: 'iso8859_1',
        850: 'cp850',
        852: 'cp852',
        855: 'cp855',
        857: 'cp857',
        860: 'cp860',
        861: 'cp861',
        862: 'cp862',
        863: 'cp863',
        864: 'cp864',
        865: 'cp865',
        866: 'cp866',
        869: 'cp869',
        874: 'cp874',
        875: 'cp875',
        912: 'iso8859_2',
        914: 'iso8859_4',
        915: 'iso8859_5',
        916: 'iso8859_8',
        920: 'iso8859_9',
        923: 'iso8859_15',
        932: 'sjis',
        936: 'ms936',
        943: 'ms932',
        944: 'cp949',
        949: 'ksc5601',
        950: 'big5',
        970:  'euc_kr',
        1006: 'cp1006',
        1026: 'cp1026',
        1089: 'iso8859_6',
        1140: 'cp1140',
        1208: 'utf8',
        1250: 'cp1250',
        1251: 'cp1251',
        1252: 'cp1252',
        1253: 'cp1253',
        1254: 'cp1254',
        1255: 'cp1255',
        1256: 'cp1256',
        1257: 'cp1257',
        1381: 'gb2312',
        1383: 'euc_cn',
        1386: 'gbk',
        1392: 'gb18030',
        5050: 'euc_jp',
        5054: 'iso2022jp',
        25546: 'iso2022kr',
    }
