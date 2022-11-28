from brownie import DebtAllocator, accounts
from brownie import network

PROGRAM_OUTPUT = [5354402413859133050145535969184521950, 6506010381989009378723109868625281994, 1, 0, 1, 10000, 0, 179398891682468167705637]

def main():
    acct = accounts.load('sach')
    tx = DebtAllocator[0].verifySolution(PROGRAM_OUTPUT, {'from': acct})
    print(tx.events)
