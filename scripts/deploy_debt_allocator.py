from ape import accounts, project
import json
import os
from dotenv import load_dotenv

def main():
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_testnet.json")
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)
    CAIRO_PROGRAM_HASH = config["cairo_program_hash"]
    CAIRO_VERIFIER = config["verifier_address"]
    VAULT_ADDRESS = config["vault_address"]

    load_dotenv()
    account = accounts.load(os.environ["ACCOUNT_ALIAS"])

    contract = project.DebtAllocator.deploy(CAIRO_VERIFIER, CAIRO_PROGRAM_HASH, VAULT_ADDRESS, sender=account, max_priority_fee="1 gwei")
    project.track_deployment(contract)
    
