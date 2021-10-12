from brownie import network
import pytest
from scripts.util import (
    LOCAL_BLOCK_CHAIN_ENV,
    get_account,
    fund_with_link,
)
from scripts.deploy import deploy_lottery
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCK_CHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    time.sleep(60)  # wait for our randomness chainlink node to respond
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
