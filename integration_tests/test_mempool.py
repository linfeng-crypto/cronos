import pytest
from pathlib import Path
from web3 import Web3

from .utils import ADDRS, sign_transaction, KEYS, send_transaction
from .network import setup_custom_cronos, setup_cronos

pytestmark = pytest.mark.mempool


# @pytest.fixture(scope="module")
# def cronos(tmp_path_factory):
#     path = tmp_path_factory.mktemp("cronos-mempool")
#     yield from setup_cronos(path, 26200)

@pytest.fixture(scope="module")
def cronos(tmp_path_factory):
    path = tmp_path_factory.mktemp("cronos-mempool")
    cfg = Path(__file__).parent / "configs/long_timeout_commit.yaml"
    yield from setup_custom_cronos(
        path, 26200, cfg
    )

def test_mempool(cronos):
    w3: Web3 = cronos.w3
    filter = w3.eth.filter("pending")
    assert filter.get_new_entries() == []

    key_from = KEYS["validator"]
    address_from = ADDRS["validator"]
    address_to = ADDRS["community"]
    gas_price = w3.eth.gas_price
    nonce = w3.eth.get_transaction_count(address_from)

    # fist send one tx, check tx in mempool
    # signed = sign_transaction(w3, {"to": address_to, "value": 1000})
    # txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
    # receipt = w3.eth.wait_for_transaction_receipt(txhash)
    # assert receipt.status == 1
    # assert filter.get_new_entries() == [txhash]


    # send many txs to mempool
    # for i in range(0, 50):
    #     signed = sign_transaction(w3, {"to": ADDRS["community"], "value": 100})
    #     txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
    #     receipt = w3.eth.wait_for_transaction_receipt(txhash)
    #     assert receipt.status == 1
    #     assert txhash in filter.get_new_entries()
    tx_hash = send_transaction(
        w3,
        {
            "to": address_to,
            "value": 10000,
            "gasPrice": gas_price,
            "nonce": nonce,
        },
        key_from,
    )
    assert tx_hash in filter.get_new_entries()
