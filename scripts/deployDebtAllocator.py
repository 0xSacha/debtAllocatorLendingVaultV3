from brownie import DebtAllocator, accounts

CAIRO_VERIFIER = "0xAB43bA48c9edF4C2C4bB01237348D1D7B28ef168"
CAIRO_PROGRAM_HASH = "0x3cc4ec7f67570d17a6a16240289f85340ac752ec9f39aea1362dae5c06d5f1f"

def main():
    acct = accounts.load('sach')
    DebtAllocator.deploy(CAIRO_VERIFIER, CAIRO_PROGRAM_HASH, {'from': acct})

    