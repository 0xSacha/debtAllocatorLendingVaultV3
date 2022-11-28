import click
from ape.cli import network_option, NetworkBoundCommand
from ape import accounts, project


def main():
    print("Hello world!")
    account = accounts.load("sacha")
    contract = project.DebtAllocator.at("0x9C1b710e3D2Af3B26E27467cEeb3369807fC582d")
    tx = contract.saveSnapshot(sender=account)
    logs = list(tx.decode_logs(contract.NewSnapshot))
    print(logs)
    # assert logs == 787



