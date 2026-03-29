# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
# Zato
from zato.common.file_transfer.const import KeyType, KeyUsage
from zato.common.file_transfer.model import KeyPairResult, PGPKey, VerifyResult

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class PGPManager:

    def __init__(self) -> 'None':
        self._pgpy = None
        self._gnupg = None
        self._init_backend()

    def _init_backend(self) -> 'None':
        try:
            import pgpy
            self._pgpy = pgpy
        except ImportError:
            pass

        if not self._pgpy:
            try:
                import gnupg
                self._gnupg = gnupg
            except ImportError:
                pass

# ################################################################################################################################

    def import_key(self, armored_key:'str') -> 'PGPKey':

        if self._pgpy:
            return self._import_key_pgpy(armored_key)
        elif self._gnupg:
            return self._import_key_gnupg(armored_key)
        else:
            raise ImportError('No PGP library available (install pgpy or python-gnupg)')

    def _import_key_pgpy(self, armored_key:'str') -> 'PGPKey':

        key, _ = self._pgpy.PGPKey.from_blob(armored_key)

        is_public = not key.is_protected and not hasattr(key, '_key') or not key.is_unlocked

        if '-----BEGIN PGP PUBLIC KEY BLOCK-----' in armored_key:
            key_type = KeyType.Public
        elif '-----BEGIN PGP PRIVATE KEY BLOCK-----' in armored_key:
            key_type = KeyType.Private
        else:
            key_type = KeyType.Public

        usage = []
        if key_type == KeyType.Public:
            usage = [KeyUsage.Encrypt, KeyUsage.Verify]
        else:
            usage = [KeyUsage.Decrypt, KeyUsage.Sign]

        fingerprint = str(key.fingerprint)
        algorithm = str(key.key_algorithm.name) if hasattr(key.key_algorithm, 'name') else str(key.key_algorithm)
        key_size = key.key_size if hasattr(key, 'key_size') else 0

        created_at = key.created.timestamp() if hasattr(key, 'created') and key.created else time.time()
        expires_at = None
        if hasattr(key, 'expires_at') and key.expires_at:
            expires_at = key.expires_at.timestamp()

        return PGPKey(
            id='',
            name='',
            key_type=key_type,
            usage=usage,
            key_data=armored_key,
            fingerprint=fingerprint,
            algorithm=algorithm,
            key_size=key_size,
            created_at=created_at,
            expires_at=expires_at,
            is_enabled=True,
        )

    def _import_key_gnupg(self, armored_key:'str') -> 'PGPKey':

        import tempfile
        gpg = self._gnupg.GPG(gnupghome=tempfile.mkdtemp())
        result = gpg.import_keys(armored_key)

        if not result.fingerprints:
            raise ValueError('Failed to import key')

        fingerprint = result.fingerprints[0]

        if '-----BEGIN PGP PUBLIC KEY BLOCK-----' in armored_key:
            key_type = KeyType.Public
            usage = [KeyUsage.Encrypt, KeyUsage.Verify]
        else:
            key_type = KeyType.Private
            usage = [KeyUsage.Decrypt, KeyUsage.Sign]

        return PGPKey(
            id='',
            name='',
            key_type=key_type,
            usage=usage,
            key_data=armored_key,
            fingerprint=fingerprint,
            algorithm='',
            key_size=0,
            created_at=time.time(),
            expires_at=None,
            is_enabled=True,
        )

