from brownie import DebtAllocator, accounts

PROGRAM_OUTPUT = 115792089237316195423570985008687907853269984665640564039457584007913129639935

def main():
    acct = accounts.load('sach')
    DebtAllocator[0].verifySolution(PROGRAM_OUTPUT {'from': acct})
