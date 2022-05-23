from web3 import Web3

from .utils import ADDRS, sign_transaction, deploy_contract, CONTRACTS



def test_pending_transaction_filter(cluster):
    w3: Web3 = cluster.w3
    flt = w3.eth.filter("pending")
    assert flt.get_new_entries() == []

    signed = sign_transaction(w3, {"to": ADDRS["community"], "value": 1000})
    txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txhash)
    assert receipt.status == 1
    assert flt.get_new_entries() == [txhash]


def test_block_filter(cluster):
    w3: Web3 = cluster.w3
    # new blocks
    flt = w3.eth.filter('latest')
    signed = sign_transaction(w3, {"to": ADDRS["community"], "value": 1000})
    txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txhash)
    assert receipt.status == 1
    blocks = flt.get_new_entries()
    print(blocks)
    assert len(blocks) == 1

def test_event_log_filter(cronos):
    w3 = cronos.w3
    mycontract = deploy_contract(w3, CONTRACTS["Greeter"])
    assert "Hello" == mycontract.caller.greet()
    # event_filter = w3.eth.filter({"address": contract.address})
    events = mycontract.events
    print(events)
    print(dir(events))
    assert 0 == 1

