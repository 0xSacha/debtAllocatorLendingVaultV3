from brownie import DebtAllocator, accounts

def main():
    tx = DebtAllocator[1].strategies.call(1)
    print(tx)

    tx = DebtAllocator[1].getStrategiesData.call()
    print(tx)

# 0x76aFA2b6C29E1B277A3BB1CD320b2756c1674c91
# 0x76AFa2B8c29e1B277a3bb1cd320B2756C1674C91
