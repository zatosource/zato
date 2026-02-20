from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from zato.server.service import Integer, Service


class Encrypt(Service):
    def handle(self: Any) -> None: ...

class Decrypt(Service):
    def handle(self: Any) -> None: ...

class HashSecret(Service):
    ...

class VerifyHash(Service):
    ...

class GenerateSecret(Service):
    ...

class GeneratePassword(Service):
    ...
