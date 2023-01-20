from ape import accounts, project
import json
import os
from dotenv import load_dotenv

BASE_TOKEN = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
cTOKEN = "0xc3d688B66703497DAA19211EEdff47f25384cdc3"

COMP_USD = "0xdbd020CAeF83eFd542f4De03e3cF0C28A4428bd5"
WANTED_TOKEN_USD = "0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6"


## totalSupply()
CONTRACT_ADDRESS_0 = cTOKEN
## 0x18160ddd (selector from totalSupply()
SELECTOR_0 = "0x18160ddd"
CALLDATA_0 = []

STRATEGYY_OFFSET_0 = 0

## totalBorrow()
CONTRACT_ADDRESS_1 = cTOKEN
## 0x8285ef40 (selector from totalBorrow()) 
SELECTOR_1 = "0x8285ef40"
CALLDATA_1 = []

STRATEGYY_OFFSET_1 = 0

## supplyPerSecondInterestRateBase() Rslop 0
CONTRACT_ADDRESS_2 = cTOKEN
## 0x94920cca (selector from supplyPerSecondInterestRateBase() ) 
SELECTOR_2 = "0x94920cca"
CALLDATA_2 = []

STRATEGYY_OFFSET_2 = 0

## supplyPerSecondInterestRateSlopeLow() Rslop 1
CONTRACT_ADDRESS_3 = cTOKEN
## 0x5a94b8d1 (selector from supplyPerSecondInterestRateSlopeLow() ) 
SELECTOR_3 = "0x5a94b8d1"
CALLDATA_3 = []

STRATEGYY_OFFSET_3 = 0

## supplyPerSecondInterestRateSlopeHigh() Rslop 2
CONTRACT_ADDRESS_4 = cTOKEN
## 0x804de71f (selector from supplyPerSecondInterestRateSlopeHigh() ) 
SELECTOR_4 = "0x804de71f"
CALLDATA_4 = []
STRATEGYY_OFFSET_4 = 0

## supplyKink() Uo
CONTRACT_ADDRESS_5 = cTOKEN
## 0xa5b4ff79 (selector from supplyKink() ) 
SELECTOR_5 = "0xa5b4ff79"
CALLDATA_5 = []
STRATEGYY_OFFSET_5 = 0

##baseTrackingSupplySpeed()
CONTRACT_ADDRESS_6 = cTOKEN
## 0x189bb2f1 (selector from baseTrackingSupplySpeed() ) 
SELECTOR_6 = "0x189bb2f1"
CALLDATA_6 = []
STRATEGYY_OFFSET_6 = 0

## baseScale()
CONTRACT_ADDRESS_7 = cTOKEN
## 0x44c1e5eb (selector from baseScale() ) 
SELECTOR_7 = "0x44c1e5eb"
CALLDATA_7 = []
STRATEGYY_OFFSET_7 = 0

## PriceFEED

##latestAnswer()
CONTRACT_ADDRESS_8 = COMP_USD
## 0x50d25bcd (selector from latestAnswer() ) 
SELECTOR_8 = "0x50d25bcd"
CALLDATA_8 = []
STRATEGYY_OFFSET_8 = 0

##decimals()
CONTRACT_ADDRESS_9 = COMP_USD
## 0x313ce567 (selector from decimals() ) 
SELECTOR_9 = "0x313ce567"
CALLDATA_9 = []
STRATEGYY_OFFSET_9 = 0

##latestAnswer()
CONTRACT_ADDRESS_10 = WANTED_TOKEN_USD
## 0x50d25bcd (selector from latestAnswer() ) 
SELECTOR_10 = "0x50d25bcd"
CALLDATA_10 = []
STRATEGYY_OFFSET_10 = 0

##decimals()
CONTRACT_ADDRESS_11 = WANTED_TOKEN_USD
## 0x313ce567 (selector from decimals() ) 
SELECTOR_11 = "0x313ce567"
CALLDATA_11 = []
STRATEGYY_OFFSET_11 = 0

##decimals()
CONTRACT_ADDRESS_12 = BASE_TOKEN
## 0x313ce567 (selector from decimals() ) 
SELECTOR_12 = "0x313ce567"
CALLDATA_12 = []
STRATEGYY_OFFSET_12 = 0



# contracts to get data from
COMPOUND_STRATEGY_CONTRACTS = [CONTRACT_ADDRESS_0, CONTRACT_ADDRESS_1, CONTRACT_ADDRESS_2, CONTRACT_ADDRESS_3, CONTRACT_ADDRESS_4, CONTRACT_ADDRESS_5, CONTRACT_ADDRESS_6, CONTRACT_ADDRESS_7, CONTRACT_ADDRESS_8, CONTRACT_ADDRESS_9, CONTRACT_ADDRESS_10, CONTRACT_ADDRESS_11, CONTRACT_ADDRESS_12]

# selector 
COMPOUND_STRATEGYY_SELECTOR = [SELECTOR_0, SELECTOR_1, SELECTOR_2, SELECTOR_3, SELECTOR_4, SELECTOR_5, SELECTOR_6, SELECTOR_7, SELECTOR_8, SELECTOR_9, SELECTOR_10, SELECTOR_11, SELECTOR_12]
COMPOUND_STRATEGYY_CALLDATA = [CALLDATA_0, CALLDATA_1, CALLDATA_2, CALLDATA_3, CALLDATA_4, CALLDATA_5, CALLDATA_6, CALLDATA_7, CALLDATA_8, CALLDATA_9, CALLDATA_10, CALLDATA_11, CALLDATA_12]

# offset, which args we need from the data received from the call, 0 by default
COMPOUND_STRATEGYY_OFFSET = [STRATEGYY_OFFSET_0, STRATEGYY_OFFSET_1, STRATEGYY_OFFSET_2, STRATEGYY_OFFSET_3, STRATEGYY_OFFSET_4, STRATEGYY_OFFSET_5, STRATEGYY_OFFSET_6, STRATEGYY_OFFSET_7, STRATEGYY_OFFSET_8, STRATEGYY_OFFSET_9, STRATEGYY_OFFSET_10, STRATEGYY_OFFSET_11, STRATEGYY_OFFSET_12]

COMPOUND_STRATEGYY_CALCULATION = [0, 0, 5, 1, 1000000000000020000, 2, 10001, 10000, 3, 5, 3, 2, 10003, 1000000000000020000, 3, 10004, 2, 0, 10002, 5, 1, 10006, 4, 2, 10007, 1000000000000020000, 3, 10008, 10005, 0,
10009, 31556000, 2, 8, 6, 2, 12, 11, 2, 31556000, 1000000000000020000, 2, 10010, 10011, 2, 10013, 10012, 2, 9, 7, 2, 10000, 10, 2, 10015, 10016, 2, 10014, 10017, 3, 10010, 10018, 0, 10019, 1000020000, 2,
0, 0, 5, 1, 1000000000000020000, 2, 10001, 10000, 3, 10002, 3, 2, 10003, 1000000000000020000, 3, 10004, 2, 0, 10005, 31556000, 2, 8, 6, 2, 12, 11, 2, 31556000, 1000000000000020000, 2,
10007, 10008, 2, 10010, 10009, 2, 9, 7, 2, 10000, 10, 2, 10012, 10013, 2, 10011, 10014, 3, 10006, 10015, 0, 10016, 1000020000, 2]
COMPOUND_CALCULATION_CONDITION = [0, 0, 5, 1, 1000000000000020000, 2, 10001, 10000, 3, 10002, 5, 22, 18]


def main():
    load_dotenv()
    f = open("./scripts/config_mainnet.json")
    config_dict = json.load(f)
    f.close()
    f = open("./scripts/strategies_info.json")
    strategies_info = json.load(f)
    f.close()

    account = accounts.load(os.environ["ACCOUNT_ALIAS"])
    contract = project.DebtAllocator.at(config_dict["debt_allocator_address"])
    compound_strategy_v3 = config_dict["strategy_compound_v3_address"]

    addresses = strategies_info["addresses"]
    callLen = strategies_info["callLen"]
    contracts = strategies_info["contracts"]
    selectors = strategies_info["selectors"]
    callData = strategies_info["callData"]
    offset = strategies_info["offset"]
    calculationsLen = strategies_info["calculationsLen"]
    calculations = strategies_info["calculations"]
    conditionsLen = strategies_info["conditionsLen"]
    conditions = strategies_info["conditions"]

    contract.addStrategy((addresses, callLen, contracts, selectors, callData, offset, calculationsLen, calculations, conditionsLen, conditions), compound_strategy, (int(len(COMPOUND_STRATEGY_CONTRACTS)), COMPOUND_STRATEGY_CONTRACTS, COMPOUND_STRATEGYY_SELECTORS, COMPOUND_STRATEGYY_CALLDATA, COMPOUND_STRATEGYY_OFFSET, int(len(COMPOUND_STRATEGYY_CALCULATION)), COMPOUND_STRATEGYY_CALCULATION, int(len(COMPOUND_CALCULATION_CONDITION)), COMPOUND_CALCULATION_CONDITION),sender=account, max_priority_fee="1 gwei")
    print("✅ Success")
 
