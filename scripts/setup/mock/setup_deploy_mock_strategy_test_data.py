import click
from ape.cli import network_option, NetworkBoundCommand
from ape import accounts, project
import json


def main():
    f = open("./scripts/config_mainnet.json")
    config_dict = json.load(f)
    f.close()
    account = accounts.load(config_dict["account"])
    contract = project.testStrategyData.deploy(sender=account)
    project.track_deployment(contract)
