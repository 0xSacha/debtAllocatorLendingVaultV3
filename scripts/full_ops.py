from ape import accounts, project
from client_lib import ClientLib
from sharp_client import SharpClient
from starkware.cairo.bootloaders.generate_fact import get_program_output
from typing import Optional
import json
import os
import time
from dotenv import load_dotenv


def main():
    # Load configuration files
    load_dotenv()
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_mainnet.json")
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)

    account = accounts.load(os.environ["ACCOUNT_ALIAS"])
    contract = project.DebtAllocator.at(config["debt_allocator_address"])

    save_snapshot(
        account,
        contract,
        config["new_allocation_array"],
        config["strategies_info_path"],
        config["cairo_program_input_path"],
    )

    #### START CLIENT ####
    client = init_client(os.environ["BIN_PATH"], [os.environ["NODE_RPC_URL"]])

    #### RUN THE CAIRO PROGRAM ####
    compiled_program = client.compile_cairo(config["cairo_program_path"])
    cairo_pie = client.run_program(compiled_program, config["cairo_program_input_path"])
    cairo_pie.to_file(config["cairo_program_output_path"])
    program_output = get_program_output(cairo_pie)

    #### SUBMIT FOR VERIFICATION ####
    print("PROGRAM OUTPUT")
    print(program_output)
    print(program_output[-1] / 1e16, "% vs.", program_output[-2] / 1e16, "%")
    # print(program_output[-1]/1e27, "% vs.", program_output[-2]/1e27, "%")

    job_key = client.submit_cairo_pie(cairo_pie=cairo_pie)
    fact = client.get_fact(cairo_pie)

    print("Job Key:", job_key)
    print("Fact:", fact)

    mins = 0
    print("Waiting for Job to be processed. This can take several minutes (> 15 min)")
    while True:
        if client.get_job_status(job_key) == "PROCESSED":
            print("Job has been processed!")
            break
        print(mins, "minutes passed")
        mins += 1
        time.sleep(60)
        print("Job is still pending... sleeping for 60 secs")

    # now that job has been processed, we can verify on-chain, just need to wait a bit

    time.sleep(10)

    #### SOLUTION VERIFICATION ####

    f = open(strategies_info_path)
    strategies_info = json.load(f)
    f.close()

    addresses = strategies_info["addresses"]
    callLen = strategies_info["callLen"]
    contracts = strategies_info["contracts"]
    selectors = strategies_info["selectors"]
    callData = strategies_info["callData"]
    offset = strategies_info["offset"]
    calculationsLen = strategies_info["calculationsLen"]
    calculations = strategies_info["calculations"]
    conditionsLen = strategies_info["conditionsLen"]
    conditions = strategies_info["conditions"]

    tx = contract.verifySolution(
        program_output,
        (
            addresses,
            callLen,
            contracts,
            selectors,
            callData,
            offset,
            calculationsLen,
            calculations,
            conditionsLen,
            conditions,
        ),
        max_priority_fee="1 gwei",
        sender=account,
    )
    logs = list(tx.decode_logs(contract.NewSolution))
    print(logs)


def save_snapshot(
    account, contract, new_allocation, strategies_info_path, cairo_program_input_path
):

    ## LOAD CURRENT CONFIG FROM LOCAL
    f = open(strategies_info_path)
    strategies_info = json.load(f)
    f.close()

    addresses = strategies_info["addresses"]
    callLen = strategies_info["callLen"]
    contracts = strategies_info["contracts"]
    selectors = strategies_info["selectors"]
    callData = strategies_info["callData"]
    offset = strategies_info["offset"]
    calculationsLen = strategies_info["calculationsLen"]
    calculations = strategies_info["calculations"]
    conditionsLen = strategies_info["conditionsLen"]
    conditions = strategies_info["conditions"]

    ## TAKE ON-CHAIN SNAPSHOT
    tx = contract.saveSnapshot(
        (
            addresses,
            callLen,
            contracts,
            selectors,
            callData,
            offset,
            calculationsLen,
            calculations,
            conditionsLen,
            conditions,
        ),
        max_priority_fee="1 gwei",
        sender=account,
    )

    ## SAVE INFO TO FEED CAIRO PROGRAM
    logs = list(tx.decode_logs(contract.NewSnapshot))

    strategies_data = logs[0].dataStrategies
    cumulative_offset = 0
    strategies_data_result = []
    for i in range(int(len(addresses))):
        strategies_data_result.append(callLen[i])
        for j in range(callLen[i]):
            strategies_data_result.append(strategies_data[cumulative_offset + j])
        cumulative_offset += callLen[i]

    strategies_calculation = logs[0].calculation
    cumulative_offset = 0
    strategies_calculation_result = []
    for i in range(int(len(addresses))):
        strategies_calculation_result.append(int(calculationsLen[i] / 3))
        for j in range(calculationsLen[i]):
            strategies_calculation_result.append(
                strategies_calculation[cumulative_offset + j]
            )
        cumulative_offset += calculationsLen[i]

    strategies_condition = logs[0].condition
    cumulative_offset = 0
    strategies_condition_result = []
    for i in range(int(len(addresses))):
        strategies_condition_result.append(int((conditionsLen[i] - 4) / 3))
        for j in range(conditionsLen[i]):
            strategies_condition_result.append(
                strategies_condition[cumulative_offset + j]
            )
        cumulative_offset += conditionsLen[i]

    target_allocation = logs[0].targetAllocations
    current_allocation_vault = []
    for i in range(int(len(addresses))):
        current_allocation_vault.append(target_allocation[i])

    result = {}
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


def init_client(bin_dir: str, node_rpc_url: Optional[str] = None) -> SharpClient:
    """
    Initialized a SharpClient instance, with or without node access.
    """
    # Load configuration file.
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_mainnet.json")
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)

    # Get Cairo toolchain executable paths.
    CAIRO_COMPILE_EXE = os.path.join(os.path.join(bin_dir, "cairo-compile"))
    CAIRO_RUN_EXE = os.path.join(os.path.join(bin_dir, "cairo-run"))

    # Initialize the SharpClient.
    client = SharpClient(
        service_client=ClientLib(config["prover_url"]),
        contract_client=FactChecker(
            fact_registry_address=config["verifier_address"],
            node_rpc_url=node_rpc_url if node_rpc_url is not None else "",
        ),
        steps_limit=config["steps_limit"],
        cairo_compiler_path=CAIRO_COMPILE_EXE,
        cairo_run_path=CAIRO_RUN_EXE,
    )

    return client
