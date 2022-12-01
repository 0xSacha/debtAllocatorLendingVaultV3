import click
from ape.cli import network_option, NetworkBoundCommand
from ape import accounts, project
import json


def main():
    account = accounts.load("sach")
    contract = project.DebtAllocator.at("0xDcAA40F17cEce7c7aB9c37E6e54754aA6985DEe1")
    tx = contract.saveSnapshot(sender=account)
    logs = list(tx.decode_logs(contract.NewSnapshot))
    print(logs)
    



