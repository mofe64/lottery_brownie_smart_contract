from brownie import (
    accounts,
    config,
    network,
    MockV3Aggregator,
    Contract,
    VRFCoordinatorMock,
    LinkToken,
    interface,
)
from web3 import Web3

LOCAL_BLOCK_CHAIN_ENV = ["development", "ganache-local"]
FORKED_LOCAL_ENV = ["mainnet-fork", "mainnet-fork-dev"]


def get_account(index=None, id=None):
    # accounts can be loaded in 3 ways
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")

    if index:
        return accounts[index]

    if id:
        return accounts.load(id)

    if (
        network.show_active() in LOCAL_BLOCK_CHAIN_ENV
        or network.show_active() in FORKED_LOCAL_ENV
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """
    This function will get the contract address from the brownie config if found
    otherwise it will deploy a mock version of that contract and return that mock contract

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract : The most recently deployed version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCK_CHAIN_ENV:
        # checking if we have a previously deployed contract of this type
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


DECIMALS = 8
INITIAL_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed mock price feed")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # note amount here is 0.1 link
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    # using contract directly
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # using interface
    # link_token_contract = interface.LinkTokenInterface(
    #     link_token.address
    # )  # we are creating the mock contract here using the interface which has already been added to contracts/interfaces dir.
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Funded contract with link")
    return tx
