import pytest
from pathlib import Path
from web3 import Web3

from .utils import ADDRS, sign_transaction
from .network import setup_custom_cronos

pytestmark = pytest.mark.mempool

@pytest.fixture(scope="module")
def cronos(tmp_path_factory):
    path = tmp_path_factory.mktemp("cronos-mempool")
    yield from setup_custom_cronos(
        path, 26200, Path(__file__).parent / "configs/long_timeout_commit.yaml"
    )

def test_mempool(cronos):
    w3: Web3 = cronos.w3
    filter = w3.eth.filter("pending")
    assert filter.get_new_entries() == []

    # fist send one tx, check tx in mempool
    signed = sign_transaction(w3, {"to": ADDRS["community"], "value": 1000})
    txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txhash)
    assert receipt.status == 1
    assert filter.get_new_entries() == [txhash]

    # send many txs to mempool
    total = 1
    for i in range(0, 100):
        signed = sign_transaction(w3, {"to": ADDRS["community"], "value": 1000})
        txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(txhash)
        assert receipt.status == 1
        assert txhash in filter.get_new_entries()