from ape import accounts, project
from typing import List, Optional
import json
import os
import time
import struct

BASE_TOKEN = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
cTOKEN = "0xc3d688B66703497DAA19211EEdff47f25384cdc3"

COMP_USD = "0xdbd020CAeF83eFd542f4De03e3cF0C28A4428bd5"
WANTED_TOKEN_USD = "0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6"


## totalSupply()
CONTRACT_ADDRESS_0 = cTOKEN
## 0x18160ddd (selector from totalSupply()
CHECKDATA_0 = "0x18160ddd"
STRATEGYY_OFFSET_0 = 0

## totalBorrow()
CONTRACT_ADDRESS_1 = cTOKEN
## 0x8285ef40 (selector from totalBorrow()) 
CHECKDATA_1 = "0x8285ef40"
STRATEGYY_OFFSET_1 = 0

## supplyPerSecondInterestRateBase() Rslop 0
CONTRACT_ADDRESS_2 = cTOKEN
## 0x94920cca (selector from supplyPerSecondInterestRateBase() ) 
CHECKDATA_2 = "0x94920cca"
STRATEGYY_OFFSET_2 = 0

## supplyPerSecondInterestRateSlopeLow() Rslop 1
CONTRACT_ADDRESS_3 = cTOKEN
## 0x5a94b8d1 (selector from supplyPerSecondInterestRateSlopeLow() ) 
CHECKDATA_3 = "0x5a94b8d1"
STRATEGYY_OFFSET_3 = 0

## supplyPerSecondInterestRateSlopeHigh() Rslop 2
CONTRACT_ADDRESS_4 = cTOKEN
## 0x804de71f (selector from supplyPerSecondInterestRateSlopeHigh() ) 
CHECKDATA_4 = "0x804de71f"
STRATEGYY_OFFSET_4 = 0

## supplyKink() Uo
CONTRACT_ADDRESS_5 = cTOKEN
## 0xa5b4ff79 (selector from supplyKink() ) 
CHECKDATA_5 = "0xa5b4ff79"
STRATEGYY_OFFSET_5 = 0

##baseTrackingSupplySpeed()
CONTRACT_ADDRESS_6 = cTOKEN
## 0x189bb2f1 (selector from baseTrackingSupplySpeed() ) 
CHECKDATA_6 = "0x189bb2f1"
STRATEGYY_OFFSET_6 = 0

## baseScale()
CONTRACT_ADDRESS_7 = cTOKEN
## 0x44c1e5eb (selector from baseScale() ) 
CHECKDATA_7 = "0x44c1e5eb"
STRATEGYY_OFFSET_7 = 0

## PriceFEED

##latestAnswer()
CONTRACT_ADDRESS_8 = COMP_USD
## 0x50d25bcd (selector from latestAnswer() ) 
CHECKDATA_8 = "0x50d25bcd"
STRATEGYY_OFFSET_8 = 0

##decimals()
CONTRACT_ADDRESS_9 = COMP_USD
## 0x313ce567 (selector from decimals() ) 
CHECKDATA_9 = "0x313ce567"
STRATEGYY_OFFSET_9 = 0

##latestAnswer()
CONTRACT_ADDRESS_10 = WANTED_TOKEN_USD
## 0x50d25bcd (selector from latestAnswer() ) 
CHECKDATA_10 = "0x50d25bcd"
STRATEGYY_OFFSET_10 = 0

##decimals()
CONTRACT_ADDRESS_11 = WANTED_TOKEN_USD
## 0x313ce567 (selector from decimals() ) 
CHECKDATA_11 = "0x313ce567"
STRATEGYY_OFFSET_11 = 0

##decimals()
CONTRACT_ADDRESS_12 = BASE_TOKEN
## 0x313ce567 (selector from decimals() ) 
CHECKDATA_12 = "0x313ce567"
STRATEGYY_OFFSET_12 = 0



# contracts to get data from
STRATEGY_CONTRACTS = [CONTRACT_ADDRESS_0, CONTRACT_ADDRESS_1, CONTRACT_ADDRESS_2, CONTRACT_ADDRESS_3, CONTRACT_ADDRESS_4, CONTRACT_ADDRESS_5, CONTRACT_ADDRESS_6, CONTRACT_ADDRESS_7, CONTRACT_ADDRESS_8, CONTRACT_ADDRESS_9, CONTRACT_ADDRESS_10, CONTRACT_ADDRESS_11, CONTRACT_ADDRESS_12]

# checkdata (selector + neccessary args bytes32)
STRATEGYY_CHECKDATA = [CHECKDATA_0, CHECKDATA_1, CHECKDATA_2, CHECKDATA_3, CHECKDATA_4, CHECKDATA_5, CHECKDATA_6, CHECKDATA_7, CHECKDATA_8, CHECKDATA_9, CHECKDATA_10, CHECKDATA_11, CHECKDATA_12]

# offset, which args we need from the data received from the call, 0 by default
STRATEGYY_OFFSET = [STRATEGYY_OFFSET_0, STRATEGYY_OFFSET_1, STRATEGYY_OFFSET_2, STRATEGYY_OFFSET_3, STRATEGYY_OFFSET_4, STRATEGYY_OFFSET_5, STRATEGYY_OFFSET_6, STRATEGYY_OFFSET_7, STRATEGYY_OFFSET_8, STRATEGYY_OFFSET_9, STRATEGYY_OFFSET_10, STRATEGYY_OFFSET_11, STRATEGYY_OFFSET_12]


STRATEGYY_CALCULATION = [0, 0, 5, 1, 1000000000000020000, 2, 10001, 10000, 3, 5, 3, 2, 10003, 1000000000000020000, 3, 10004, 2, 0, 10002, 5, 1, 10006, 4, 2, 10007, 1000000000000020000, 3, 10008, 10005, 0,
10009, 31556000, 2, 8, 6, 2, 12, 11, 2, 31556000, 1000000000000020000, 2, 10010, 10011, 2, 10013, 10012, 2, 9, 7, 2, 10000, 10, 2, 10015, 10016, 2, 10014, 10017, 3, 10010, 10018, 0, 10019, 1000020000, 2,
0, 0, 5, 1, 1000000000000020000, 2, 10001, 10000, 3, 10002, 3, 2, 10003, 1000000000000020000, 3, 10004, 2, 0, 10005, 31556000, 2, 8, 6, 2, 12, 11, 2, 31556000, 1000000000000020000, 2,
10007, 10008, 2, 10010, 10009, 2, 9, 7, 2, 10000, 10, 2, 10012, 10013, 2, 10011, 10014, 3, 10006, 10015, 0, 10016, 1000020000, 2]
CALCULATION_CONDITION = [0, 0, 5, 1, 1000000000000020000, 2, 10001, 10000, 3, 10002, 5, 22, 18]


def main():
    f = open("./scripts/config_mainnet.json")
    config_dict = json.load(f)
    f.close()
    
    account = accounts.load(config_dict["account"])
    contract = project.testStrategyData.at(config_dict["data_strat_test"])
    
    contract.getStrategiesData(STRATEGY_CONTRACTS, STRATEGYY_CHECKDATA, STRATEGYY_OFFSET,sender=account)
    data = []
    for i in range(13):
        result = contract.dataSaved(i)
        data.append(result)
    print(data)
 
## Compound V3 : [168482027497752, 76823946090320, 0, 1030568239, 12683916793, 800000000000000000, 0, 1000000, 3606000000, 8, 99994853, 8, 6]