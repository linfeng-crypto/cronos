import pytest
from pathlib import Path
from web3 import Web3

from .utils import ADDRS, sign_transaction
from .network import setup_custom_cronos

pytestmark = pytest.mark.mempool

@pytest.fixture(scope="module")
def mempool_cronos(tmp_path_factory):
    path = tmp_path_factory.mktemp("cronos-mempool")
    yield from setup_custom_cronos(
        path, 26000, Path(__file__).parent / "configs/long_timeout_commit.yaml"
    )

def test_mempool(mempool_cronos):
    w3: Web3 = mempool_cronos.w3
    flt = w3.eth.filter("pending")
    assert flt.get_new_entries() == []

    signed = sign_transaction(w3, {"to": ADDRS["community"], "value": 1000})
    txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txhash)
    assert receipt.status == 1
    assert flt.get_new_entries() == [txhash]

#
# import web3
# from web3._utils.method_formatters import receipt_formatter
# from web3.datastructures import AttributeDict
# from eth_account import Account
#
# from .utils import send_transaction, sign_transaction, ADDRS, KEYS



# def test_mempool(cronos):
#     w3 = cronos.w3
#     signed = sign_transaction(w3, {"to": ADDRS["community"], "value": 1000})
#     txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
#
#     tx_filter = w3.eth.filter('pending')
#     txs = tx_filter.get_all_entries()
#     assert len(txs) > 0
#     assert txhash in txs
#
#     receipt = w3.eth.wait_for_transaction_receipt(txhash)
#     assert receipt.status == 1
#     txs = tx_filter.get_all_entries()
#     assert len(txs) == 0


    # tx1 = w3.eth.get_transaction(txhash_1)
    # assert tx1["transactionIndex"] == 0
    #
    #
    # # tx already in mempool
    # with pytest.raises(ValueError) as exc:
    #     send_transaction(
    #         w3,
    #         {
    #             "to": ADDRS["community"],
    #             "value": 10000,
    #             "gasPrice": gas_price,
    #             "nonce": w3.eth.get_transaction_count(ADDRS["validator"]) - 1,
    #         },
    #         KEYS["validator"],
    #     )
    # assert "tx already in mempool" in str(exc)

    # invalid sequence
    # with pytest.raises(ValueError) as exc:
    #     send_transaction(
    #         w3,
    #         {
    #             "to": ADDRS["community"],
    #             "value": 10000,
    #             "gasPrice": w3.eth.gas_price,
    #             "nonce": w3.eth.get_transaction_count(ADDRS["validator"]) + 1,
    #         },
    #         KEYS["validator"],
    #     )
    # assert "invalid sequence" in str(exc)