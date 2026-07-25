# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The AS2 implementation - RFC 4130 with RFC 5402 compression, over the S/MIME primitives
of RFC 8551 and the CMS structures of RFC 5652.

Security posture
================

What is enforced

- A partnership's own signing and encryption settings are requirements on what arrives, not
  merely a description of what we send. A message reaching a partnership configured for signing
  or encryption without the matching layer is answered with insufficient-message-security and
  is never routed. The AS2-From and AS2-To pair travels in the clear in every message, so it
  identifies a partner rather than authenticating one, and the cryptographic layers are what
  the trust decision actually rests on.

- An inbound signing certificate has to satisfy both the rotation window an operator configured
  around it and its own notBefore and notAfter dates. The same holds for the certificates
  outgoing encryption targets and for our own decryption entries.

- Trust is pinned to the partner's configured certificate, or to a configured trust anchor the
  signer chains up to. A certificate carried inside a message is never trusted on its own.

- Every quantity on the path a message travels before it is known to come from the partner has
  a ceiling - the request body, the number of stacked security layers, the depth of BER nesting
  the definite-length re-encoding walks, and the output of decompression. Each one answers with
  a disposition modifier rather than with resource exhaustion.

What is deliberately not done

- Certificate revocation is not checked. There is no CRL fetching and no OCSP, neither for
  inbound signing certificates nor for the certificates outgoing encryption targets. Revocation
  in AS2 is handled between the two parties out of band, by removing the certificate from the
  partnership, which takes effect on the next message. An operator who learns that a partner's
  key is compromised removes the certificate from the partnership rather than relying on the
  partner's revocation infrastructure being reachable and current.

- RSA key transport uses PKCS #1 v1.5 rather than OAEP. RFC 8551 allows both and OAEP is the
  stronger construction, but the AS2 install base does not implement it - a message encrypted
  with OAEP is undecryptable by essentially every deployed counterparty. The exposure PKCS #1
  v1.5 carries is a Bleichenbacher-style adaptive chosen-ciphertext attack, and what closes it
  here is that a decryption failure is never distinguishable from the outside: every path
  through key recovery and content decryption reports the same decryption-failed modifier, with
  no detail from the failure reaching the wire. A timing difference between a key-transport
  failure and a content-padding failure remains.

- SHA-1 signatures and 3DES content encryption are supported because partners require them, and
  neither is a default. A partnership has to name them explicitly.
"""
