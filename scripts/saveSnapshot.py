from brownie import DebtAllocator, accounts

def main():
    acct = accounts.load('sach')
    tx = DebtAllocator[1].saveSnapshot( {'from': acct})
    print(tx.events)
