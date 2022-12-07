import time
import evm_sc_utils.signers
from Crypto.Hash import keccak
from eth_typing import Address
from eth_account import Account
import config


def generate_new_key():
    return Account.create()


def load_key(eip191_private_key):
    return Address(bytes.fromhex(eip191_private_key))


def process(data):
    # removing 0x
    data_hex = data[2:]

    # getting current timestamp
    timestamp = int(time.time())

    # creating a zero-padded 4-byte hex from timestamp
    timestamp_hex = '{0:0{1}x}'.format(timestamp, 4)

    # concatenating data hex and timestamp hex
    dt = data_hex + timestamp_hex

    # getting keccak256 hash of the concatenation result
    k = keccak.new(digest_bits=256)
    k.update(bytes.fromhex(dt))
    message = k.hexdigest()

    # calculation
    if len(message) % 2 == 1:
        message = '0' + message
    value_array = [int(message[i:i+2], 16) for i in range(0, len(message), 2)]
    abi_array = ['int8' for i in range(0, len(message), 2)]

    # signing the hash using an EIP191-compatible signer
    signer = evm_sc_utils.signers.EIP191Signer(load_key(config.api_eip191_private_key))
    signature = signer.sign(abi_array, value_array)

    # creating the proof by concatenating 'data', 'timestamp', and 'signature'
    proof = '0x' + data_hex + timestamp_hex + signature.signature.hex()[2:]
    return proof, timestamp


if __name__ == '__main__':
    new_account = generate_new_key()
    print('Private key:')
    print(new_account.key.hex())
    print()
    print('Public key:')
    print(new_account.address)


