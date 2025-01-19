from Blockchain.Backend.core.script import script
from Blockchain.Backend.util.util import intToLittleEndian, bytesNeeded, decodeBase58, littleEndianToInt, encode_varint, hash256

ZERO_HASH = b'\0'*32
REWARD = 50 # Reward for mining a block, 50 BTC

PRIVATE_KEY = '23552092742495087308438200554028942420451413990235758340030176324413303050216'
MINER_ADDRESS = '1DGDeF1chZyhr14yPGUjjdedyJDnsQVKn'
SIGHASH_ALL = 1

# BlackHeight -> Big Endian and Little Endian
class CoinbaseTx:
    def __init__(self, BlockHeight):
        self.BlockHeightInLittleEndian = intToLittleEndian(BlockHeight, bytesNeeded(BlockHeight))
    
    def CoinbaseTransaction(self):
        prev_tx = ZERO_HASH
        prev_index = 0xffffffff

        tx_ins = []
        tx_ins.append(TxIn(prev_tx, prev_index))
        tx_ins[0].script_sig.cmds.append(self.BlockHeightInLittleEndian)

        tx_outs = []
        target_amout = REWARD * 100000000 # Satoshi
        target_h160 = decodeBase58(MINER_ADDRESS)
        target_script = script.p2pkh_script(target_h160)
        tx_outs.append(TxOut(amount = target_amout, script_pubkey= target_script))
        coinbaseTx = Tx(1, tx_ins, tx_outs, 0)
        coinbaseTx.TxId = coinbaseTx.id()

        return coinbaseTx

class Tx:
    def __init__(self, version, tx_ins, tx_outs, locktime):
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime

    def id(self):
        """Human Readable Tx id"""
        return self.hash().hex()

    def hash(self):
        """Binary Hash of serialization"""
        return hash256(self.serialize())[::-1]

    def serialize(self):
        result = intToLittleEndian(self.version, 4)
        result += encode_varint(len(self.tx_ins))

        for tx_in in self.tx_ins:
            result += tx_in.serialize()

        result += encode_varint(len(self.tx_outs))

        for tx_out in self.tx_outs:
            result += tx_out.serialize()
        
        result += intToLittleEndian(self.locktime, 4)
        return result 
    
    def sig_hash(self, input_index, script_pubkey):
        s = intToLittleEndian(self.version, 4)
        s += encode_varint(len(self.tx_ins))

        for i, tx_in in enumerate(self.tx_ins):
            if i == input_index:
                s += TxIn(tx_in.prev_tx, tx_in.prev_index, script_pubkey).serialize()
            else:
                s += TxIn(tx_in.prev_tx, tx_in.prev_index).serialize()

        s += encode_varint(len(self.tx_outs))
        for tx_out in self.tx_outs:
            s += tx_out.serialize()

        s += intToLittleEndian(self.locktime, 4)
        s += intToLittleEndian(SIGHASH_ALL, 4)

        h256 = hash256(s)
        return int.from_bytes(h256, byteorder='big')
    
    
    def sign_input(self, input_index, private_key, script_pubkey):
        z = self.sig_hash(input_index, script_pubkey)
        der = private_key.sign(z).der()
        sig = der + SIGHASH_ALL.to_bytes(1, byteorder='big')
        sec = private_key.point.sec()
        self.tx_ins[input_index].script_sig = script([sig, sec])

    def verify_input(self, input_index, script_pubkey):
        tx_in = self.tx_ins[input_index]
        z = self.sig_hash(input_index, script_pubkey)
        combined = tx_in.script_sig + script_pubkey
        return combined.evaluate(z)
        

    def is_coinbase(self):
        """
        # Check that there is exactly 1 input
        # Grab the first input and check if the prev_tx is b'\x00' * 32
        # Check that if the frist input prev_index is 0xffffffff
        """

        if len(self.tx_ins) != 1:
            return False
        
        first_input = self.tx_ins[0]

        if first_input.prev_tx != b'\x00' * 32:
            return False
        
        if first_input.prev_index != 0xffffffff:
            return False
        
        return True

    def toDict(self):
        """Convert All Transaction
            # Convert prev_tx Hash in hex from bytes
            # Convert Blockheight in hex which is stored in Script signature
        """

        for tx_index, tx_in in enumerate(self.tx_ins):
            if self.is_coinbase():
                tx_in.script_sig.cmds[0] = littleEndianToInt(tx_in.script_sig.cmds[0])

            tx_in.prev_tx = tx_in.prev_tx.hex()

            for index, cmd in enumerate(tx_in.script_sig.cmds):
                if isinstance(cmd, bytes):
                    tx_in.script_sig.cmds[index] = cmd.hex()
            tx_in.script_sig = tx_in.script_sig.__dict__
            self.tx_ins[tx_index] = tx_in.__dict__

        """Convert Transaction Output to dict
        # If there are Numbers we don't need to do anything
        # If values is in bytes, conver it to hex
        # Loop Through all the TxOut Objects and convert them into dict
        """

        for index, tx_out in enumerate(self.tx_outs):
            tx_out.script_pubkey.cmds[2] = tx_out.script_pubkey.cmds[2].hex()
            tx_out.script_pubkey = tx_out.script_pubkey.__dict__
            self.tx_outs[index] = tx_out.__dict__

        return self.__dict__


class TxIn:
    def __init__(self, prev_tx, prev_index, script_sig = None, sequence = 0xffffffff):
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        
        if script_sig is None:
            self.script_sig = script()
        else:
            self.script_sig = script_sig

        self.sequence = sequence

    def serialize(self): # Convert everything into byte format
        result = self.prev_tx[::-1]
        result += intToLittleEndian(self.prev_index, 4)
        result += self.script_sig.serialize()
        result += intToLittleEndian(self.sequence, 4)
        return result

class TxOut:
    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey # Who we are sending the money to

    def serialize(self):
        result = intToLittleEndian(self.amount, 8)
        result += self.script_pubkey.serialize()
        return result