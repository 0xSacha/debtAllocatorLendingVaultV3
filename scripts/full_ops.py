from ape import accounts, project
from starkware.cairo.sharp.client_lib import CairoPie, ClientLib
from starkware.cairo.sharp.fact_checker import FactChecker
from starkware.cairo.bootloaders.generate_fact import get_program_output
from starkware.cairo.sharp.sharp_client import SharpClient, init_client
from starkware.cairo.lang.compiler.assembler import Program
from typing import List, Optional
import json
import os
import time

def main():
    f = open("./scripts/config.json")
    config_dict = json.load(f)
    f.close()

    account = accounts.load(config_dict["account"])
    contract = project.DebtAllocator.at(config_dict["debt_allocator_address"])

    save_snapshot(account, contract, config_dict["new_allocation_array"])

    #### START CLIENT ####
    client = init_client(config_dict["bin_path"], [config_dict["rpc"]])

    #### RUN THE CAIRO PROGRAM ####
    compiled_program = client.compile_cairo(config_dict["cairo_program_path"])
    cairo_pie = client.run_program(compiled_program, config_dict["cairo_program_input_path"])
    # save cairo pie
    cairo_pie.to_file(config_dict["cairo_program_output_path"])
    program_output = get_program_output(cairo_pie)

    #### SUBMIT FOR VERIFICATION ####
    print("PROGRAM OUTPUT")
    print(program_output)
    print(program_output[-1]/1e16, "% vs.", program_output[-2]/1e16, "%")
    job_key = client.submit_cairo_pie(cairo_pie=cairo_pie)
    fact = client.get_fact(cairo_pie)
    print("Job Key:", job_key)
    print("Fact:", fact)

    mins = 0
    print("Waiting for Job to be processed. This can take several minutes (> 15 min)")
    while True:
        if client.get_job_status(job_key) == "PROCESSED":
            print("Job has been processed!")
            break;
        print(mins, "minutes passed")
        mins += 1
        time.sleep(60)
        print("Job is still pending... sleeping for 60 secs")

    #### SOLUTION VERIFICATION ####
    tx = contract.verifySolution(program_output, max_priority_fee="0.0001 gwei", sender=account)
    logs = list(tx.decode_logs(contract.NewSolution))
    print(logs)

def save_snapshot(account, contract, new_allocation = [0, 0]):
    tx = contract.saveSnapshot(max_priority_fee="0.0001 gwei", sender=account)
    logs = list(tx.decode_logs(contract.NewSnapshot))
    
    strategies_data = logs[0].dataStrategies
    strategies_data_result = []
    for sdata in strategies_data:
        strategies_data_result.append(int(len(sdata)))
        strategies_data_result += sdata

    strategies_calculation = logs[0].calculation
    strategies_calculation_result = []
    for scalc in strategies_calculation:
        strategies_calculation_result.append(int(len(scalc)/3))
        strategies_calculation_result += scalc 

    strategies_condition = logs[0].condition
    strategies_condition_result = []
    for scond in strategies_condition:
        strategies_condition_result.append(int((len(scond)-4)/3))
        strategies_condition_result += scond 

    result = {}
    result['current_debt_ratio'] = [contract.debtRatios(0), contract.debtRatios(1)]
    result['new_debt_ratio'] = new_allocation
    result['strategies_data'] = strategies_data_result
    result['strategies_calculation'] = strategies_calculation_result
    result['strategies_calculation_conditions'] = strategies_condition_result

    f = open("./cairoScripts/input/apy_calculator_lender_input.json", "w")
    json.dump(result, f)
    f.close()

    print("SNAPSHOT RESULT:")
    print(result)

