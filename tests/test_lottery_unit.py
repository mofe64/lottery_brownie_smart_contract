from brownie import Lottery, accounts, config, network, exceptions
from web3 import Web3
from scripts.deploy import deploy_lottery, get_account, fund_with_link, get_contract
import pytest

from scripts.util import LOCAL_BLOCK_CHAIN_ENV, get_account


def test_get_entrance_fee():
    if network.show_active not in LOCAL_BLOCK_CHAIN_ENV:
        pytest.skip()

    lottery = deploy_lottery()
    # 2000 eth / usd initial price value
    # usdEntryFee = 50
    # 2000/1 === 50/x == 0.025
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    if network.show_active not in LOCAL_BLOCK_CHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCK_CHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]  # access events
    STATIC_RNG = 777  # dummy random number which we will use to determine winner, the chain link call was supposed to proivde this for us, but since we are mocking the call we generate it ourself and pass to our callback function
    # we mnaually call this callback function which the chain link node was supposed to call for us, and pass in the requestId which we pulled from our event
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account}
    )
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    # 777 % 3 = 0 using the formula
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery
