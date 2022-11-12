from brownie import testCall, accounts

cETH = "0x64078a6189Bf45f80091c6Ff2fCEe1B15Ac8dbde"
INTEREST_RATE_CETH = "0xB24D5c2F5d881689C14F69Dd4a7118C89747D403"

## getCash
CONTRACT_ADDRESS_0 = cETH
## 0x3b1d21a2 (selector from getCash())
CHECKDATA_0 = "0x3b1d21a2"
STRATEGYY_OFFSET_0 = 0

## totalBorrows()
CONTRACT_ADDRESS_1 = cETH
## 0x47bd3718 (selector from totalBorrows()) 
CHECKDATA_1 = "0x47bd3718"
STRATEGYY_OFFSET_1 = 0

## totalReserves() 
CONTRACT_ADDRESS_2 = cETH
## 0x8f840ddd (selector from totalReserves())
CHECKDATA_2 = "0x8f840ddd"
STRATEGYY_OFFSET_2 = 0

## reserveFactorMantissa() 
CONTRACT_ADDRESS_3 = cETH
## 0x173b9904 (selector from reserveFactorMantissa()) 
CHECKDATA_3 = "0x173b9904"
STRATEGYY_OFFSET_3 = 0

## Optimal utilization rate  
CONTRACT_ADDRESS_4 = INTEREST_RATE_CETH
## 0x35ea6a75 (selector from kink() ) 
CHECKDATA_4 = "0xfd2da339"
STRATEGYY_OFFSET_4 = 0

## multiplierPerBlock R1
CONTRACT_ADDRESS_5 = INTEREST_RATE_CETH
## 0x8726bb89 (selector from multiplierPerBlock() ) 
CHECKDATA_5 = "0x8726bb89"
STRATEGYY_OFFSET_5 = 0

## jumpMultiplierPerBlock R2
CONTRACT_ADDRESS_6 = INTEREST_RATE_CETH
## 0xb9f9850a (selector from jumpMultiplierPerBlock() ) 
CHECKDATA_6 = "0xb9f9850a"
STRATEGYY_OFFSET_6 = 0

## baseRatePerBlock R0
CONTRACT_ADDRESS_7 = INTEREST_RATE_CETH
## 0xf14039de (selector from baseRatePerBlock() ) 
CHECKDATA_7 = "0xf14039de"
STRATEGYY_OFFSET_7 = 0


def main():
    acct = accounts.load('sach')
    tx = testCall[0].getStrategiesData(CONTRACT_ADDRESS_1, CHECKDATA_1, STRATEGYY_OFFSET_1, {'from': acct})
    print("yo")
    tx = testCall[0].getStrategiesData(CONTRACT_ADDRESS_2, CHECKDATA_2, STRATEGYY_OFFSET_2, {'from': acct})
    print("yo")
    tx = testCall[0].getStrategiesData(CONTRACT_ADDRESS_3, CHECKDATA_3, STRATEGYY_OFFSET_3, {'from': acct})
    print("yo")
    tx = testCall[0].getStrategiesData(CONTRACT_ADDRESS_4, CHECKDATA_4, STRATEGYY_OFFSET_4, {'from': acct})
    print("yo")
    tx = testCall[0].getStrategiesData(CONTRACT_ADDRESS_5, CHECKDATA_5, STRATEGYY_OFFSET_5, {'from': acct})
    print("yo")
    tx = testCall[0].getStrategiesData(CONTRACT_ADDRESS_6, CHECKDATA_6, STRATEGYY_OFFSET_6, {'from': acct})
    print("yo")
    tx = testCall[0].getStrategiesData(CONTRACT_ADDRESS_7, CHECKDATA_7, STRATEGYY_OFFSET_7, {'from': acct})
    print("yo")
