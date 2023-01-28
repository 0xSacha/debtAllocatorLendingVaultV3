from dotenv import load_dotenv
import os
import json
from ape import accounts, project
from starkware.cairo.bootloaders.generate_fact import get_program_output
from starkware.cairo.lang.vm.cairo_pie import CairoPie


def _load_config(config_file):
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), config_file)
    with open(CONFIG_PATH, "r") as file:
        config = json.load(file)
    return config


def main():
    load_dotenv()
    account = accounts.load(os.environ["ACCOUNT_ALIAS"])
    config = _load_config("config_mainnet.json")

    #### SOLUTION VERIFICATION ####
    f = open(config["strategies_info_path"])
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

    debt_allocator = project.DebtAllocator.at(config["debt_allocator_address"])
    cairo_pie = CairoPie.from_file(config["cairo_program_output_path"])
    program_output = get_program_output(cairo_pie)

    tx = debt_allocator.verifySolution(
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
        max_fee="100 gwei", max_priority_fee="1 gwei",
        sender=account,
    )
    logs = list(tx.decode_logs(debt_allocator.NewSolution))
    print(logs)
