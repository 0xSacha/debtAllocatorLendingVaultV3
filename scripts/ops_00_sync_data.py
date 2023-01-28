import json
import os
from ape import project


def _load_config(config_file):
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), config_file)
    with open(CONFIG_PATH, "r") as file:
        config = json.load(file)
    return config


def main():
    ADDRESSES = []
    CALL_LEN = []
    CONTRACTS = []
    SELECTORS = []
    CALLDATA = []
    OFFSET = []
    CALCULATIONS_LEN = []
    CALCULATIONS = []
    CONDITIONS_LEN = []
    CONDITIONS = []
    config = _load_config("config_mainnet.json")
    block_number_start = 16477135
    block_number_range = 10000
    block_number_stop = block_number_start + block_number_range

    debt_allocator = project.DebtAllocator.at(config["debt_allocator_address"])
    ## Get all events that changed strategies
    list_strategy_added_events = list(
        debt_allocator.StrategyAdded.range(block_number_start, block_number_stop)
    )
    list_strategy_updated_events = list(
        debt_allocator.StrategyUpdated.range(block_number_start, block_number_stop)
    )
    list_strategy_removed_events = list(
        debt_allocator.StrategyRemoved.range(block_number_start, block_number_stop)
    )

    list_all_events = list(
        list_strategy_added_events
        + list_strategy_removed_events
        + list_strategy_updated_events
    )

    # Find last update
    latest_block = 0
    latest_event = ""
    if len(list_all_events) > 0:
        latest_event = list_all_events[0]
        for e in list_all_events:
            if e.block_number > latest_block:
                latest_block = e.block_number
                latest_event = e

    # No update events
    if latest_event == "":
        print("No update events")
        return

    # Read last update
    strat_array = latest_event.Strategies
    ADDRESSES = strat_array[0]
    CALL_LEN = strat_array[1]
    CONTRACTS = strat_array[2]
    SELECTORS = []
    SELECTORS = list(strat_array[3])
    for i in range(len(SELECTORS)):
        SELECTORS[i] = SELECTORS[i].hex()

    CALLDATA = []
    CALLDATA = list(strat_array[4])
    for i in range(len(list(strat_array[4]))):
        CALLDATA[i] = list(strat_array[4][i])
        for j in range(len(CALLDATA[i])):
            CALLDATA[i][j] = CALLDATA[i][j].hex()
    OFFSET = strat_array[5]
    CALCULATIONS_LEN = strat_array[6]
    CALCULATIONS = strat_array[7]
    CONDITIONS_LEN = strat_array[8]
    CONDITIONS = strat_array[9]

    result = {}
    result["addresses"] = ADDRESSES
    result["callLen"] = CALL_LEN
    result["contracts"] = CONTRACTS
    result["selectors"] = SELECTORS
    result["callData"] = CALLDATA
    result["offset"] = OFFSET
    result["calculationsLen"] = CALCULATIONS_LEN
    result["calculations"] = CALCULATIONS
    result["conditionsLen"] = CONDITIONS_LEN
    result["conditions"] = CONDITIONS
    f = open("./scripts/config/strategies_info.json", "w")
    json.dump(result, f)
    f.close()
    print("✅ Data Strategies load")
