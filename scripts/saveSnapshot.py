import click
from ape.cli import network_option, NetworkBoundCommand
from ape import accounts, project
import json


def main():
    account = accounts.load("sach")
    contract = project.DebtAllocator.at("0x8aD42486109e5Ec080eFe015830d2c9B806631d0")
    tx = contract.saveSnapshot(sender=account)
    logs = list(tx.decode_logs(contract.NewSnapshot))
    print(logs)
    



