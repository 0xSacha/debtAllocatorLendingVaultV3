# TODO: import different functions and use this script as a router / proxy to setup folder functions
from web3 import Web3
import requests
from web3._utils.abi import get_constructor_abi, merge_args_and_kwargs
from web3._utils.events import get_event_data
from web3._utils.filters import construct_event_filter_params
from web3._utils.contracts import encode_abi
import json


def run():    
    f = open("./config_testnet.json")
    config_dict = json.load(f)
    f.close()
    f = open("../.build/abi/debtAllocator_abi.json")
    abi = json.load(f)
    f.close()

    infura = 'https://goerli.infura.io/v3/eebdf8732cd044f0a52f976af7781260'
    web3 = Web3(Web3.HTTPProvider(infura))

    address = config_dict["debt_allocator_address"]
    contract = web3.eth.contract(address, abi=abi)
    abi_codec = web3.codec

    last_block = 0
    result = {}
    result["addresses"] = []
    result["callLen"] = []
    result["contracts"] = []
    result["checkdata"] = []
    result["offset"] = []
    result["calculationsLen"] = []
    result["calculations"] = []
    result["conditionsLen"] = []
    result["conditions"] = []

    abi = contract.events.StrategyAdded._get_event_abi()
    data_filter_set, event_filter_params = construct_event_filter_params(
        abi,
        abi_codec,
        contract_address=config_dict["debt_allocator_address"],
        argument_filters=None,
        fromBlock=7958605,
        toBlock="latest",
        address=None,
        topics=None,
    )
    logs = web3.eth.get_logs(event_filter_params)

    if len(logs) > 0:
        last_block = logs[len(logs) - 1].blockNumber
        last_strategy_added = get_event_data(abi_codec, abi, logs[len(logs) - 1])
        print(last_strategy_added)
    
    

    # abi = contract.events.StrategyUpdated._get_event_abi()
    # data_filter_set, event_filter_params = construct_event_filter_params(
    #     abi,
    #     abi_codec,
    #     contract_address=config_dict["debt_allocator_address"],
    #     argument_filters=None,
    #     fromBlock=7958605,
    #     toBlock="latest",
    #     address=None,
    #     topics=None,
    # )
    # logs = web3.eth.get_logs(event_filter_params)

    # if(len(logs) != 0)
    # # block_last_strategy_updated = logs[len(logs) - 1].blockNumber
    # last_strategy_updated = get_event_data(abi_codec, abi, logs[len(logs) - 1])
    # print(last_strategy_updated)

    # abi = contract.events.StrategyRemoved._get_event_abi()
    # data_filter_set, event_filter_params = construct_event_filter_params(
    #     abi,
    #     abi_codec,
    #     contract_address=config_dict["debt_allocator_address"],
    #     argument_filters=None,
    #     fromBlock=7958605,
    #     toBlock="latest",
    #     address=None,
    #     topics=None,
    # )
    # logs = web3.eth.get_logs(event_filter_params)
    # block_last_strategy_removed = logs[len(logs) - 1].blockNumber
    # last_strategy_removed = get_event_data(abi_codec, abi, logs[len(logs) - 1])

    # print(block_last_strategy_removed)
    


run()