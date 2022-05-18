import pytest
from pathlib import Path
from web3 import Web3
from datetime import datetime

from .utils import ADDRS, sign_transaction, KEYS, send_transaction, deploy_contract, CONTRACTS, wait_for_new_blocks
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
    cli = cronos.cosmos_cli(0)

    # fist send one tx, check tx in mempool
    # signed = sign_transaction(w3, {"to": address_to, "value": 1000})
    # txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
    # receipt = w3.eth.wait_for_transaction_receipt(txhash)
    block_num_0 = w3.eth.get_block_number()
    # assert receipt.status == 1
    # assert filter.get_new_entries() == [txhash]

    current_height_0 = int((cli.status())["SyncInfo"]["latest_block_height"])
    print(f"current block number 0: {block_num_0}")
    now = datetime.timestamp(datetime.now())
    nonce_begin = w3.eth.get_transaction_count(address_from)

    # signed = sign_transaction(w3, tx, key)
    # txhash = w3.eth.send_raw_transaction(signed.rawTransaction)

    sended_hash_list = []
    for i in range(5):
        nonce = nonce_begin + i
        tx = {
            "to": address_to,
            "value": 10000,
            "gasPrice": gas_price,
            "nonce": nonce,
        }
        signed = sign_transaction(w3, tx, key_from)
        txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
        sended_hash_list.append(txhash)
        now_2 = datetime.timestamp(datetime.now())
        print(f"use time: {now_2 - now}")
    block_num_1 = w3.eth.get_block_number()
    assert block_num_1 == block_num_0
    print(f"all send tx hash: f{sended_hash_list}")
    all_pending_tx_hash = filter.get_all_entries()
    print(f"all pending tx hash: f{all_pending_tx_hash}")
    wait_for_new_blocks(cli, 1)
    # get all txhash in mempool
    all_tx_hash_list = filter.get_all_entries()
    assert len(all_tx_hash_list) == 0

    # test contract
    block_num_2 = w3.eth.get_block_number()
    print(f"block number 2: f{block_num_2}")
    contract = deploy_contract(w3, CONTRACTS["Greeter"])
    tx = contract.functions.setGreeting("world").buildTransaction()
    signed = sign_transaction(w3, tx, key_from)
    txhash = w3.eth.send_raw_transaction(signed.rawTransaction)

    # check tx in mempool
    block_num_3 = w3.eth.get_block_number()
    assert block_num_3 == block_num_2
    new_txs = filter.get_new_entries()
    assert txhash in new_txs

    # wait block update
    wait_for_new_blocks(cli, 1)
    greeter_call_result = contract.caller.greet()
    assert "world" == greeter_call_result
    print(f"all txs in mempool: {filter.get_all_entries()}")
