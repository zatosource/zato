# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from tempfile import NamedTemporaryFile
from unittest import TestCase
from uuid import uuid4

# Nose
from nose.tools import eq_

# Zato
from zato.common.crypto import CryptoManager

# ##############################################################################

# Test keys - note that the private one uses PKCS#8 not PKCS#1.

pub_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA5yVNaJJCukjfg7aEslhz
vxRP4rQ6Lt6s0tEdT/1sM2VREsJo2VZY66jrSHJWyTmIQmdYEbJk/gEnVhadQ/n6
YJwrjGY6M6VzTO4D6vLBugaQ60x6nDNAgA2cQ79HPACLLSeyamW1uunV0PqoGbBV
kUQ+G8Ob0IabN6eGcN6OBsc6BSja3VmM++tIn679yE9yUM7LTGr3y2yOUI3dBWz4
RZH3QJPTJcLBY+arh49RIVfLHvwjG+zlKNEXw8AhI9SlmOXP+O03CvwoQxU8zmpe
isKc5rGni2pgn6oaGaLMOlu+bHBT5aZOJt6q1GqHaKviwNb/nIw+GvPiYwSr95t8
bwIDAQAB
-----END PUBLIC KEY-----"""

# ##############################################################################

priv_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDnJU1okkK6SN+D
toSyWHO/FE/itDou3qzS0R1P/WwzZVESwmjZVljrqOtIclbJOYhCZ1gRsmT+ASdW
Fp1D+fpgnCuMZjozpXNM7gPq8sG6BpDrTHqcM0CADZxDv0c8AIstJ7JqZbW66dXQ
+qgZsFWRRD4bw5vQhps3p4Zw3o4GxzoFKNrdWYz760ifrv3IT3JQzstMavfLbI5Q
jd0FbPhFkfdAk9MlwsFj5quHj1EhV8se/CMb7OUo0RfDwCEj1KWY5c/47TcK/ChD
FTzOal6KwpzmsaeLamCfqhoZosw6W75scFPlpk4m3qrUaodoq+LA1v+cjD4a8+Jj
BKv3m3xvAgMBAAECggEAB2HEmBtbsDFVmhJBKKT0hVyztGzHEuofoNf21LAmPXn1
3eCBkrdUPap2YSjtpp2EwYIlaONGoGoPBIvSV/Jq0Z0LMv+syit1hDZxv5YjI7rD
9A/MNqLYY36LyAoaz0rBJx8Gbqly5VZEctkedzuPcAU66o4TstQprtxVydMBvCuf
G20TSE+GlD7fcS4AlEJ7+LebNbAU3aCZ9c0dqthhRmu2xxvIEzCrA5PVcTqw7krn
fqej8Hm3ArfL1YWyV56oaF0SmS4qotm88QHeR6VBgv0KP0AHnaPgRkJTQQvZZ1A0
PrCcgiVQNDCUz6MFiZGj1WVRKLvFS2TzwS2Ei80Y2QKBgQD/YC4f2p0ED6ZbcxJe
n57EhZeWQW2ZKSmELzx4S4bqSo9IAkWu98JVYnN6rP1V0IARN6VVLlTMjM9q37Wq
y6YusNBB8AELYOvEL3g4ImepBQR4xF5N9wfESr87Y9x+DruDeKevBAcLwRCEstHo
/ae7RI2A8h3StJxu7pboaxaLywKBgQDntfViaMS+R3WF0FV3IXdJOnMG5SjYXs+B
NpdMg1dsbhucrHC7unKjBCjSiw0CKtLcFTCR+xc93Jx0lo1aayPR54lEXy58gsGG
WvHeM/TeWEwd+6QXsY7GoqKFQRNt86efgY++mL7lQaCGuz24J1sRtaIafFP/Ig+i
psnGz/UFbQKBgD51qrJVyMN+hGSnj12fUrikKAAy/nhQbfwLhZGyf0v8cnDdRWfW
5yv1CWN+vfNoLHqJjqF31Hu3EOAF2Svt5TZUPotyBP9gdCmmppOsLohTVtWmyZ3u
BnNHCOCguwQF3Gz6bKDMrmB8luqtxdNjfsu5p5ZbIVownHYxWq17y6bjAoGADbfQ
F0tsmndQleOHq83nagZz2OyoRmcWkefRfU4pVtoN+HCdHAAl2VDdudlRo9c1NKJs
hbf/4EG3YY+oPropHLxAfDPGZMi4/GNV/nnE/YTsvLmxNVXlxgzK4mi/5bqPKfpZ
sEcKxjfkcRWUydpKofnG5xqFPo2dr1uAhqy5LOECgYEAsMpk9adcah/axZf30AR8
kDUp83UmxVI4nBPpsJGC92SDuOE7Pr4MzROhPIMum8aBpM6MwwsyQrPF1MxFvyIl
Ckuau69qTi/h6A/DoqpbZ9426khtB7A4zSPYqfhbj4C2LFhC385ZbOhA6Coa7u1s
HtO3lDnY8Qno29yTCP4+GWM=
-----END PRIVATE KEY-----"""

