from scripts.util import get_account, get_contract, fund_with_link
from brownie import Lottery, config, network
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Lottery deployed")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)  # wait for transaction to complete before proceeding
    print("Lottery started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = (
        lottery.getEntranceFee() + 1000000
    )  # we tack on some wei to the value incase our estimation is slightly off
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("Lottery entered...")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # fund the contract with some link token since our randomness chainlink contract requires link to be processed
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    # since we are calling a chain link node and that node in return calls our callback function, we need to wait for the callback call before proceeding
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the winner")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
