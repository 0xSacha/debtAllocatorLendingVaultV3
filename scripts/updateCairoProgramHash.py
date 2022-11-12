from brownie import DebtAllocator, accounts

PROGRAM_HASH = "0x3cc4ec7f67570d17a6a16240289f85340ac752ec9f39aea1362dae5c06d5f1f"

def main():
    acct = accounts.load('sach')
    DebtAllocator[0].updateCairoProgramHash(PROGRAM_HASH, {'from': acct})