# ################################################################################################################################

    def generate_keypair(
        self,
        name:'str',
        email:'str',
        algorithm:'str'='RSA',
        key_size:'int'=4096,
        passphrase:'str'='',
    ) -> 'KeyPairResult':

        if self._pgpy:
            return self._generate_keypair_pgpy(name, email, algorithm, key_size, passphrase)
        elif self._gnupg:
            return self._generate_keypair_gnupg(name, email, algorithm, key_size, passphrase)
        else:
            raise ImportError('No PGP library available (install pgpy or python-gnupg)')

    def _generate_keypair_pgpy(
        self,
        name:'str',
        email:'str',
        algorithm:'str',
        key_size:'int',
        passphrase:'str',
    ) -> 'KeyPairResult':

        from pgpy.constants import PubKeyAlgorithm, KeyFlags, HashAlgorithm, SymmetricKeyAlgorithm, CompressionAlgorithm

        if algorithm.upper() == 'RSA':
            algo = PubKeyAlgorithm.RSAEncryptOrSign
        elif algorithm.upper() == 'DSA':
            algo = PubKeyAlgorithm.DSA
        else:
            algo = PubKeyAlgorithm.RSAEncryptOrSign

        key = self._pgpy.PGPKey.new(algo, key_size)

        uid = self._pgpy.PGPUID.new(name, email=email)
        key.add_uid(uid, usage={
            KeyFlags.Sign,
            KeyFlags.EncryptCommunications,
            KeyFlags.EncryptStorage,
        }, hashes=[HashAlgorithm.SHA256, HashAlgorithm.SHA384, HashAlgorithm.SHA512],
           ciphers=[SymmetricKeyAlgorithm.AES256, SymmetricKeyAlgorithm.AES192, SymmetricKeyAlgorithm.AES128],
           compression=[CompressionAlgorithm.ZLIB, CompressionAlgorithm.BZ2, CompressionAlgorithm.ZIP])

        if passphrase:
            key.protect(passphrase, SymmetricKeyAlgorithm.AES256, HashAlgorithm.SHA256)

        private_armored = str(key)
        public_armored = str(key.pubkey)

        fingerprint = str(key.fingerprint)
        created_at = key.created.timestamp() if hasattr(key, 'created') and key.created else time.time()

        private_key = PGPKey(
            id='',
            name=name,
            key_type=KeyType.Private,
            usage=[KeyUsage.Decrypt, KeyUsage.Sign],
            key_data=private_armored,
            fingerprint=fingerprint,
            algorithm=algorithm,
            key_size=key_size,
            created_at=created_at,
            expires_at=None,
            is_enabled=True,
        )

        public_key = PGPKey(
            id='',
            name=name,
            key_type=KeyType.Public,
            usage=[KeyUsage.Encrypt, KeyUsage.Verify],
            key_data=public_armored,
            fingerprint=fingerprint,
            algorithm=algorithm,
            key_size=key_size,
            created_at=created_at,
            expires_at=None,
            is_enabled=True,
        )

        return KeyPairResult(public_key=public_key, private_key=private_key)

    def _generate_keypair_gnupg(
        self,
        name:'str',
        email:'str',
        algorithm:'str',
        key_size:'int',
        passphrase:'str',
    ) -> 'KeyPairResult':

        import tempfile
        gpg = self._gnupg.GPG(gnupghome=tempfile.mkdtemp())

        input_data = gpg.gen_key_input(
            key_type=algorithm.upper(),
            key_length=key_size,
            name_real=name,
            name_email=email,
            passphrase=passphrase,
        )

        key = gpg.gen_key(input_data)
        fingerprint = str(key)

        public_armored = gpg.export_keys(fingerprint)
        private_armored = gpg.export_keys(fingerprint, secret=True, passphrase=passphrase)

        private_key = PGPKey(
            id='',
            name=name,
            key_type=KeyType.Private,
            usage=[KeyUsage.Decrypt, KeyUsage.Sign],
            key_data=private_armored,
            fingerprint=fingerprint,
            algorithm=algorithm,
            key_size=key_size,
            created_at=time.time(),
            expires_at=None,
            is_enabled=True,
        )

        public_key = PGPKey(
            id='',
            name=name,
            key_type=KeyType.Public,
            usage=[KeyUsage.Encrypt, KeyUsage.Verify],
            key_data=public_armored,
            fingerprint=fingerprint,
            algorithm=algorithm,
            key_size=key_size,
            created_at=time.time(),
            expires_at=None,
            is_enabled=True,
        )

        return KeyPairResult(public_key=public_key, private_key=private_key)

# ################################################################################################################################

    def encrypt(self, content:'bytes', recipient_key_data:'str') -> 'bytes':

        if self._pgpy:
            return self._encrypt_pgpy(content, recipient_key_data)
        elif self._gnupg:
            return self._encrypt_gnupg(content, recipient_key_data)
        else:
            raise ImportError('No PGP library available')

    def _encrypt_pgpy(self, content:'bytes', recipient_key_data:'str') -> 'bytes':

        key, _ = self._pgpy.PGPKey.from_blob(recipient_key_data)
        message = self._pgpy.PGPMessage.new(content, file=True)
        encrypted = key.encrypt(message)
        return str(encrypted).encode('utf-8')

    def _encrypt_gnupg(self, content:'bytes', recipient_key_data:'str') -> 'bytes':

        import tempfile
        gpg = self._gnupg.GPG(gnupghome=tempfile.mkdtemp())
        result = gpg.import_keys(recipient_key_data)
        fingerprint = result.fingerprints[0]
        encrypted = gpg.encrypt(content, fingerprint, armor=True)
        return str(encrypted).encode('utf-8')

