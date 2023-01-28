from ape import accounts, project
import json
import os
from dotenv import load_dotenv


def main():
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_testnet.json")
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)

    AAVE_STRAT = config["strategy_aave_address"]
    COMPOUND2_STRAT = config["strategy_compound_address"]
    COMPOUND3_STRAT = config["strategy_compound_v3_address"]

    load_dotenv()
    account = accounts.load(os.environ["ACCOUNT_ALIAS"])

    contract = project.MockVault.deploy(sender=account, max_priority_fee="1 gwei")
    project.track_deployment(contract)
    contract.addStrategy(AAVE_STRAT, (0, 0, 1000000000, 0), sender=account)
    contract.addStrategy(COMPOUND2_STRAT, (0, 0, 2000000000, 0), sender=account)
    contract.addStrategy(COMPOUND3_STRAT, (0, 0, 3000000000, 0), sender=account)
