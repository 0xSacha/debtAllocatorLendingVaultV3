from ape import accounts, project
import json
import os



def main():
    VAULT_ADDRESS = ""
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_mainnet.json")
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)
    
    CAIRO_PROGRAM_HASH = config["cairo_program_hash"]
    CAIRO_VERIFIER = config["verifier_address"]

    account = accounts.load(config["account"])
    contract = project.DebtAllocator.deploy(CAIRO_VERIFIER, CAIRO_PROGRAM_HASH, VAULT_ADDRESS, sender=account, max_priority_fee="1 gwei")
    project.track_deployment(contract)
    
