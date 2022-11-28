from brownie import DebtAllocator, accounts

CAIRO_VERIFIER = "0xAB43bA48c9edF4C2C4bB01237348D1D7B28ef168"
CAIRO_PROGRAM_HASH = "0x18261fedf8bb9295db94450fdda4343f1b04d3ae08f198d079a0e178596f494"

def main():
    acct = accounts.load('sach')
    DebtAllocator.deploy(CAIRO_VERIFIER, CAIRO_PROGRAM_HASH, {'from': acct})