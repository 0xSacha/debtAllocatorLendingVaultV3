from ape import accounts, project, reverts
import pytest

CAIRO_VERIFIER = "0xAB43bA48c9edF4C2C4bB01237348D1D7B28ef168"
CAIRO_PROGRAM_HASH = "0x18261fedf8bb9295db94450fdda4343f1b04d3ae08f198d079a0e178596f494"

## The following data is valid for Goerli, with WETH ASSET
AAVE_WETH = "0xCCa7d1416518D095E729904aAeA087dBA749A4dC"
AAVE_PROTOCOL_DATA_PROVIDER = "0x927F584d4321C1dCcBf5e2902368124b02419a1E"
AAVE_RESERVE_INTEREST_RATE_STRATEGY= "0x5ecE040038c822d7228F24D9F2e1Fd41bc77A3c4"

## Reserve Data
AAVE_CONTRACT_ADDRESS_0 = AAVE_PROTOCOL_DATA_PROVIDER
## 0x3e150141 (selector from getReserveConfigurationData(address)) + 000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC wethadress to byte32
AAVE_CHECKDATA_0 = "0x3e150141000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC"
## 5th arg so (5-1)*32 
AAVE_STRATEGYY_OFFSET_0 = 128

## Available Liquidity
AAVE_CONTRACT_ADDRESS_1 = AAVE_PROTOCOL_DATA_PROVIDER
## 0x35ea6a75 (selector from getReserveData(address)) + 000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC wethadress to byte32
AAVE_CHECKDATA_1 = "0x35ea6a75000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC"
## first arg so 0
AAVE_STRATEGYY_OFFSET_1 = 0

## totalStableDebt 
AAVE_CONTRACT_ADDRESS_2 = AAVE_PROTOCOL_DATA_PROVIDER
## 0x35ea6a75 (selector from getReserveData(address)) + 000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC wethadress to byte32
AAVE_CHECKDATA_2 = "0x35ea6a75000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC"
## second arg so 32
AAVE_STRATEGYY_OFFSET_2 = 32

## totalVariableDebt 
AAVE_CONTRACT_ADDRESS_3 = AAVE_PROTOCOL_DATA_PROVIDER
## 0x35ea6a75 (selector from getReserveData(address)) + 000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC wethadress to byte32
AAVE_CHECKDATA_3 = "0x35ea6a75000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC"
## third arg so 64
AAVE_STRATEGYY_OFFSET_3 = 64

## totalVariableDebt 
AAVE_CONTRACT_ADDRESS_4 = AAVE_RESERVE_INTEREST_RATE_STRATEGY
## 0x35ea6a75 (selector from OPTIMAL_UTILIZATION_RATE() ) 
AAVE_CHECKDATA_4 = "0xa15f30ac"
AAVE_STRATEGYY_OFFSET_4 = 0

AAVE_CONTRACT_ADDRESS_5 = AAVE_RESERVE_INTEREST_RATE_STRATEGY
## 0x0bdf953f (selector from stableRateSlope1() ) 
AAVE_CHECKDATA_5 = "0x0bdf953f"
AAVE_STRATEGYY_OFFSET_5 = 0

AAVE_CONTRACT_ADDRESS_6 = AAVE_RESERVE_INTEREST_RATE_STRATEGY
## 0xccab01a3 (selector from stableRateSlope2() ) 
AAVE_CHECKDATA_6 = "0xccab01a3"
AAVE_STRATEGYY_OFFSET_6 = 0

AAVE_CONTRACT_ADDRESS_7 = AAVE_RESERVE_INTEREST_RATE_STRATEGY
## 0x7b832f58 (selector from variableRateSlope1() ) 
AAVE_CHECKDATA_7 = "0x7b832f58"
AAVE_STRATEGYY_OFFSET_7 = 0

AAVE_CONTRACT_ADDRESS_8 = AAVE_RESERVE_INTEREST_RATE_STRATEGY
## 0x65614f81 (selector from variableRateSlope2() ) 
AAVE_CHECKDATA_8 = "0x65614f81"
AAVE_STRATEGYY_OFFSET_8 = 0

