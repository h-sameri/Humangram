import ecdsa


def generate_new_key():
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    with open("private.pem", "wb") as f:
        f.write(sk.to_pem())
    with open("public.pem", "wb") as f:
        f.write(vk.to_pem())
    return str(sk.to_pem()), str(vk.to_pem())  # returns PEM private key, PEM public key


def load_key(sk):
    return ecdsa.SigningKey.from_pem(sk)


def sign(message, sk):
    sig = sk.sign(bytes(message, encoding='utf8'))
    return sig, message


if __name__ == '__main__':
    private, public = generate_new_key()
    print('Private key:')
    print(private)
    print()
    print('Public key:')
    print(public)
