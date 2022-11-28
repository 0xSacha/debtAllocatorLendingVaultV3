from brownie import DebtAllocator, accounts

CURRENT_DEBT = [0]
NEW_DEBT = [10000]



def main():
    tx = DebtAllocator[0].checkAllowedDebtRatio.call(CURRENT_DEBT, NEW_DEBT)
    print(tx)
