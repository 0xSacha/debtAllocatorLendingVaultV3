from brownie import DebtAllocator, accounts

CAIRO_VERIFIER = "0x47312450B3Ac8b5b8e247a6bB6d523e7605bDb60"
CAIRO_PROGRAM_HASH = "0x00bfd3c17a344350521b3f4c254de74e98ef52cbb2a305be36c72f8af8b6b282"

def main():
    acct = accounts.load('sa')
    DebtAllocator.deploy(CAIRO_VERIFIER, CAIRO_PROGRAM_HASH, {'from': acct})