AAVE_CONTRACT_ADDRESS_9 = AAVE_RESERVE_INTEREST_RATE_STRATEGY
## 0xb2589544 (selector from baseVariableBorrowRate() ) 
AAVE_CHECKDATA_9 = "0xb2589544"
AAVE_STRATEGYY_OFFSET_9 = 0


# concerned strategy address
AAVE_STRATEGY_ADDRESS= "0x76aFA2b6C29E1B277A3BB1CD320b2756c1674c91" 

AAVE_MAX_STRATEGY_DEBT_RATIO = 10000

# contracts to get data from
AAVE_STRATEGY_CONTRACTS = [AAVE_CONTRACT_ADDRESS_0, AAVE_CONTRACT_ADDRESS_1, AAVE_CONTRACT_ADDRESS_2, AAVE_CONTRACT_ADDRESS_3, AAVE_CONTRACT_ADDRESS_4, AAVE_CONTRACT_ADDRESS_5, AAVE_CONTRACT_ADDRESS_6, AAVE_CONTRACT_ADDRESS_7, AAVE_CONTRACT_ADDRESS_8, AAVE_CONTRACT_ADDRESS_9]
AAVE_STRATEGY_CONTRACTS_FAKE = [AAVE_CONTRACT_ADDRESS_1, AAVE_CONTRACT_ADDRESS_2, AAVE_CONTRACT_ADDRESS_3, AAVE_CONTRACT_ADDRESS_4, AAVE_CONTRACT_ADDRESS_5, AAVE_CONTRACT_ADDRESS_6, AAVE_CONTRACT_ADDRESS_7, AAVE_CONTRACT_ADDRESS_8, AAVE_CONTRACT_ADDRESS_9]
# checkdata (selector + neccessary args bytes32)
AAVE_STRATEGYY_CHECKDATA = [AAVE_CHECKDATA_0, AAVE_CHECKDATA_1, AAVE_CHECKDATA_2, AAVE_CHECKDATA_3, AAVE_CHECKDATA_4, AAVE_CHECKDATA_5, AAVE_CHECKDATA_6, AAVE_CHECKDATA_7, AAVE_CHECKDATA_8, AAVE_CHECKDATA_9]
AAVE_STRATEGYY_CHECKDATA_FAKE = [AAVE_CHECKDATA_1, AAVE_CHECKDATA_2, AAVE_CHECKDATA_3, AAVE_CHECKDATA_4, AAVE_CHECKDATA_5, AAVE_CHECKDATA_6, AAVE_CHECKDATA_7, AAVE_CHECKDATA_8, AAVE_CHECKDATA_9]

# offset, which args we need from the data received from the call, 0 by default
AAVE_STRATEGYY_OFFSET = [AAVE_STRATEGYY_OFFSET_0, AAVE_STRATEGYY_OFFSET_1, AAVE_STRATEGYY_OFFSET_2, AAVE_STRATEGYY_OFFSET_3, AAVE_STRATEGYY_OFFSET_4, AAVE_STRATEGYY_OFFSET_5, AAVE_STRATEGYY_OFFSET_6, AAVE_STRATEGYY_OFFSET_7, AAVE_STRATEGYY_OFFSET_8, AAVE_STRATEGYY_OFFSET_9]
AAVE_STRATEGYY_OFFSET_FAKE = [AAVE_STRATEGYY_OFFSET_1, AAVE_STRATEGYY_OFFSET_2, AAVE_STRATEGYY_OFFSET_3, AAVE_STRATEGYY_OFFSET_4, AAVE_STRATEGYY_OFFSET_5, AAVE_STRATEGYY_OFFSET_6, AAVE_STRATEGYY_OFFSET_7, AAVE_STRATEGYY_OFFSET_8, AAVE_STRATEGYY_OFFSET_9]


