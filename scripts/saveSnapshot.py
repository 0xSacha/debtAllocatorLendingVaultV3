import click
from ape.cli import network_option, NetworkBoundCommand
from ape import accounts, project
import json


def main():
    f = open("./scripts/config.json")
    config_dict = json.load(f)
    f.close()
    account = accounts.load(config_dict["account"])
    contract = project.DebtAllocator.at(config_dict["debt_allocator_address"])

    tx = contract.saveSnapshot(sender=account)
    logs = list(tx.decode_logs(contract.NewSnapshot))
    
    strategies_data = logs[0].dataStrategies
    strategies_data_result = []
    for sdata in strategies_data:
        strategies_data_result.append(len(sdata))
        strategies_data_result += sdata

    strategies_calculation = logs[0].calculation
    strategies_calculation_result = []
    for scalc in strategies_calculation:
        strategies_calculation_result.append(len(scalc))
        strategies_calculation_result += scalc 

    strategies_condition = logs[0].condition
    strategies_condition_result = []
    for scond in strategies_condition:
        strategies_condition_result.append(len(scond))
        strategies_condition_result += scond 

    result = {}
    result['current_debt_ratio'] = [0, 0]
    result['new_debt_ratio'] = [5000, 5000]
    result['strategies_data'] = strategies_data_result
    result['strategies_calculation'] = strategies_calculation_result
    result['strategies_calculation_conditions'] = strategies_condition_result

    f = open("./cairoScripts/input/apy_calculator_lender_input.json", "w")
    json.dump(result, f)
    f.close()
    print(result)
