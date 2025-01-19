import sys
sys.path.append('/CSProject/Bitcoin')
from Blockchain.Backend.core.block import Block
from Blockchain.Backend.core.blockheader import BlockHeader
from Blockchain.Backend.util.util import hash256, merkle_root, target_to_bits
from Blockchain.Backend.core.database.database import BlockchainDB
from Blockchain.Backend.core.tx import CoinbaseTx
from multiprocessing import Process, Manager
from Blockchain.Frontend.run import main
import time



ZERO_HASH = "0" * 64
VERSION = 1
INITIAL_TARGET = 0x0000FFFF00000000000000000000000000000000000000000000000000000000

class Blockchain:
    def __init__(self, utxos, MemPool):
        self.utxos = utxos
        self.MemPool = MemPool
        self.current_target = INITIAL_TARGET
        self.bits = target_to_bits(INITIAL_TARGET)

    def write_on_dist(self,block):
        blockchainDB = BlockchainDB()
        blockchainDB.write(block)
    
    def fetch_last_block(self):
        blockchainDB = BlockchainDB()
        last_block = blockchainDB.lastBlock()
        if not last_block: 
            print("Blockchain is empty. Returning genesis block data.")
            return {"Height": 0, "BlockHeader": {"blockHash": ZERO_HASH}}
        return last_block
    
    def GenesisBlock(self):
        BlockHeight = 0
        prev_block_hash = ZERO_HASH
        self.addBlock(BlockHeight, prev_block_hash)


    """Keep track of all the unspent Transaction in cache memory for rast retrival"""
    def store_utxos_in_cache(self):
        for tx in self.addTransactionsInBlock:
            self.utxos[tx.TxId] = tx


    def remove_spent_tx(self):
        for txIn_index in self.remove_spent_transaction:
            if txIn_index[0].hex() in self.utxos:
                if len(self.utxos[txIn_index[0].hex()].tx_outs) < 2:
                    del self.utxos[txIn_index[0].hex()]
                else:
                    prev_trans = self.utxos[txIn_index[0].hex()]
                    self.utxos[txIn_index[0].hex()] = prev_trans.tx_outs.pop(txIn_index[1])


    """Read all the transactions from the mempool and store them in a list"""

    def read_transaction_from_mempool(self):
        self.Blocksize = 80
        self.TxIds = []
        self.addTransactionsInBlock = []
        self.remove_spent_transaction = []

        for tx in self.MemPool:
            self.TxIds.append(bytes.fromhex(tx))
            self.addTransactionsInBlock.append(self.MemPool[tx])
            self.Blocksize +=  len(self.MemPool[tx].serialize())

            for spent in self.MemPool[tx].tx_ins:
                self.remove_spent_transaction.append([spent.prev_tx, spent.prev_index])

    """Remove Transactions from Memory Pool"""
    def remove_transactions_from_mempool(self):
        for tx in self.TxIds:
            if tx.hex() in self.MemPool:
                del self.MemPool[tx.hex()]


    def convert_to_json(self):
        self.TxJson = []

        for tx in self.addTransactionsInBlock:
            self.TxJson.append(tx.toDict())

    def calculate_fees(self):
        self.input_amount = 0
        self.output_amount = 0
        """ calculate input amount """
        for TxId_index in self.remove_spent_transaction:
            if TxId_index[0].hex() in self.utxos:
                self.input_amount += self.utxos[TxId_index[0].hex()].tx_outs[TxId_index[1]].amount
        """ calculate output amount"""
        for tx in self.addTransactionsInBlock:
            for tx_out in tx.tx_outs:
                self.output_amout += tx_out.amount
        
        self.fee = self.input_amount - self.output_amount


    def addBlock(self, BlockHeight, prev_block_hash):
        self.read_transaction_from_mempool()
        self.calculate_fees()
        timestamp = int(time.time())
        coinbaseInstance = CoinbaseTx(BlockHeight)
        coinbaseTx = coinbaseInstance.CoinbaseTransaction()
        self.Blocksize += len(coinbaseTx.serialize())

        coinbaseTx.tx_outs[0].amount = coinbaseTx.tx_outs[0].amount + self.fee

        self.TxIds.insert(0, bytes.fromhex(coinbaseTx.TxId))
        self.addTransactionsInBlock.insert(0,coinbaseTx)

        merkleRoot = merkle_root(self.TxIds)[::-1].hex()
        blockheader = BlockHeader(VERSION, prev_block_hash, merkleRoot, timestamp, self.bits)
        blockheader.mine(self.current_target)
        self.remove_spent_tx()
        self.remove_transactions_from_mempool()
        self.store_utxos_in_cache()
        self.convert_to_json()

        print(f"Block {BlockHeight} mined successfully with Nonce value of {blockheader.nonce}.")
        self.write_on_dist([Block(BlockHeight, self.Blocksize , blockheader.__dict__, 1, self.TxJson).__dict__])

    
       

    def main(self):
        lastBlock = self.fetch_last_block()
        if lastBlock is None:
            self.GenesisBlock()

        while True:
            lastBlock = self.fetch_last_block()
            BlockHeight = lastBlock["Height"] + 1
            prev_block_hash = lastBlock['BlockHeader']['blockHash']
            self.addBlock(BlockHeight, prev_block_hash)

if __name__ == '__main__':
    with Manager() as manager:
        utxos = manager.dict()
        MemPool = manager.dict()

        webapp = Process(target = main, args = (utxos, MemPool))
        webapp.start()

        blockchain = Blockchain(utxos, MemPool)
        blockchain.main()
