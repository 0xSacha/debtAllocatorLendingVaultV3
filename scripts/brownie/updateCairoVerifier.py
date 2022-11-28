from brownie import DebtAllocator, accounts

CAIRO_VERIFIER = "0xAB43bA48c9edF4C2C4bB01237348D1D7B28ef168"

def main():
    acct = accounts.load('sach')
    tx = DebtAllocator[1].updateCairoVerifier(CAIRO_VERIFIER, {'from': acct})
    print(tx.events)
