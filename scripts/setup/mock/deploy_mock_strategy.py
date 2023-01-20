import click
from ape.cli import network_option, NetworkBoundCommand
from ape import accounts, project
import json

def run():
    f = open("./scripts/config_testnet.json")
    config_dict = json.load(f)
    f.close()
    account = accounts.load(config_dict["account"])
    contract = project.MockStrategy.deploy(sender=account)
    project.track_deployment(contract)
    # contract = project.MockStrategy2.deploy(sender=account)
    # project.track_deployment(contract)