AAVE_STRATEGYY_CALCULATION = [1, 2, 0, 10000, 3, 0, 2, 3, 0, 10002, 1000000000000000000000020000, 2,10003, 10001, 3, 10004, 4, 1, 1000000000000000000000020000, 4, 1, 10005, 1000000000000000000000020000, 2, 10007, 10006, 3, 10008, 6, 2, 10009, 1000000000000000000000020000, 3,
                10010, 5, 0, 10011, 9, 0, 2, 1000000000000000000000020000, 2, 10013, 10002, 3, 10011, 10014, 2, 10015, 1000000000000000000000020000, 3, 10008, 8, 2, 10017, 1000000000000000000000020000, 3, 10018, 7, 0, 10019, 9, 0,
                3, 1000000000000000000000020000, 2, 10021, 10002, 3, 10020, 10022, 2, 10023, 1000000000000000000000020000, 3, 10016, 10024, 0, 30000, 0, 1, 10025, 10026, 2, 10027, 30000, 3, 10028, 10004, 2, 10029, 1000000000000000000000020000, 3, 1, 2, 0, 10000, 3, 
                0, 2, 3, 0, 10002, 1000000000000000000000020000, 2, 10003, 10001, 3, 10004, 1000000000000000000000020000, 2, 10005, 4, 3, 10006, 5, 2, 10007, 1000000000000000000000020000, 3, 10008, 9, 0, 2, 1000000000000000000000020000, 2,
                     10010, 10002, 3, 10011, 10009, 2, 10012, 1000000000000000000000020000, 3, 10006, 7, 2, 10014, 1000000000000000000000020000, 3, 10015, 9, 0, 3, 1000000000000000000000020000, 2, 10017, 10002, 3, 10016, 10018, 2, 10019, 1000000000000000000000020000, 3,
                     10013, 10020, 0, 30000, 0, 1, 10021, 10022, 2, 10023, 30000, 3, 10024, 10004, 2, 10025, 1000000000000000000000020000, 3]

AAVE_STRATEGYY_CALCULATION_FAKE = [10000, 3, 0, 2, 3, 0, 10002, 1000000000000000000000020000, 2,10003, 10001, 3, 10004, 4, 1, 1000000000000000000000020000, 4, 1, 10005, 1000000000000000000000020000, 2, 10007, 10006, 3, 10008, 6, 2, 10009, 1000000000000000000000020000, 3,
                10010, 5, 0, 10011, 9, 0, 2, 1000000000000000000000020000, 2, 10013, 10002, 3, 10011, 10014, 2, 10015, 1000000000000000000000020000, 3, 10008, 8, 2, 10017, 1000000000000000000000020000, 3, 10018, 7, 0, 10019, 9, 0,
                3, 1000000000000000000000020000, 2, 10021, 10002, 3, 10020, 10022, 2, 10023, 1000000000000000000000020000, 3, 10016, 10024, 0, 30000, 0, 1, 10025, 10026, 2, 10027, 30000, 3, 10028, 10004, 2, 10029, 1000000000000000000000020000, 3, 1, 2, 0, 10000, 3, 
                0, 2, 3, 0, 10002, 1000000000000000000000020000, 2, 10003, 10001, 3, 10004, 1000000000000000000000020000, 2, 10005, 4, 3, 10006, 5, 2, 10007, 1000000000000000000000020000, 3, 10008, 9, 0, 2, 1000000000000000000000020000, 2,
                     10010, 10002, 3, 10011, 10009, 2, 10012, 1000000000000000000000020000, 3, 10006, 7, 2, 10014, 1000000000000000000000020000, 3, 10015, 9, 0, 3, 1000000000000000000000020000, 2, 10017, 10002, 3, 10016, 10018, 2, 10019, 1000000000000000000000020000, 3,
                     10013, 10020, 0, 30000, 0, 1, 10021, 10022, 2, 10023, 30000, 3, 10024, 10004, 2, 10025, 1000000000000000000000020000, 3]

AAVE_CALCULATION_CONDITION = [1, 2, 0, 10000, 3, 0, 2, 3, 0, 10002, 1000000000000000000000020000, 2, 10003, 10001, 3, 10004, 4, 31, 27]
AAVE_CALCULATION_CONDITION_FAKE = [10000, 3, 0, 2, 3, 0, 10002, 1000000000000000000000020000, 2, 10003, 10001, 3, 10004, 4, 31, 27]


