import os, json
from dotenv import load_dotenv
from ape import accounts, project


def _load_config(config_file):
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), config_file)
    with open(CONFIG_PATH, "r") as file:
        config = json.load(file)
    return config


def save_snapshot(
    account, contract, new_allocation, strategies_info_path, cairo_program_input_path
):
    block_number_start = 16510135
    block_number_range = 10000
    block_number_stop = block_number_start + block_number_range
    
    ## LOAD CURRENT CONFIG FROM LOCAL
    f = open(strategies_info_path)
    strategies_info = json.load(f)
    f.close()

    addresses = strategies_info["addresses"]
    callLen = strategies_info["callLen"]
    calculationsLen = strategies_info["calculationsLen"]
    conditionsLen = strategies_info["conditionsLen"]

    logs = list(
        contract.NewSnapshot.range(block_number_start, block_number_stop)
    )
    if len(logs) == 0:
        print("No New Solutions detected")
        return
    strategies_data = logs[-1].dataStrategies
    cumulative_offset = 0
    strategies_data_result = []
    for i in range(int(len(addresses))):
        strategies_data_result.append(callLen[i])
        for j in range(callLen[i]):
            strategies_data_result.append(strategies_data[cumulative_offset + j])
        cumulative_offset += callLen[i]

    strategies_calculation = logs[-1].calculation
    cumulative_offset = 0
    strategies_calculation_result = []
    for i in range(int(len(addresses))):
        strategies_calculation_result.append(int(calculationsLen[i] / 3))
        for j in range(calculationsLen[i]):
            strategies_calculation_result.append(
                strategies_calculation[cumulative_offset + j]
            )
        cumulative_offset += calculationsLen[i]

    strategies_condition = logs[-1].condition
    cumulative_offset = 0
    strategies_condition_result = []
    for i in range(int(len(addresses))):
        strategies_condition_result.append(int((conditionsLen[i] - 4) / 3))
        for j in range(conditionsLen[i]):
            strategies_condition_result.append(
                strategies_condition[cumulative_offset + j]
            )
        cumulative_offset += conditionsLen[i]

    target_allocation = logs[-1].targetAllocations
    current_allocation_vault = []
    for i in range(int(len(addresses))):
        current_allocation_vault.append(target_allocation[i])

    result = {}
    assert len(current_allocation_vault) == len(new_allocation)
    result["current_allocation"] = current_allocation_vault
    result["new_allocation"] = new_allocation
    result["strategies_data"] = strategies_data_result
    result["strategies_calculation"] = strategies_calculation_result
    result["strategies_calculation_conditions"] = strategies_condition_result

    f = open(cairo_program_input_path, "w")
    json.dump(result, f)
    f.close()

    print("SNAPSHOT RESULT:")
    print(result)


def main():
    load_dotenv()
    account = accounts.load(os.environ["ACCOUNT_ALIAS"])
    config = _load_config("config_mainnet.json")

    debt_allocator = project.DebtAllocator.at(config["debt_allocator_address"])
    save_snapshot(
        account,
        debt_allocator,
        config["new_allocation_array"],
        config["strategies_info_path"],
        config["cairo_program_input_path"],
    )
