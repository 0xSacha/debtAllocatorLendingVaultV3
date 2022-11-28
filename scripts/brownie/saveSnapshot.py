from brownie import DebtAllocator, accounts

def main():
    acct = accounts.load('sach')
    tx = DebtAllocator[0].saveSnapshot( {'from': acct})
    print(tx.events)
