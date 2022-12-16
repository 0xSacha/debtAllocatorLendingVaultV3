from ape import accounts, project
from typing import List, Optional
import json
import os
import time
 

WANTED_TOKEN = "0x07865c6E87B9F70255377e024ace6630C1Eaa37F"
cTOKEN = "0x73506770799Eb04befb5AaE4734e58C2C624F493"
INTEREST_RATE_cTOKEN = "0xef5ae06093bdFc54Fbc804C7627B15dAE98Ca5e7"
Comptroller = "0x05Df6C772A563FfB37fD3E04C1A279Fb30228621"
COMP_USD = "0x0d79df66BE487753B02D015Fb622DED7f0E9798d"
WANTED_TOKEN_USD = "0xAb5c49580294Aff77670F839ea425f5b78ab3Ae7"
COMPOUND_CONTRACT_ADDRESS_0 = cTOKEN
COMPOUND_CHECKDATA_0 = "0x3b1d21a2"
COMPOUND_STRATEGYY_OFFSET_0 = 0
COMPOUND_CONTRACT_ADDRESS_1 = cTOKEN
COMPOUND_CHECKDATA_1 = "0x47bd3718"
COMPOUND_STRATEGYY_OFFSET_1 = 0
COMPOUND_CONTRACT_ADDRESS_2 = cTOKEN
COMPOUND_CHECKDATA_2 = "0x8f840ddd"
COMPOUND_STRATEGYY_OFFSET_2 = 0
COMPOUND_CONTRACT_ADDRESS_3 = cTOKEN
COMPOUND_CHECKDATA_3 = "0x173b9904"
COMPOUND_STRATEGYY_OFFSET_3 = 0
COMPOUND_CONTRACT_ADDRESS_4 = INTEREST_RATE_cTOKEN
COMPOUND_CHECKDATA_4 = "0xfd2da339"
COMPOUND_STRATEGYY_OFFSET_4 = 0
COMPOUND_CONTRACT_ADDRESS_5 = INTEREST_RATE_cTOKEN
COMPOUND_CHECKDATA_5 = "0x8726bb89"
COMPOUND_STRATEGYY_OFFSET_5 = 0
COMPOUND_CONTRACT_ADDRESS_6 = INTEREST_RATE_cTOKEN
COMPOUND_CHECKDATA_6 = "0xb9f9850a"
COMPOUND_STRATEGYY_OFFSET_6 = 0
COMPOUND_CONTRACT_ADDRESS_7 = INTEREST_RATE_cTOKEN
COMPOUND_CHECKDATA_7 = "0xf14039de"
COMPOUND_STRATEGYY_OFFSET_7 = 0
COMPOUND_CONTRACT_ADDRESS_8 = INTEREST_RATE_cTOKEN
COMPOUND_CHECKDATA_8 = "0xa385fb96"
COMPOUND_STRATEGYY_OFFSET_8 = 0
COMPOUND_CONTRACT_ADDRESS_9 = Comptroller
COMPOUND_CHECKDATA_9 = "0x6aa875b500000000000000000000000073506770799Eb04befb5AaE4734e58C2C624F493"
COMPOUND_STRATEGYY_OFFSET_9 = 0
COMPOUND_CONTRACT_ADDRESS_10 = COMP_USD
COMPOUND_CHECKDATA_10 = "0x50d25bcd"
COMPOUND_STRATEGYY_OFFSET_10 = 0
COMPOUND_CONTRACT_ADDRESS_11 = COMP_USD
COMPOUND_CHECKDATA_11 = "0x313ce567"
COMPOUND_STRATEGYY_OFFSET_11 = 0
COMPOUND_CONTRACT_ADDRESS_12 = WANTED_TOKEN_USD
COMPOUND_CHECKDATA_12 = "0x50d25bcd"
COMPOUND_STRATEGYY_OFFSET_12 = 0
COMPOUND_CONTRACT_ADDRESS_13 = WANTED_TOKEN_USD
COMPOUND_CHECKDATA_13 = "0x313ce567"
COMPOUND_STRATEGYY_OFFSET_13 = 0
COMPOUND_CONTRACT_ADDRESS_14 = WANTED_TOKEN
COMPOUND_CHECKDATA_14 = "0x313ce567"
COMPOUND_STRATEGYY_OFFSET_14 = 0
COMPOUND_STRATEGY_ADDRESS= "0x3468Ef8426530842F4044cbb1D0A2e175d88628F" 
COMPOUND_MAX_STRATEGY_DEBT_RATIO = 10000
COMPOUND_STRATEGY_CONTRACTS = [COMPOUND_CONTRACT_ADDRESS_0, COMPOUND_CONTRACT_ADDRESS_1, COMPOUND_CONTRACT_ADDRESS_2, COMPOUND_CONTRACT_ADDRESS_3, COMPOUND_CONTRACT_ADDRESS_4, COMPOUND_CONTRACT_ADDRESS_5, COMPOUND_CONTRACT_ADDRESS_6, COMPOUND_CONTRACT_ADDRESS_7, COMPOUND_CONTRACT_ADDRESS_8, COMPOUND_CONTRACT_ADDRESS_9, COMPOUND_CONTRACT_ADDRESS_10, COMPOUND_CONTRACT_ADDRESS_11, COMPOUND_CONTRACT_ADDRESS_12, COMPOUND_CONTRACT_ADDRESS_13, COMPOUND_CONTRACT_ADDRESS_14]
COMPOUND_STRATEGYY_CHECKDATA = [COMPOUND_CHECKDATA_0, COMPOUND_CHECKDATA_1, COMPOUND_CHECKDATA_2, COMPOUND_CHECKDATA_3, COMPOUND_CHECKDATA_4, COMPOUND_CHECKDATA_5, COMPOUND_CHECKDATA_6, COMPOUND_CHECKDATA_7, COMPOUND_CHECKDATA_8, COMPOUND_CHECKDATA_9, COMPOUND_CHECKDATA_10, COMPOUND_CHECKDATA_11, COMPOUND_CHECKDATA_12, COMPOUND_CHECKDATA_13, COMPOUND_CHECKDATA_14]
COMPOUND_STRATEGYY_OFFSET = [COMPOUND_STRATEGYY_OFFSET_0, COMPOUND_STRATEGYY_OFFSET_1, COMPOUND_STRATEGYY_OFFSET_2, COMPOUND_STRATEGYY_OFFSET_3, COMPOUND_STRATEGYY_OFFSET_4, COMPOUND_STRATEGYY_OFFSET_5, COMPOUND_STRATEGYY_OFFSET_6, COMPOUND_STRATEGYY_OFFSET_7, COMPOUND_STRATEGYY_OFFSET_8, COMPOUND_STRATEGYY_OFFSET_9, COMPOUND_STRATEGYY_OFFSET_10, COMPOUND_STRATEGYY_OFFSET_11, COMPOUND_STRATEGYY_OFFSET_12, COMPOUND_STRATEGYY_OFFSET_13, COMPOUND_STRATEGYY_OFFSET_14]
COMPOUND_STRATEGYY_CALCULATION = [0, 0, 5, 10000, 1, 0, 10001, 2, 1, 1, 1000000000000020000, 2, 10003, 10002, 3, 4, 5, 2, 10005, 1000000000000020000, 3, 10006, 7, 0, 10004, 4, 1, 10008, 6, 2, 10009, 1000000000000020000, 3, 10010, 10007, 0, 
1000000000000020000, 3, 1, 10011, 10012, 2, 10013, 1000000000000020000, 3, 10014, 10004, 2, 10015, 1000000000000020000, 3, 10016, 8, 2, 9, 8, 2, 20010, 14, 4, 10018, 10019, 2, 10020, 10002, 3, 10021, 10, 2, 20010, 11, 4, 10022, 10023, 3, 20010, 13, 4, 10024, 10025, 2,
10026, 12, 3, 10027, 10017, 0 , 10028, 1000020000, 2, 0, 0, 5, 10000, 1, 0, 10001, 2, 1, 1, 1000000000000020000, 2, 10003, 10002, 3, 10004, 5, 2, 10005, 1000000000000020000, 3,
10006, 7, 0, 1000000000000020000, 3, 1, 10008, 10007, 2, 10009, 1000000000000020000, 3, 10010, 10004, 2, 10011, 1000000000000020000, 3, 10012, 8, 2, 9, 8, 2, 20010, 14, 4, 10014, 10015, 2,
10016, 10002, 3, 10017, 10, 2, 20010, 11, 4, 10018, 10019, 3, 20010, 13, 4, 10020, 10021, 2, 10022, 12, 3, 10023, 10013, 0, 10024, 1000020000, 2]
COMPOUND_CALCULATION_CONDITION = [0, 0, 5, 10000, 1, 0, 10001, 2, 1, 1, 1000000000000020000, 2, 10003, 10002, 3, 10004, 4, 30, 26]