@pytest.fixture
def owner(accounts):
    return accounts[0]

@pytest.fixture
def owner2(accounts):
    return accounts[1]

@pytest.fixture
def debt_allo(project, owner):
    return owner.deploy(project.DebtAllocator, CAIRO_VERIFIER, CAIRO_PROGRAM_HASH)

    
def test_deployment(debt_allo, owner):
    assert debt_allo.cairoVerifier() == CAIRO_VERIFIER
    assert debt_allo.cairoProgramHash() == bytes.fromhex("018261fedf8bb9295db94450fdda4343f1b04d3ae08f198d079a0e178596f494")

def test_add_strategy_1(debt_allo, owner2):
    with reverts("Ownable: caller is not the owner"):
        debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner2)

def test_add_strategy_2(debt_allo, owner):
    debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
    with reverts("STRATEGY_EXISTS"):
        debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)

def test_add_strategy_3(debt_allo, owner):
    with reverts("INVALID_TAB_LEN_1"):
        debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA_FAKE, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)

def test_add_strategy_4(debt_allo, owner):
    with reverts("INVALID_TAB_LEN_2"):
        debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET_FAKE, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)

def test_add_strategy_5(debt_allo, owner):
    tx = debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
    logs = list(tx.decode_logs(debt_allo.NewStrategy))
    assert logs[0].newStrategy == AAVE_STRATEGY_ADDRESS
    assert logs[0].strategyMaxDebtRatio == AAVE_MAX_STRATEGY_DEBT_RATIO
    assert logs[0].strategyContracts[0] == AAVE_STRATEGY_CONTRACTS[0].lower()
    assert logs[0].strategyContracts[1] == AAVE_STRATEGY_CONTRACTS[1].lower()
    assert logs[0].strategyContracts[2] == AAVE_STRATEGY_CONTRACTS[2].lower()
    assert logs[0].strategyContracts[3] == AAVE_STRATEGY_CONTRACTS[3].lower()
    assert logs[0].strategyContracts[4] == AAVE_STRATEGY_CONTRACTS[4].lower()
    assert logs[0].strategyContracts[5] == AAVE_STRATEGY_CONTRACTS[5].lower()
    assert logs[0].strategyContracts[6] == AAVE_STRATEGY_CONTRACTS[6].lower()
    assert logs[0].strategyContracts[7] == AAVE_STRATEGY_CONTRACTS[7].lower()
    assert logs[0].strategyContracts[8] == AAVE_STRATEGY_CONTRACTS[8].lower()
    assert logs[0].strategyContracts[9] == AAVE_STRATEGY_CONTRACTS[9].lower()
    assert logs[0].strategyCheckData[0] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA[0][2:])
    assert logs[0].strategyCheckData[1] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA[1][2:])
    assert logs[0].strategyCheckData[2] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA[2][2:])
    assert logs[0].strategyCheckData[3] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA[3][2:])
    assert logs[0].strategyCheckData[4] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA[4][2:])
    assert logs[0].strategyCheckData[5] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA[5][2:])
    assert logs[0].strategyCheckData[6] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA[6][2:])
    assert logs[0].strategyCheckData[7] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA[7][2:])
    assert logs[0].strategyCheckData[8] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA[8][2:])
    assert logs[0].strategyCheckData[9] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA[9][2:])
    assert list(logs[0].strategyOffset) == AAVE_STRATEGYY_OFFSET
    assert list(logs[0].strategyCalculation) == AAVE_STRATEGYY_CALCULATION
    assert list(logs[0].strategyCondition) == AAVE_CALCULATION_CONDITION

def test_update_strategy_1(debt_allo, owner2):
    with reverts("Ownable: caller is not the owner"):
        debt_allo.updateStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner2)

def test_update_strategy_2(debt_allo, owner):
    with reverts("STRATEGY_NOT_FOUND"):
        debt_allo.updateStrategy("0x79c32F042e2e5aE9c70a9814833A9013f0023c7a", AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)

