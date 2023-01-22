from ape import accounts, project
import json
import os
from dotenv import load_dotenv


def main():
    # Load configuration files
    load_dotenv()
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_testnet.json")
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)

    account = accounts.load(os.environ["ACCOUNT_ALIAS"])
    debt_allocator = project.DebtAllocator.at(config["debt_allocator_address"])
    debt_allocator.updateCairoProgramHash(
        config["cairo_program_hash"], sender=account, max_priority_fee="1 gwei"
    )
