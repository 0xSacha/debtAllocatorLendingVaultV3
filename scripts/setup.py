# TODO: import different functions and use this script as a router / proxy to setup folder functions
from web3 import Web3
from web3._utils.events import get_event_data
from web3._utils.filters import construct_event_filter_params
import json
import os
from dotenv import load_dotenv


def run():
    ADDRESSES = []
    CALL_LEN = []
    CONTRACTS = []
    SELECTORS = []
    CALLDATA = []
    OFFSET = []
    CALCULATIONS_LEN = []
    CALCULATIONS = []
    CONDTIONS_LEN = []
    CONDTIONS = []
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_testnet.json")
    ABI_PATH = os.path.join(os.path.dirname(__file__), "/config/DebtAllocatorAbi.json")

    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)

    with open(ABI_PATH, "r") as abi_file:
        abi = json.load(abi_file)

    load_dotenv()
    RPC = os.getenv("NODE_RPC_URL")
    web3 = Web3(Web3.HTTPProvider(RPC))
    address = config["debt_allocator_address"]
    contract = web3.eth.contract(address, abi=abi)
    abi_codec = web3.codec

    current_block = 0
    result = {}
    result["addresses"] = []
    result["callLen"] = []
    result["contracts"] = []
    result["selectors"] = []
    result["callData"] = []
    result["offset"] = []
    result["calculationsLen"] = []
    result["calculations"] = []
    result["conditionsLen"] = []
    result["conditions"] = []

    abi = contract.events.StrategyAdded._get_event_abi()
    data_filter_set, event_filter_params = construct_event_filter_params(
        abi,
        abi_codec,
        contract_address=config["debt_allocator_address"],
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
        strat_array = last_strategy_added.args.Strategies
        if last_block > current_block:
            current_block = last_block
            ADDRESSES = strat_array[0]
            CALL_LEN = strat_array[1]
            CONTRACTS = strat_array[2]
            SELECTORS = strat_array[3]
            for i in range(len(SELECTORS)):
                SELECTORS[i] = SELECTORS[i].hex()

            CALLDATA = strat_array[4]
            for i in range(len(CALLDATA)):
                for j in range(len(CALLDATA[i])):
                    CALLDATA[i][j] = CALLDATA[i][j].hex()
            OFFSET = strat_array[5]
            CALCULATIONS_LEN = strat_array[6]
            CALCULATIONS = strat_array[7]
            CONDTIONS_LEN = strat_array[8]
            CONDTIONS = strat_array[9]

    abi = contract.events.StrategyUpdated._get_event_abi()
    data_filter_set, event_filter_params = construct_event_filter_params(
        abi,
        abi_codec,
        contract_address=config["debt_allocator_address"],
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
        strat_array = last_strategy_added.args.Strategies
        if last_block > current_block:
            current_block = last_block
            ADDRESSES = strat_array[0]
            CALL_LEN = strat_array[1]
            CONTRACTS = strat_array[2]
            SELECTORS = strat_array[3]
            for i in range(len(SELECTORS)):
                SELECTORS[i] = SELECTORS[i].hex()

            CALLDATA = strat_array[4]
            for i in range(len(CALLDATA)):
                for j in range(len(CALLDATA[i])):
                    print(CALLDATA[i][j].hex())
                    CALLDATA[i][j] = CALLDATA[i][j].hex()
            OFFSET = strat_array[5]
            CALCULATIONS_LEN = strat_array[6]
            CALCULATIONS = strat_array[7]
            CONDTIONS_LEN = strat_array[8]
            CONDTIONS = strat_array[9]

    abi = contract.events.StrategyRemoved._get_event_abi()
    data_filter_set, event_filter_params = construct_event_filter_params(
        abi,
        abi_codec,
        contract_address=config["debt_allocator_address"],
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
        strat_array = last_strategy_added.args.Strategies
        if last_block > current_block:
            current_block = last_block
            ADDRESSES = strat_array[0]
            CALL_LEN = strat_array[1]
            CONTRACTS = strat_array[2]
            SELECTORS = strat_array[3]
            for i in range(len(SELECTORS)):
                SELECTORS[i] = SELECTORS[i].hex()

            CALLDATA = strat_array[4]
            for i in range(len(CALLDATA)):
                for j in range(len(CALLDATA[i])):
                    print(CALLDATA[i][j].hex())
                    CALLDATA[i][j] = CALLDATA[i][j].hex()
            OFFSET = strat_array[5]
            CALCULATIONS_LEN = strat_array[6]
            CALCULATIONS = strat_array[7]
            CONDTIONS_LEN = strat_array[8]
            CONDTIONS = strat_array[9]

    result = {}
    result["addresses"] = ADDRESSES
    result["callLen"] = CALL_LEN
    result["contracts"] = CONTRACTS
    result["selectors"] = SELECTORS
    result["callData"] = CALLDATA
    result["offset"] = OFFSET
    result["calculationsLen"] = CALCULATIONS_LEN
    result["calculations"] = CALCULATIONS
    result["conditionsLen"] = CONDTIONS_LEN
    result["conditions"] = CONDTIONS
    f = open("./scripts/strategies_info.json", "w")
    json.dump(result, f)
    f.close()
    print("✅ Data Strategies load")


run()
