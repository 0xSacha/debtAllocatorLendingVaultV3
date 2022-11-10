from brownie import DebtAllocator, accounts

def main():
    acct = accounts.load('sach')
    DebtAllocator[0].saveSnapshot({'from': acct})