def test_add_strategy_3(debt_allo, owner):
    debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
    with reverts("INVALID_TAB_LEN_1"):
        debt_allo.updateStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA_FAKE, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)

def test_add_strategy_4(debt_allo, owner):
    debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
    with reverts("INVALID_TAB_LEN_2"):
        debt_allo.updateStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET_FAKE, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)

def test_update_strategy_5(debt_allo, owner):
    tx1 = debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
    tx2 = debt_allo.updateStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS_FAKE, AAVE_STRATEGYY_CHECKDATA_FAKE, AAVE_STRATEGYY_OFFSET_FAKE, AAVE_STRATEGYY_CALCULATION_FAKE, AAVE_CALCULATION_CONDITION_FAKE,sender=owner)
    logs = list(tx2.decode_logs(debt_allo.StrategyUpdated))
    assert logs[0].currentStrategy == AAVE_STRATEGY_ADDRESS
    assert logs[0].strategyMaxDebtRatio == AAVE_MAX_STRATEGY_DEBT_RATIO
    assert logs[0].strategyContracts[0] == AAVE_STRATEGY_CONTRACTS_FAKE[0].lower()
    assert logs[0].strategyContracts[1] == AAVE_STRATEGY_CONTRACTS_FAKE[1].lower()
    assert logs[0].strategyContracts[2] == AAVE_STRATEGY_CONTRACTS_FAKE[2].lower()
    assert logs[0].strategyContracts[3] == AAVE_STRATEGY_CONTRACTS_FAKE[3].lower()
    assert logs[0].strategyContracts[4] == AAVE_STRATEGY_CONTRACTS_FAKE[4].lower()
    assert logs[0].strategyContracts[5] == AAVE_STRATEGY_CONTRACTS_FAKE[5].lower()
    assert logs[0].strategyContracts[6] == AAVE_STRATEGY_CONTRACTS_FAKE[6].lower()
    assert logs[0].strategyContracts[7] == AAVE_STRATEGY_CONTRACTS_FAKE[7].lower()
    assert logs[0].strategyContracts[8] == AAVE_STRATEGY_CONTRACTS_FAKE[8].lower()
    assert logs[0].strategyCheckData[0] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[0][2:])
    assert logs[0].strategyCheckData[1] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[1][2:])
    assert logs[0].strategyCheckData[2] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[2][2:])
    assert logs[0].strategyCheckData[3] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[3][2:])
    assert logs[0].strategyCheckData[4] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[4][2:])
    assert logs[0].strategyCheckData[5] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[5][2:])
    assert logs[0].strategyCheckData[6] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[6][2:])
    assert logs[0].strategyCheckData[7] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[7][2:])
    assert logs[0].strategyCheckData[8] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[8][2:])
    assert list(logs[0].strategyOffset) == AAVE_STRATEGYY_OFFSET_FAKE
    assert list(logs[0].strategyCalculation) == AAVE_STRATEGYY_CALCULATION_FAKE
    assert list(logs[0].strategyCondition) == AAVE_CALCULATION_CONDITION_FAKE

def test_force_debt_ratio_1(debt_allo, owner2):
    with reverts("Ownable: caller is not the owner"):
        debt_allo.forceDebtRatio([0],sender=owner2)

def test_force_debt_ratio_2(debt_allo, owner):
    with reverts("Pausable: not paused"):
        debt_allo.forceDebtRatio([0],sender=owner)

def test_force_debt_ratio_3(debt_allo, owner):
    debt_allo.pause(sender=owner)
    with reverts("STRATEGY_NUL"):
        debt_allo.forceDebtRatio([0],sender=owner)

def test_force_debt_ratio_4(debt_allo, owner):
    debt_allo.pause(sender=owner)
    with reverts("STRATEGY_NUL"):
        debt_allo.forceDebtRatio([0],sender=owner)

def test_force_debt_ratio_5(debt_allo, owner):
    debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
    debt_allo.pause(sender=owner)
    with reverts("INVALIDE_LENGTH"):
        debt_allo.forceDebtRatio([1, 2],sender=owner)

