from ape import accounts, project
from starkware.cairo.sharp.client_lib import CairoPie, ClientLib
from starkware.cairo.sharp.fact_checker import FactChecker
from starkware.cairo.bootloaders.generate_fact import get_program_output
from starkware.cairo.sharp.sharp_client import SharpClient
from starkware.cairo.lang.compiler.assembler import Program
from typing import List, Optional
import json
import os
import time
from dotenv import load_dotenv


def main():
    # Load configuration files
    load_dotenv()
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_testnet.json")
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)

    account = accounts.load(os.environ["ACCOUNT_ALIAS"])
    contract = project.DebtAllocator.at(config["debt_allocator_address"])
    contract.updateCairoProgramHash(config["cairo_program_hash"], sender=account, max_priority_fee="1 gwei")
    