from Blockchain.Backend.util.util import decodeBase58
from Blockchain.Backend.core.script import script
from Blockchain.Backend.core.tx import TxIn, TxOut, Tx
from Blockchain.Backend.core.database.database import AccountDB
from Blockchain.Backend.core.EllepticCurve.EllepticCurve import PrivateKey
import time
class sendBTC:
    def __init__(self, fromAccount, toAccount, amount, UTXOS):
        self.COIN = 100000000
        self.FromPublicAddress = fromAccount
        self.toAccount = toAccount
        self.Amount = amount * self.COIN
        self.utxos = UTXOS

    def scriptPubKey(self, PublicAddress):
        h160 = decodeBase58(PublicAddress)
        script_pubkey = script().p2pkh_script(h160)
        return script_pubkey
    
    def getPrivateKey(self):
        AllAccounts = AccountDB().read()
        for account in AllAccounts:
            if account['PublicAddress'] == self.FromPublicAddress:
                return account['privateKey']

    def prepareTxIn(self):
        TxIns = []
        self.Total = 0

        """Convert Public Address into Public Hash to find tx_out that are locked to this hash"""

        self.From_address_script_pubkey = self.scriptPubKey(self.FromPublicAddress)
        self.fromPubKeyHash = self.From_address_script_pubkey.cmds[2]

        newutxos = {}

        try:
            while len(newutxos) < 1:
                newutxos = dict(self.utxos)
                time.sleep(2)
        except Exception as e:
            print(f"Error in converting the managed Dict to Normal Dict: {e}")

        for Txbyte in newutxos:
            if self.Total < self.Amount:
                TxObj = newutxos[Txbyte]
            
                for index, txout in enumerate(TxObj.tx_outs):
                    if txout.script_pubkey.cmds[2] == self.fromPubKeyHash:
                        self.Total += txout.amount
                        prev_tx = bytes.fromhex(TxObj.id())
                        TxIns.append(TxIn(prev_tx, index))

            else:
                break

        self.isBalanceEnough = True
        if self.Total < self.Amount:
            self.isBalanceEnough = False

        return TxIns

            

    def prepareIxOut(self):
        TxOuts = []
        to_scriptPubkey = self.scriptPubKey(self.toAccount)
        TxOuts.append(TxOut(self.Amount, to_scriptPubkey))

        """Calculate Fee"""
        self.fee = self.COIN
        self.changeAmount = self.Total - self.Amount - self.fee

        TxOuts.append(TxOut(self.changeAmount, self.From_address_script_pubkey))
        return TxOuts
    
    def signTx(self):
        secret = self.getPrivateKey()
        priv = PrivateKey(secret = secret)

        for index, input in enumerate(self.TxIns):
            self.TxObj.sign_input(index, priv, self.From_address_script_pubkey)

        return True


    def prepareTransaction(self):
        self.TxIns = self.prepareTxIn()
        
        if self.isBalanceEnough:
            self.TxOuts = self.prepareIxOut()
            self.TxObj = Tx(1, self.TxIns, self.TxOuts, 0)
            self.TxObj.TxId = self.TxObj.id()
            self.signTx()
            return self.TxObj
        
        return False