def test_force_debt_ratio_6(debt_allo, owner):
    debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
    debt_allo.pause(sender=owner)
    with reverts("INVALID_DEBT_RATIO_SUM"):
        debt_allo.forceDebtRatio([10900],sender=owner)

def test_force_debt_ratio_7(debt_allo, owner):
    debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
    debt_allo.pause(sender=owner)
    tx = debt_allo.forceDebtRatio([10000],sender=owner)
    logs = list(tx.decode_logs(debt_allo.debtRatioForced))
    assert list(logs[0].newDebtRatio) == [10000]

def test_remove_strategy_1(debt_allo, owner2):
    with reverts("Ownable: caller is not the owner"):
        debt_allo.removeStrategy(0,sender=owner2)

def test_remove_strategy_2(debt_allo, owner):
    with reverts("INDEX_OUT_OF_RANGE"):
        debt_allo.removeStrategy(0,sender=owner)

def test_remove_strategy_3(debt_allo, owner):
    tx1 = debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
    debt_allo.pause(sender=owner)
    debt_allo.forceDebtRatio([10000],sender=owner)
    with reverts("DEBT_RATIO_NOT_NUL"):
        debt_allo.removeStrategy(0,sender=owner)

def test_remove_strategy_4(debt_allo, owner):
    debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
    tx = debt_allo.removeStrategy(0,sender=owner)
    logs = list(tx.decode_logs(debt_allo.StrategyRemoved))
    assert logs[0].strategyRemoved == AAVE_STRATEGY_ADDRESS


def test_update_cairo_program_hash_1(debt_allo, owner2):
    with reverts("Ownable: caller is not the owner"):
        debt_allo.updateCairoProgramHash("018261fedf8bb9295db94450fdda4343f1b04d3ae08f198d079a0e178596f492",sender=owner2)

def test_update_cairo_program_hash_2(debt_allo, owner):
    tx = debt_allo.updateCairoProgramHash("018261fedf8bb9295db94450fdda4343f1b04d3ae08f198d079a0e178596f492",sender=owner)
    logs = list(tx.decode_logs(debt_allo.NewCairoProgramHash))
    assert logs[0].newCairoProgramHash == bytes.fromhex("018261fedf8bb9295db94450fdda4343f1b04d3ae08f198d079a0e178596f492")


def test_update_cairo_verifier_1(debt_allo, owner2):
    with reverts("Ownable: caller is not the owner"):
        debt_allo.updateCairoVerifier("0x79c32F042e2e5aE9c70a9814833A9013f0023c7a",sender=owner2)

def test_update_cairo_verifier_2(debt_allo, owner):
    tx = debt_allo.updateCairoVerifier("0x79c32F042e2e5aE9c70a9814833A9013f0023c7a",sender=owner)
    logs = list(tx.decode_logs(debt_allo.NewCairoVerifier))
    assert logs[0].newCairoVerifier == "0x79c32F042e2e5aE9c70a9814833A9013f0023c7a"


def test_update_stale_period_1(debt_allo, owner2):
    with reverts("Ownable: caller is not the owner"):
        debt_allo.updateStalePeriod(88,sender=owner2)

def test_update_stale_period_2(debt_allo, owner):
    tx = debt_allo.updateStalePeriod(88,sender=owner)
    logs = list(tx.decode_logs(debt_allo.NewStalePeriod))
    assert logs[0].newStalePeriod == 88

def test_update_stale_snapshot_period_1(debt_allo, owner2):
    with reverts("Ownable: caller is not the owner"):
        debt_allo.updateStaleSnapshotPeriod(88,sender=owner2)

def test_update_stale_snapshot_period_2(debt_allo, owner):
    tx = debt_allo.updateStaleSnapshotPeriod(90,sender=owner)
    logs = list(tx.decode_logs(debt_allo.NewStaleSnapshotPeriod))
    assert logs[0].newStaleSnapshotPeriod == 90

def saveSnapshot_1(debt_allo, owner):
    with reverts("STRATEGY_NUL"):
        debt_allo.saveSnapshot_1(sender=owner2)

