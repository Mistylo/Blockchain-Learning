import sys
from Blockchain.Backend.util.util import hash256, littleEndianToInt, intToLittleEndian

class BlockHeader:
    def __init__(self, version, prev_block_hash, merkle_root, timestamp, bits):
        self.version = version
        self.prev_block_hash = prev_block_hash
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = 0
        self.blockHash = ''

    def mine(self, target):
        self.blockHash = target + 1

        while self.blockHash > target:
                self.blockHash = littleEndianToInt(
                    hash256(
                        intToLittleEndian(self.version, 4)
                        + bytes.fromhex(self.prev_block_hash)[::-1]
                        + bytes.fromhex(self.merkle_root)
                        + intToLittleEndian(self.timestamp, 4)
                        + self.bits
                        + intToLittleEndian(self.nonce, 4)
                    )
                )
                self.nonce += 1
                print(f"Mining Started {self.nonce}", end='\r')

        self.blockHash = intToLittleEndian(self.blockHash, 32).hex()[::-1]
        self.bits = self.bits.hex()