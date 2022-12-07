import sys
import pgpy
from pgpy.constants import PubKeyAlgorithm, KeyFlags, HashAlgorithm, SymmetricKeyAlgorithm, CompressionAlgorithm


def generate_new_key(name, email, comment):
    key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 4096)
    uid = pgpy.PGPUID.new(name, email=email, comment=comment)
    key.add_uid(uid, usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage},
                hashes=[HashAlgorithm.SHA256, HashAlgorithm.SHA384, HashAlgorithm.SHA512, HashAlgorithm.SHA224],
                ciphers=[SymmetricKeyAlgorithm.AES256, SymmetricKeyAlgorithm.AES192, SymmetricKeyAlgorithm.AES128],
                compression=[CompressionAlgorithm.ZLIB, CompressionAlgorithm.BZ2, CompressionAlgorithm.ZIP,
                             CompressionAlgorithm.Uncompressed])
    return str(key), str(key.pubkey)  # returns ASCII armored private key, ASCII armored public key


def load_key(private_key):
    key, _ = pgpy.PGPKey.from_blob(private_key)
    return key


def sign(message, pgp_key):
    pgp_message = pgpy.PGPMessage.new(message=message, cleartext=True, encoding='UTF-8')
    signature = pgp_key.sign(pgp_message)
    return signature, pgp_message


if __name__ == '__main__':
    if len(sys.argv) >= 4:
        private, public = generate_new_key(sys.argv[1], sys.argv[2], sys.argv[3])
        print('Private key:')
        print(private)
        print()
        print('Public key:')
        print(public)
    else:
        print('Usage: python3 crypto_ecdsa.py <name> <email> <comment>')
