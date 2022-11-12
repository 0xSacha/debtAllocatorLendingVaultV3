from brownie import DebtAllocator, accounts

PROGRAM_HASH = "0x18261fedf8bb9295db94450fdda4343f1b04d3ae08f198d079a0e178596f494"

def main():
    acct = accounts.load('sach')
    DebtAllocator[0].updateCairoProgramHash(PROGRAM_HASH, {'from': acct})
