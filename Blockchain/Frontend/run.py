from flask import Flask, render_template, request
from Blockchain.client.sendBTC import sendBTC
from Blockchain.Backend.core.tx import Tx

app = Flask(__name__)

@app.route('/', methods = ["GET", "POST"])
def wallet():
    message = ''
    if request.method == "POST":
        fromAddress = request.form.get("fromAddress")
        toAddress = request.form.get("toAddress")
        Amount = request.form.get("Amount", type = int)
        sendCoin = sendBTC(fromAddress, toAddress, Amount, UTXOS)
        TxObj = sendCoin.prepareTransaction()

        scriptPubKey = sendCoin.scriptPubKey(fromAddress)
        verified = True

        if not TxObj:
            message = "Invalid Transaction"

        if isinstance(TxObj, Tx):
            for index, tx in enumerate(TxObj.tx_ins):
                if not TxObj.verify_input(index, scriptPubKey):
                    verified = False

            if verified:
                MEMPOOL[TxObj.TxId] = TxObj
                message = "Transaction added in memory pool"

            
    return render_template('wallet.html', message = message)

def main(utxos, MemPool):
    global UTXOS 
    global MEMPOOL
    UTXOS = utxos
    MEMPOOL = MemPool
    app.run()
