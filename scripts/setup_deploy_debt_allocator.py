from ape import accounts, project
from typing import List, Optional
import json
import os
import time

CAIRO_VERIFIER = "0xAB43bA48c9edF4C2C4bB01237348D1D7B28ef168"
CAIRO_PROGRAM_HASH = "0x18261fedf8bb9295db94450fdda4343f1b04d3ae08f198d079a0e178596f494"

def main():
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_testnet.json")
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)
    account = accounts.load(config["account"])
    contract = project.DebtAllocator.deploy(CAIRO_VERIFIER, CAIRO_PROGRAM_HASH, sender=account, max_priority_fee="0.5 gwei")
    project.track_deployment(contract)
