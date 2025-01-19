import sys
sys.path.append("/CSProject/Bitcoin")
from Blockchain.Backend.core.EllepticCurve.EllepticCurve import Sha256Point
from Blockchain.Backend.util.util import hash160, hash256
from Blockchain.Backend.core.database.database import AccountDB
import secrets



class account:
    def createKeys(self):
        Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
        Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

        G = Sha256Point(Gx, Gy)
        self.privateKey = secrets.randbits(256)
        unCompressedPublicKey = G * self.privateKey
        Xpoint = unCompressedPublicKey.x
        Ypoint = unCompressedPublicKey.y

        if Ypoint.num % 2 == 0:
            compressKey = b'\x02' + Xpoint.num.to_bytes(32, byteorder='big')
        else:
            compressKey = b'\x03' + Xpoint.num.to_bytes(32, byteorder='big')
        
        hsh160 = hash160(compressKey)
        """Prefix for Mainnet"""
        main_prefix = b'\x00'

        newAddress = main_prefix + hsh160
        """Checksum"""
        checksum = hash256(newAddress)[:4]

        newAddress = newAddress + checksum
        BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

        count = 0
        for c in newAddress:
            if c == 0:
                count += 1
            else:
                break

        num = int.from_bytes(newAddress,'big')
        prefix = '1' * count
        result = ''

        while num > 0:
            num, mod = divmod(num, 58)
            result = BASE58_ALPHABET[mod] + result

        self.PublicAddress = prefix + result

        print(f"Private Key {self.privateKey}")
        print(f"Public Key {self.PublicAddress}")

if __name__ == "__main__":
    acct = account()
    acct.createKeys()
    AccountDB().write([acct.__dict__])