def main():
    f = open("./scripts/config_testnet.json")
    config_dict = json.load(f)
    f.close()
    f = open("./scripts/strategies_info.json")
    strategies_info = json.load(f)
    f.close()
    account = accounts.load(config_dict["account"])
    contract = project.DebtAllocator.at(config_dict["debt_allocator_address"])
    compound_strategy = config_dict["strategy_compound_address"]
    addresses = strategies_info["addresses"]
    callLen = strategies_info["callLen"]
    contracts = strategies_info["contracts"]
    checkdata = strategies_info["checkdata"]
    offset = strategies_info["offset"]
    calculationsLen = strategies_info["calculationsLen"]
    calculations = strategies_info["calculations"]
    conditionsLen = strategies_info["conditionsLen"]
    conditions = strategies_info["conditions"]

    tx = contract.addStrategy((addresses, callLen, contracts, checkdata, offset, calculationsLen, calculations, conditionsLen, conditions), compound_strategy, (int(len(COMPOUND_STRATEGY_CONTRACTS)), COMPOUND_STRATEGY_CONTRACTS, COMPOUND_STRATEGYY_CHECKDATA, COMPOUND_STRATEGYY_OFFSET, int(len(COMPOUND_STRATEGYY_CALCULATION)), COMPOUND_STRATEGYY_CALCULATION, int(len(COMPOUND_CALCULATION_CONDITION)), COMPOUND_CALCULATION_CONDITION),sender=account, max_priority_fee="1 gwei")
    logs = list(tx.decode_logs(contract.StrategyAdded))
    addresses = logs[0].Strategies
    callLen = logs[0].StrategiesCallLen
    contracts = logs[0].Contracts
    for i in COMPOUND_STRATEGYY_CHECKDATA:
        checkdata.append(i[2:])
    
    offset = logs[0].Offset
    calculationsLen = logs[0].CalculationsLen
    calculations = logs[0].Calculations
    ConditionsLen = logs[0].ConditionsLen
    conditions = logs[0].Conditions
    result = {}
    result["addresses"] = addresses
    result["callLen"] = callLen
    result["contracts"] = contracts
    result["checkdata"] = checkdata
    result["offset"] = offset
    result["calculationsLen"] = calculationsLen
    result["calculations"] = calculations
    result["conditionsLen"] = ConditionsLen
    result["conditions"] = conditions
    f = open("./scripts/strategies_info.json", "w")
    json.dump(result, f)
    f.close()
    print("new strategies: ")
    print(result)
 
