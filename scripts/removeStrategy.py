from brownie import DebtAllocator, accounts

INDEX = 1 

def main():
    acct = accounts.load('sach')
    DebtAllocator[1].removeStrategy(INDEX, {'from': acct})
