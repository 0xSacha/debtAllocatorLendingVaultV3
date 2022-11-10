from brownie import DebtAllocator, accounts


## Supply rate = Ut * (SBt*St + VBt*Vt) * (1 - Rt)
# Ut, the utilisation ratio
# SBt, the share of stable borrows
# St, the average stable rate
# VBt, the share of variable borrows
# Vt, the variable rate
# Rt, the reserve factor

# average stable rate St = R0 + (Ut/Uo)* R1 if Ut < Uo, R0 + R1 + (Ut - Uo)/ (1 - Uo)R2s else
# R0, Base Variable Borrow Rate
# R1, stable Rate Slope 1
# R2, stable Rate Slope 2
# R2, stable Rate Slope 2
# Uo, optimal utilization rate

# average variable rate Vt = R0 + (Ut/Uo)* R1 if Ut < Uo, R0 + R1 + (Ut - Uo)/ (1 - Uo)R2v else
# R0, Base Variable Borrow Rate
# R1, Variable Rate Slope 1
# R2, Variable Rate Slope 2
# R2, Variable Rate Slope 2
# Uo, optimal utilization rate

## Ut = available liquidity / (available liquidity + stable debt + variable debt)
## Sbt = stable debt / (stable debt + variable debt)
## VBt = variable debt / (stable debt + variable debt)

## Head to https://docs.aave.com/developers/v/2.0/deployed-contracts/deployed-contracts, get the protocol data provider address and call getReserveConfigurationData(address)  providing the token address, and get the reserveFactor (5th from the tupple), 
## In the same conract call getReserveData(address) providing the token address and get: available liquidity (first), totalStableDebt (second), totalVariableDebt (third)

## Head to https://docs.aave.com/developers/v/2.0/deployed-contracts/deployed-contracts, get the lending pool address, call  getReserveData(address) providing the token address, and get the ReserveInterestRateStrategy adress
## (penultimate data from the returned tupple). From this contract, you'll have access to variableRateSlope1, variableRateSlope2, baseVariableBorrowRate, OPTIMAL_UTILIZATION_RATE, stableRateSlope1 and stableRateSlope2


## The following data is valid for Goerli, with WETH ASSET
WETH = "0xCCa7d1416518D095E729904aAeA087dBA749A4dC"
PROTOCOL_DATA_PROVIDER = "0x927F584d4321C1dCcBf5e2902368124b02419a1E"
RESERVE_INTEREST_RATE_STRATEGY= "0x5ecE040038c822d7228F24D9F2e1Fd41bc77A3c4"

## Reserve Data
CONTRACT_ADDRESS_0 = PROTOCOL_DATA_PROVIDER
## 0x3e150141 (selector from getReserveConfigurationData(address)) + 000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC wethadress to byte32
CHECKDATA_0 = "0x3e150141000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC"
## 5th arg so (5-1)*32 
STRATEGYY_OFFSET_0 = 128

## Available Liquidity
CONTRACT_ADDRESS_1 = PROTOCOL_DATA_PROVIDER
## 0x35ea6a75 (selector from getReserveData(address)) + 000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC wethadress to byte32
CHECKDATA_1 = "0x35ea6a75000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC"
## first arg so 0
STRATEGYY_OFFSET_1 = 0

## totalStableDebt 
CONTRACT_ADDRESS_2 = PROTOCOL_DATA_PROVIDER
## 0x35ea6a75 (selector from getReserveData(address)) + 000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC wethadress to byte32
CHECKDATA_2 = "0x35ea6a75000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC"
## second arg so 32
STRATEGYY_OFFSET_2 = 32

## totalVariableDebt 
CONTRACT_ADDRESS_3 = PROTOCOL_DATA_PROVIDER
## 0x35ea6a75 (selector from getReserveData(address)) + 000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC wethadress to byte32
CHECKDATA_3 = "0x35ea6a75000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC"
## third arg so 64
STRATEGYY_OFFSET_3 = 64

## totalVariableDebt 
CONTRACT_ADDRESS_4 = RESERVE_INTEREST_RATE_STRATEGY
## 0x35ea6a75 (selector from OPTIMAL_UTILIZATION_RATE() ) 
CHECKDATA_4 = "0xa15f30ac"
STRATEGYY_OFFSET_4 = 0

CONTRACT_ADDRESS_5 = RESERVE_INTEREST_RATE_STRATEGY
## 0x0bdf953f (selector from stableRateSlope1() ) 
CHECKDATA_5 = "0x0bdf953f"
STRATEGYY_OFFSET_5 = 0

CONTRACT_ADDRESS_6 = RESERVE_INTEREST_RATE_STRATEGY
## 0xccab01a3 (selector from stableRateSlope2() ) 
CHECKDATA_6 = "0xccab01a3"
STRATEGYY_OFFSET_6 = 0

CONTRACT_ADDRESS_7 = RESERVE_INTEREST_RATE_STRATEGY
## 0x7b832f58 (selector from variableRateSlope1() ) 
CHECKDATA_7 = "0x7b832f58"
STRATEGYY_OFFSET_7 = 0

CONTRACT_ADDRESS_8 = RESERVE_INTEREST_RATE_STRATEGY
## 0x65614f81 (selector from variableRateSlope2() ) 
CHECKDATA_8 = "0x65614f81"
STRATEGYY_OFFSET_8 = 0

CONTRACT_ADDRESS_9 = RESERVE_INTEREST_RATE_STRATEGY
## 0xb2589544 (selector from baseVariableBorrowRate() ) 
CHECKDATA_9 = "0xb2589544"
STRATEGYY_OFFSET_9 = 0


# concerned strategy address
STRATEGY_ADDRESS= "0x76aFA2b6C29E1B277A3BB1CD320b2756c1674c91" 

MAX_STRATEGY_DEBT_RATIO = 10000

# contracts to get data from
STRATEGY_CONTRACTS = [CONTRACT_ADDRESS_0, CONTRACT_ADDRESS_1, CONTRACT_ADDRESS_2, CONTRACT_ADDRESS_3, CONTRACT_ADDRESS_4, CONTRACT_ADDRESS_5, CONTRACT_ADDRESS_6, CONTRACT_ADDRESS_7, CONTRACT_ADDRESS_8, CONTRACT_ADDRESS_9]

# checkdata (selector + neccessary args bytes32)
STRATEGYY_CHECKDATA = [CHECKDATA_0, CHECKDATA_1, CHECKDATA_2, CHECKDATA_3, CHECKDATA_4, CHECKDATA_5, CHECKDATA_6, CHECKDATA_7, CHECKDATA_8, CHECKDATA_9]

# offset, which args we need from the data received from the call, 0 by default
STRATEGYY_OFFSET = [STRATEGYY_OFFSET_0, STRATEGYY_OFFSET_1, STRATEGYY_OFFSET_2, STRATEGYY_OFFSET_3, STRATEGYY_OFFSET_4, STRATEGYY_OFFSET_5, STRATEGYY_OFFSET_6, STRATEGYY_OFFSET_7, STRATEGYY_OFFSET_8, STRATEGYY_OFFSET_9]


STRATEGYY_CALCULATION = []

CALCULATION_CONDITION = []


def main():
    acct = accounts.load('sa')
    DebtAllocator[0].addStrategy(STRATEGY_ADDRESS, MAX_STRATEGY_DEBT_RATIO, STRATEGY_CONTRACTS, STRATEGYY_CHECKDATA, STRATEGYY_OFFSET, STRATEGYY_CALCULATION, CALCULATION_CONDITION,{'from': acct})
