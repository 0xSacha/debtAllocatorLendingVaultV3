import click
from ape.cli import network_option, NetworkBoundCommand
from ape import accounts, project
import json


def main():
    account = accounts.load("sacha")
    contract = project.DebtAllocator.at("0xa6cf8E6eBF43d69E0c20d8E8a3c66dfb5B384C6B")
    tx = contract.strategies(1,sender=account)
    print (tx)
    