# ##############################################################################

# Plain text and its value after encrypting with the private key
plain_text = 'zato1'
secret = 'T8irIao63mrrSIItl1JDgs8K+9zIXi3OTXYzEHtSpzB9m52Q34LYeeiyYJTvEq8nWb3Lpuav29QuJAfgyPCUgf8RZAWNNkIgmfwsNPAcP4os62i13QGp2Vuxk22QZ7qOjZtMRXncQ8sDgL9JyEo+bphthw8TEdo08I1aGe0iSMg8QQhbwtEGVgdY0286cvSFLbadwNYQCSdadUMlCmtBft2vVUxM/cZGYc5VAgE4ey2KeFgGYVtg7GZjbiWT1JUPKsJESksrvKMmv5SZ9aVBa8Ex/ahIWy+IDPcNKe4MskZrGnqCxWF3+yQYa/1xv0hCw1N7LlW592xDzNWdTALE5A=='

# ##############################################################################

class CryptoTestCase(TestCase):
    
    def xtest_decrypt_priv_key_in_file(self):
        """ Decrypt a message using a private key from file.
        """
        with NamedTemporaryFile(prefix='zato-test-') as tf:
            tf.write(priv_key)
            tf.flush()
            
            cm = CryptoManager()
            cm.priv_key_location = tf.name
            cm.load_keys()
            
            eq_(plain_text, cm.decrypt(secret))

    def xtest_decrypt_priv_key_in_string(self):
        """ Decrypt a message using a private key from string.
        """
        cm = CryptoManager()
        cm.priv_key = priv_key
        cm.load_keys()
        
        eq_(plain_text, cm.decrypt(secret))
        
    def test_enrypt(self):
        """ Encrypt a message using the public key.
        """
        _plain_text = uuid4().hex
        
        with NamedTemporaryFile(prefix='zato-test-') as tf_priv:
            with NamedTemporaryFile(prefix='zato-test-') as tf_pub:
                
                tf_priv.write(priv_key)
                tf_priv.flush()
                
                tf_pub.write(pub_key)
                tf_pub.flush()
                
                cm_priv = CryptoManager()
                cm_priv.priv_key_location = tf_priv.name
                cm_priv.load_keys()
                
                cm_pub = CryptoManager()
                cm_pub.pub_key_location = tf_pub.name
                cm_pub.load_keys()
                
                encrypted = cm_pub.encrypt(_plain_text)
                decrypted = cm_priv.decrypt(encrypted)
                
                eq_(_plain_text, decrypted)
        
    def xtest_reset(self):
        """ Resets all keys to None.
        """
        cm = CryptoManager()
        cm.reset()
        
        eq_(cm.priv_key_location, None)
        eq_(cm.pub_key_location, None)
        eq_(cm.priv_key, None)
        eq_(cm.pub_key, None)
