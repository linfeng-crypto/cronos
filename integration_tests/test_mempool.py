from pathlib import Path

import pytest
import web3
from web3._utils.method_formatters import receipt_formatter
from web3.datastructures import AttributeDict
from eth_account import Account

from .network import setup_custom_cronos
from .utils import send_transaction, ADDRS, KEYS


pytestmark = pytest.mark.mempool

@pytest.fixture(scope="module")
def cronos(tmp_path_factory):
    path = tmp_path_factory.mktemp("cronos")
    yield from setup_custom_cronos(
        path, 26900, Path(__file__).parent / "configs/long_timeout_commit.yaml"
    )

def test_mempool(cronos):
    w3 = cronos.w3
    gas_price = w3.eth.gas_price
    key = KEYS["validator"]

    # send transaction
    txhash_1 = send_transaction(
        w3,
        {"to": ADDRS["community"], "value": 10000, "gasPrice": gas_price},
        key,
    )["transactionHash"]

    tx_filter = w3.eth.filter('pending')
    txs = tx_filter.get_all_entries()
    assert len(txs) > 0
    assert txhash_1 in txs

    # tx1 = w3.eth.get_transaction(txhash_1)
    # assert tx1["transactionIndex"] == 0
    #
    # initial_block_number = w3.eth.get_block_number()
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