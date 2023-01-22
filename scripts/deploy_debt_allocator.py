from ape import accounts, project, chain
import json
import os
from dotenv import load_dotenv

def _load_config(config_file):
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), config_file)
    with open(CONFIG_PATH, "r") as file:
        config = json.load(file)
    return config

def _save_debt_allocator_address(config_file, config, address):
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), config_file)
    config["debt_allocator_address"] = address
    with open(CONFIG_PATH, "w") as file:
        json.dump(config, file)
    return config

def main():
    load_dotenv()
    account = accounts.load(os.environ["ACCOUNT_ALIAS"])
    config = _load_config("config_mainnet.json")
    CAIRO_PROGRAM_HASH = config["cairo_program_hash"]
    CAIRO_VERIFIER = config["verifier_address"]
    VAULT_ADDRESS = config["vault_address"]

    print("ChainID", chain.chain_id)

    debt_allocator = project.DebtAllocator.deploy(
        CAIRO_VERIFIER,
        CAIRO_PROGRAM_HASH,
        VAULT_ADDRESS,
        sender=account,
        max_priority_fee="1 gwei",
    )
    
    _save_debt_allocator_address("config_mainnet.json", config, str(debt_allocator))

    project.track_deployment(debt_allocator)
