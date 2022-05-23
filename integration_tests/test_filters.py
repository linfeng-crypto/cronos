from web3 import Web3

from .utils import ADDRS, sign_transaction, deploy_contract, send_transaction, CONTRACTS, wait_for_new_blocks



def test_pending_transaction_filter(cluster):
    w3: Web3 = cluster.w3
    flt = w3.eth.filter("pending")
    assert flt.get_new_entries() == []

    signed = sign_transaction(w3, {"to": ADDRS["community"], "value": 1000})
    txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txhash)
    assert receipt.status == 1
    assert txhash in flt.get_new_entries()


def test_block_filter(cluster):
    w3: Web3 = cluster.w3
    # new blocks
    signed = sign_transaction(w3, {"to": ADDRS["community"], "value": 1000})
    txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txhash)
    assert receipt.status == 1
    flt = w3.eth.filter('latest')
    blocks = flt.get_new_entries()
    wait_for_new_blocks(1)
    print(f"yyyyyyyyyyyyyyyyyyyyyyyyyyyyy: {blocks}")
    assert len(blocks) == 1

def test_event_log_filter(cronos):
    w3 = cronos.w3
    mycontract = deploy_contract(w3, CONTRACTS["Greeter"])
    assert "Hello" == mycontract.caller.greet()
    event_filter = mycontract.events.ChangeGreeting.createFilter(fromBlock="0x0")

    tx = mycontract.functions.setGreeting("world").buildTransaction()
    tx_receipt = send_transaction(w3, tx)
    assert tx_receipt.status == 1
    # event_filter = w3.eth.filter({"address": mycontract.address})
    print(f"fffffffffffffff: {event_filter.get_new_entries()}")

    log = mycontract.events.ChangeGreeting().processReceipt(tx_receipt)
    print("llllllllllllll:", log)
    assert 0 == 1