# ################################################################################################################################

    def decrypt(self, content:'bytes', private_key_data:'str', passphrase:'str'='') -> 'bytes':

        if self._pgpy:
            return self._decrypt_pgpy(content, private_key_data, passphrase)
        elif self._gnupg:
            return self._decrypt_gnupg(content, private_key_data, passphrase)
        else:
            raise ImportError('No PGP library available')

    def _decrypt_pgpy(self, content:'bytes', private_key_data:'str', passphrase:'str') -> 'bytes':

        key, _ = self._pgpy.PGPKey.from_blob(private_key_data)

        if passphrase:
            with key.unlock(passphrase):
                message = self._pgpy.PGPMessage.from_blob(content)
                decrypted = key.decrypt(message)
                return decrypted.message
        else:
            message = self._pgpy.PGPMessage.from_blob(content)
            decrypted = key.decrypt(message)
            return decrypted.message

    def _decrypt_gnupg(self, content:'bytes', private_key_data:'str', passphrase:'str') -> 'bytes':

        import tempfile
        gpg = self._gnupg.GPG(gnupghome=tempfile.mkdtemp())
        gpg.import_keys(private_key_data)
        decrypted = gpg.decrypt(content, passphrase=passphrase)
        return bytes(decrypted.data)

# ################################################################################################################################

    def sign(self, content:'bytes', private_key_data:'str', passphrase:'str'='') -> 'bytes':

        if self._pgpy:
            return self._sign_pgpy(content, private_key_data, passphrase)
        elif self._gnupg:
            return self._sign_gnupg(content, private_key_data, passphrase)
        else:
            raise ImportError('No PGP library available')

    def _sign_pgpy(self, content:'bytes', private_key_data:'str', passphrase:'str') -> 'bytes':

        key, _ = self._pgpy.PGPKey.from_blob(private_key_data)
        message = self._pgpy.PGPMessage.new(content, file=True)

        if passphrase:
            with key.unlock(passphrase):
                signed = key.sign(message)
        else:
            signed = key.sign(message)

        return str(signed).encode('utf-8')

    def _sign_gnupg(self, content:'bytes', private_key_data:'str', passphrase:'str') -> 'bytes':

        import tempfile
        gpg = self._gnupg.GPG(gnupghome=tempfile.mkdtemp())
        result = gpg.import_keys(private_key_data)
        fingerprint = result.fingerprints[0]
        signed = gpg.sign(content, keyid=fingerprint, passphrase=passphrase)
        return bytes(signed.data)

# ################################################################################################################################

    def verify(self, content:'bytes', public_key_data:'str') -> 'VerifyResult':

        if self._pgpy:
            return self._verify_pgpy(content, public_key_data)
        elif self._gnupg:
            return self._verify_gnupg(content, public_key_data)
        else:
            raise ImportError('No PGP library available')

    def _verify_pgpy(self, content:'bytes', public_key_data:'str') -> 'VerifyResult':

        try:
            key, _ = self._pgpy.PGPKey.from_blob(public_key_data)
            message = self._pgpy.PGPMessage.from_blob(content)

            verification = key.verify(message)

            for sig in verification:
                if sig:
                    signer = str(sig.signer) if hasattr(sig, 'signer') else ''
                    return VerifyResult(signer=signer)

            return VerifyResult(is_ok=False)
        except Exception:
            return VerifyResult(is_ok=False)

    def _verify_gnupg(self, content:'bytes', public_key_data:'str') -> 'VerifyResult':

        try:
            import tempfile
            gpg = self._gnupg.GPG(gnupghome=tempfile.mkdtemp())
            gpg.import_keys(public_key_data)
            verified = gpg.verify(content)

            if verified.valid:
                return VerifyResult(signer=verified.fingerprint or '')
            return VerifyResult(is_ok=False)
        except Exception:
            return VerifyResult(is_ok=False)

# ################################################################################################################################

    def get_fingerprint(self, key_data:'str') -> 'str':

        if self._pgpy:
            key, _ = self._pgpy.PGPKey.from_blob(key_data)
            return str(key.fingerprint)
        elif self._gnupg:
            import tempfile
            gpg = self._gnupg.GPG(gnupghome=tempfile.mkdtemp())
            result = gpg.import_keys(key_data)
            return result.fingerprints[0] if result.fingerprints else ''
        else:
            raise ImportError('No PGP library available')

# ################################################################################################################################

    def get_key_info(self, key_data:'str') -> 'Dict[str, any_]':

        if self._pgpy:
            key, _ = self._pgpy.PGPKey.from_blob(key_data)
            return {
                'fingerprint': str(key.fingerprint),
                'algorithm': str(key.key_algorithm.name) if hasattr(key.key_algorithm, 'name') else str(key.key_algorithm),
                'key_size': key.key_size if hasattr(key, 'key_size') else 0,
                'created': key.created.timestamp() if hasattr(key, 'created') and key.created else None,
                'expires': key.expires_at.timestamp() if hasattr(key, 'expires_at') and key.expires_at else None,
            }
        elif self._gnupg:
            import tempfile
            gpg = self._gnupg.GPG(gnupghome=tempfile.mkdtemp())
            result = gpg.import_keys(key_data)
            return {
                'fingerprint': result.fingerprints[0] if result.fingerprints else '',
                'algorithm': '',
                'key_size': 0,
                'created': None,
                'expires': None,
            }
        else:
            raise ImportError('No PGP library available')

# ################################################################################################################################
# ################################################################################################################################
