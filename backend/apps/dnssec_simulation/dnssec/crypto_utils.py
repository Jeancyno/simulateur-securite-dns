import hashlib
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_der_public_key


class DNSSECCrypto:
    @staticmethod
    def sha256(data):
        return hashlib.sha256(data).digest()

    @staticmethod
    def sha384(data):
        return hashlib.sha384(data).digest()

    @staticmethod
    def sha1(data):
        return hashlib.sha1(data).digest()

    @staticmethod
    def hash_ds(dnskey_data, algorithm=2):
        if algorithm == 1:
            return hashlib.sha1(dnskey_data).digest()
        elif algorithm == 2:
            return hashlib.sha256(dnskey_data).digest()
        elif algorithm == 4:
            return hashlib.sha384(dnskey_data).digest()
        else:
            raise ValueError(f"Algorithme de hash non supporté: {algorithm}")

    @staticmethod
    def parse_dnskey(key_data):
        try:
            return load_pem_public_key(key_data.encode('utf-8'))
        except:
            try:
                return load_der_public_key(base64.b64decode(key_data))
            except:
                raise ValueError("Format de clé non reconnu")

    @staticmethod
    def verify_rrsig(rrset_data, signature_base64, public_key_pem, algorithm):
        try:
            signature = base64.b64decode(signature_base64)
            key = DNSSECCrypto.parse_dnskey(public_key_pem)

            if algorithm in [5, 7, 8]:
                from cryptography.hazmat.primitives.asymmetric import padding
                hash_alg = hashes.SHA256() if algorithm == 8 else hashes.SHA1()
                key.verify(
                    signature,
                    rrset_data,
                    padding.PKCS1v15(),
                    hash_alg
                )
                return True
            elif algorithm == 13:
                key.verify(signature, rrset_data, ec.ECDSA(hashes.SHA256()))
                return True
            elif algorithm == 14:
                key.verify(signature, rrset_data, ec.ECDSA(hashes.SHA384()))
                return True
            elif algorithm == 15:
                key.verify(signature, rrset_data)
                return True
            elif algorithm == 16:
                key.verify(signature, rrset_data)
                return True
            else:
                return False
        except Exception:
            return False