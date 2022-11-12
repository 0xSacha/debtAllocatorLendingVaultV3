from brownie import testCall, accounts

def main():
    acct = accounts.load('sach')
    testCall.deploy({'from': acct})


