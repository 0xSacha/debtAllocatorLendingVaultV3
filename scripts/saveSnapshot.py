import click
from ape.cli import network_option, NetworkBoundCommand
from ape import accounts, project
import json


def main():
    account = accounts.load("sacha")
    contract = project.DebtAllocator.at("0x11Bff0E8f8cAe5b5E697EABCbaa379787DfdBC83")
    tx = contract.saveSnapshot(sender=account)
    logs = list(tx.decode_logs(contract.NewSnapshot))
    print(logs)
    



