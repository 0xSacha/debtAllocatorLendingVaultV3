from ape import accounts, project, reverts
import pytest

CAIRO_VERIFIER = "0xAB43bA48c9edF4C2C4bB01237348D1D7B28ef168"
CAIRO_PROGRAM_HASH = "0x18261fedf8bb9295db94450fdda4343f1b04d3ae08f198d079a0e178596f494"



SELECTOR_1 = "dd384acb"
SELECTOR_2 = "9c47575f"

RANDOM_ADDRESS = "0xAB43bA48c9edF4C2C4bB01237348D1D7B28ef168"
RANDOM_SELECTOR = "0xf84b04f5"



@pytest.fixture
def owner(accounts):
    return accounts[0]

@pytest.fixture
def owner2(accounts):
    return accounts[1]

@pytest.fixture
def debt_allo(project, owner):
    return owner.deploy(project.DebtAllocator, CAIRO_VERIFIER, CAIRO_PROGRAM_HASH)

@pytest.fixture
def strat(project, owner):
    return owner.deploy(project.MockStrategy)

@pytest.fixture
def stratData1(project, owner):
    return owner.deploy(project.MockStrategyData1)

@pytest.fixture
def stratData2(project, owner):
    return owner.deploy(project.MockStrategyData2)



@pytest.fixture
def rewards_payer(accounts):
    return accounts[2]

# @pytest.fixture
# def rewards_token(project, owner):
#     return owner.deploy(project.dependencies["LlamaPay"]["master"].MockToken, 18)

# @pytest.fixture
# def rewards_streamer(project, rewards_payer, rewards_token, owner):
#     factory = owner.deploy(project.dependencies["LlamaPay"]["master"].LlamaPayFactory)
#     tx = factory.createLlamaPayContract(rewards_token, {'from': owner})
#     event = list(tx.decode_logs(factory.LlamaPayCreated))
#     return project.dependencies["LlamaPay"]["master"].LlamaPay.contract_type.at(event[0].llamaPay)

# def test_deployment(debt_allo):
#     assert debt_allo.cairoVerifier() == CAIRO_VERIFIER
#     assert debt_allo.cairoProgramHash() == bytes.fromhex("018261fedf8bb9295db94450fdda4343f1b04d3ae08f198d079a0e178596f494")


# def test_update_cairo_program_hash_1(debt_allo, owner2):
#     with reverts("Ownable: caller is not the owner"):
#         debt_allo.updateCairoProgramHash("018261fedf8bb9295db94450fdda4343f1b04d3ae08f198d079a0e178596f492",sender=owner2)

# def test_update_cairo_program_hash_2(debt_allo, owner):
#     tx = debt_allo.updateCairoProgramHash("018261fedf8bb9295db94450fdda4343f1b04d3ae08f198d079a0e178596f492",sender=owner)
#     logs = list(tx.decode_logs(debt_allo.NewCairoProgramHash))
#     assert logs[0].newCairoProgramHash == bytes.fromhex("018261fedf8bb9295db94450fdda4343f1b04d3ae08f198d079a0e178596f492")


# def test_update_cairo_verifier_1(debt_allo, owner2):
#     with reverts("Ownable: caller is not the owner"):
#         debt_allo.updateCairoVerifier("0x79c32F042e2e5aE9c70a9814833A9013f0023c7a",sender=owner2)

# def test_update_cairo_verifier_2(debt_allo, owner):
#     tx = debt_allo.updateCairoVerifier("0x79c32F042e2e5aE9c70a9814833A9013f0023c7a",sender=owner)
#     logs = list(tx.decode_logs(debt_allo.NewCairoVerifier))
#     assert logs[0].newCairoVerifier == "0x79c32F042e2e5aE9c70a9814833A9013f0023c7a"


# def test_update_stale_period_1(debt_allo, owner2):
#     with reverts("Ownable: caller is not the owner"):
#         debt_allo.updateStalePeriod(88,sender=owner2)

# def test_update_stale_period_2(debt_allo, owner):
#     tx = debt_allo.updateStalePeriod(88,sender=owner)
#     logs = list(tx.decode_logs(debt_allo.NewStalePeriod))
#     assert logs[0].newStalePeriod == 88

# def test_update_stale_snapshot_period_1(debt_allo, owner2):
#     with reverts("Ownable: caller is not the owner"):
#         debt_allo.updateStaleSnapshotPeriod(88,sender=owner2)

# def test_update_stale_snapshot_period_2(debt_allo, owner):
#     tx = debt_allo.updateStaleSnapshotPeriod(90,sender=owner)
#     logs = list(tx.decode_logs(debt_allo.NewStaleSnapshotPeriod))
#     assert logs[0].newStaleSnapshotPeriod == 90

# def test_add_strategy_1(debt_allo, owner2, strat, stratData1, stratData2):
#     with reverts("Ownable: caller is not the owner"):
#         debt_allo.addStrategy(([], [], [], [], [], [], [], [], []), strat.address, (2, [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner2)

# def test_add_strategy_2(debt_allo, owner, strat, stratData1, stratData2):
#     with reverts("INVALID_STRATEGY"):
#         debt_allo.addStrategy(([], [], [], [], [], [], [], [], []), stratData1.address, (2, [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)

# def test_add_strategy_3(debt_allo, owner, strat, stratData1, stratData2):
#     with reverts("INVALID_ARRAY_LEN"):
#         debt_allo.addStrategy(([], [], [], [], [], [], [], [], []), strat.address, (2, [stratData1.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)

# def test_add_strategy_4(debt_allo, owner, strat, stratData1, stratData2):
#     with reverts("INVALID_CALLDATA"):
#         debt_allo.addStrategy(([], [], [], [], [], [], [], [], []), strat.address, (2, [stratData1.address, stratData2.address], [RANDOM_SELECTOR, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)

# def test_add_strategy_5(debt_allo, owner, strat, stratData1, stratData2):
#     debt_allo.addStrategy(([], [], [], [], [], [], [], [], []), strat.address, (2, [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)
#     with reverts("INVALID_DATA"):
#         debt_allo.addStrategy(([], [], [], [], [], [], [], [], []), strat.address, (2, [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)

# def test_add_strategy_6(debt_allo, owner, strat, stratData1, stratData2):
#     debt_allo.addStrategy(([], [], [], [], [], [], [], [], []), strat.address, (2, [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)
#     with reverts("STRATEGY_EXISTS"):
#         debt_allo.addStrategy(([strat.address], [2], [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], [3], [0, 1, 0], [4], [0,0,0,0]), strat.address, (2, [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)

# def test_add_strategy_7(debt_allo, owner, strat, stratData1, stratData2):
#     tx = debt_allo.addStrategy(([], [], [], [], [], [], [], [], []), strat.address, (2, [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)
#     logs = list(tx.decode_logs(debt_allo.StrategyAdded))
#     assert logs[0].Strategies[0] == (strat.address).lower()
#     assert logs[0].StrategiesCallLen[0] == 2
#     assert logs[0].Contracts[0] == (stratData1.address).lower()
#     assert logs[0].Contracts[1] == (stratData2.address).lower()
#     assert logs[0].Checkdata[0] == bytearray.fromhex(SELECTOR_1)
#     assert logs[0].Checkdata[1] == bytearray.fromhex(SELECTOR_2)
#     assert logs[0].Offset[0] == 0
#     assert logs[0].Offset[1] == 0
#     assert logs[0].CalculationsLen[0] == 3
#     assert logs[0].Calculations[0] == 0
#     assert logs[0].Calculations[1] == 1
#     assert logs[0].Calculations[2] == 0
#     assert logs[0].ConditionsLen[0] == 4
#     assert logs[0].Conditions[0] == 0
#     assert logs[0].Conditions[1] == 0
#     assert logs[0].Conditions[2] == 0
#     assert logs[0].Conditions[3] == 0

# def test_update_strategy_1(debt_allo, owner2, strat, stratData1, stratData2):
#     with reverts("Ownable: caller is not the owner"):
#         debt_allo.updateStrategy(([], [], [], [], [], [], [], [], []), 0, (2, [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner2)

# def test_update_strategy_2(debt_allo, owner, strat, stratData1, stratData2):
#     with reverts("NO_STRATEGIES_REGISTERED"):
#         debt_allo.updateStrategy(([], [], [], [], [], [], [], [], []), 0, (2, [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)

# def test_update_strategy_3(debt_allo, owner, strat, stratData1, stratData2):
#     debt_allo.addStrategy(([], [], [], [], [], [], [], [], []), strat.address, (2, [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)
#     with reverts("INVALID_DATA"):
#         debt_allo.updateStrategy(([], [], [], [], [], [], [], [], []), 0, (2, [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)

# def test_update_strategy_4(debt_allo, owner, strat, stratData1, stratData2):
#     debt_allo.addStrategy(([], [], [], [], [], [], [], [], []), strat.address, (2, [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)
#     with reverts("INDEX_OUT_OF_RANGE"):
#         debt_allo.updateStrategy(([strat.address], [2], [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], [3], [0, 1, 0], [4], [0,0,0,0]), 1, (2, [stratData1.address, stratData2.address], [SELECTOR_2, SELECTOR_1], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)

# def test_update_strategy_5(debt_allo, owner, strat, stratData1, stratData2):
#     debt_allo.addStrategy(([], [], [], [], [], [], [], [], []), strat.address, (2, [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)
#     with reverts("INVALID_CALLDATA"):
#         debt_allo.updateStrategy(([strat.address], [2], [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], [3], [0, 1, 0], [4], [0,0,0,0]), 0, (2, [stratData1.address, stratData2.address], [RANDOM_ADDRESS, SELECTOR_1], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)

def test_update_strategy_6(debt_allo, owner, strat, stratData1, stratData2):
    debt_allo.addStrategy(([], [], [], [], [], [], [], [], []), strat.address, (2, [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], 3, [0, 1, 0], 4, [0,0,0,0]),sender=owner)
    tx = debt_allo.updateStrategy(([strat.address], [2], [stratData1.address, stratData2.address], [SELECTOR_1, SELECTOR_2], [0, 0], [3], [0, 1, 0], [4], [0,0,0,0]), 0, (2, [stratData1.address, stratData2.address], [SELECTOR_2, SELECTOR_1], [0, 0], 3, [0, 1, 0], 5, [0,0,0,0,0]),sender=owner)
    logs = list(tx.decode_logs(debt_allo.StrategyAdded))
    assert logs[0].Strategies[0] == (strat.address).lower()
    assert logs[0].StrategiesCallLen[0] == 2
    assert logs[0].Contracts[0] == (stratData1.address).lower()
    assert logs[0].Contracts[1] == (stratData2.address).lower()
    assert logs[0].Checkdata[0] == bytearray.fromhex(SELECTOR_2)
    assert logs[0].Checkdata[1] == bytearray.fromhex(SELECTOR_1)
    assert logs[0].Offset[0] == 0
    assert logs[0].Offset[1] == 0
    assert logs[0].CalculationsLen[0] == 3
    assert logs[0].Calculations[0] == 0
    assert logs[0].Calculations[1] == 1
    assert logs[0].Calculations[2] == 0
    assert logs[0].ConditionsLen[0] == 4
    assert logs[0].Conditions[0] == 0
    assert logs[0].Conditions[1] == 0
    assert logs[0].Conditions[2] == 0
    assert logs[0].Conditions[3] == 0



# def test_remove_strategy_1(debt_allo, owner2, strat, stratData1, stratData2):
#     with reverts("Ownable: caller is not the owner"):
#         debt_allo.removeStrategy(([], [], [], [], [], [], [], [], []), 0,sender=owner2)

# def test_remove_strategy_2(debt_allo, owner, strat, stratData1, stratData2):
#     with reverts("NO_STRATEGIES_REGISTERED"):
#         debt_allo.removeStrategy(([], [], [], [], [], [], [], [], []), 0,sender=owner)

# def test_update_strategy_2(debt_allo, owner):
#     with reverts("STRATEGY_NOT_FOUND"):
#         debt_allo.updateStrategy("0x79c32F042e2e5aE9c70a9814833A9013f0023c7a", AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)

# def test_add_strategy_3(debt_allo, owner):
#     debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
#     with reverts("INVALID_TAB_LEN_1"):
#         debt_allo.updateStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA_FAKE, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)

# def test_add_strategy_4(debt_allo, owner):
#     debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
#     with reverts("INVALID_TAB_LEN_2"):
#         debt_allo.updateStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET_FAKE, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)

# def test_update_strategy_5(debt_allo, owner):
#     tx1 = debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
#     tx2 = debt_allo.updateStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS_FAKE, AAVE_STRATEGYY_CHECKDATA_FAKE, AAVE_STRATEGYY_OFFSET_FAKE, AAVE_STRATEGYY_CALCULATION_FAKE, AAVE_CALCULATION_CONDITION_FAKE,sender=owner)
#     logs = list(tx2.decode_logs(debt_allo.StrategyUpdated))
#     assert logs[0].currentStrategy == AAVE_STRATEGY_ADDRESS
#     assert logs[0].strategyMaxDebtRatio == AAVE_MAX_STRATEGY_DEBT_RATIO
#     assert logs[0].strategyContracts[0] == AAVE_STRATEGY_CONTRACTS_FAKE[0].lower()
#     assert logs[0].strategyContracts[1] == AAVE_STRATEGY_CONTRACTS_FAKE[1].lower()
#     assert logs[0].strategyContracts[2] == AAVE_STRATEGY_CONTRACTS_FAKE[2].lower()
#     assert logs[0].strategyContracts[3] == AAVE_STRATEGY_CONTRACTS_FAKE[3].lower()
#     assert logs[0].strategyContracts[4] == AAVE_STRATEGY_CONTRACTS_FAKE[4].lower()
#     assert logs[0].strategyContracts[5] == AAVE_STRATEGY_CONTRACTS_FAKE[5].lower()
#     assert logs[0].strategyContracts[6] == AAVE_STRATEGY_CONTRACTS_FAKE[6].lower()
#     assert logs[0].strategyContracts[7] == AAVE_STRATEGY_CONTRACTS_FAKE[7].lower()
#     assert logs[0].strategyContracts[8] == AAVE_STRATEGY_CONTRACTS_FAKE[8].lower()
#     assert logs[0].strategyCheckData[0] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[0][2:])
#     assert logs[0].strategyCheckData[1] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[1][2:])
#     assert logs[0].strategyCheckData[2] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[2][2:])
#     assert logs[0].strategyCheckData[3] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[3][2:])
#     assert logs[0].strategyCheckData[4] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[4][2:])
#     assert logs[0].strategyCheckData[5] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[5][2:])
#     assert logs[0].strategyCheckData[6] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[6][2:])
#     assert logs[0].strategyCheckData[7] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[7][2:])
#     assert logs[0].strategyCheckData[8] == bytearray.fromhex(AAVE_STRATEGYY_CHECKDATA_FAKE[8][2:])
#     assert list(logs[0].strategyOffset) == AAVE_STRATEGYY_OFFSET_FAKE
#     assert list(logs[0].strategyCalculation) == AAVE_STRATEGYY_CALCULATION_FAKE
#     assert list(logs[0].strategyCondition) == AAVE_CALCULATION_CONDITION_FAKE

# def test_force_debt_ratio_1(debt_allo, owner2):
#     with reverts("Ownable: caller is not the owner"):
#         debt_allo.forceDebtRatio([0],sender=owner2)

# def test_force_debt_ratio_2(debt_allo, owner):
#     with reverts("Pausable: not paused"):
#         debt_allo.forceDebtRatio([0],sender=owner)

# def test_force_debt_ratio_3(debt_allo, owner):
#     debt_allo.pause(sender=owner)
#     with reverts("STRATEGY_NUL"):
#         debt_allo.forceDebtRatio([0],sender=owner)

# def test_force_debt_ratio_4(debt_allo, owner):
#     debt_allo.pause(sender=owner)
#     with reverts("STRATEGY_NUL"):
#         debt_allo.forceDebtRatio([0],sender=owner)

# def test_force_debt_ratio_5(debt_allo, owner):
#     debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
#     debt_allo.pause(sender=owner)
#     with reverts("INVALIDE_LENGTH"):
#         debt_allo.forceDebtRatio([1, 2],sender=owner)

# def test_force_debt_ratio_6(debt_allo, owner):
#     debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
#     debt_allo.pause(sender=owner)
#     with reverts("INVALID_DEBT_RATIO_SUM"):
#         debt_allo.forceDebtRatio([10900],sender=owner)

# def test_force_debt_ratio_7(debt_allo, owner):
#     debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
#     debt_allo.pause(sender=owner)
#     tx = debt_allo.forceDebtRatio([10000],sender=owner)
#     logs = list(tx.decode_logs(debt_allo.debtRatioForced))
#     assert list(logs[0].newDebtRatio) == [10000]

# def test_remove_strategy_1(debt_allo, owner2):
#     with reverts("Ownable: caller is not the owner"):
#         debt_allo.removeStrategy(0,sender=owner2)

# def test_remove_strategy_2(debt_allo, owner):
#     with reverts("INDEX_OUT_OF_RANGE"):
#         debt_allo.removeStrategy(0,sender=owner)

# def test_remove_strategy_3(debt_allo, owner):
#     tx1 = debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
#     debt_allo.pause(sender=owner)
#     debt_allo.forceDebtRatio([10000],sender=owner)
#     with reverts("DEBT_RATIO_NOT_NUL"):
#         debt_allo.removeStrategy(0,sender=owner)

# def test_remove_strategy_4(debt_allo, owner):
#     debt_allo.addStrategy(AAVE_STRATEGY_ADDRESS, AAVE_MAX_STRATEGY_DEBT_RATIO, AAVE_STRATEGY_CONTRACTS, AAVE_STRATEGYY_CHECKDATA, AAVE_STRATEGYY_OFFSET, AAVE_STRATEGYY_CALCULATION, AAVE_CALCULATION_CONDITION,sender=owner)
#     tx = debt_allo.removeStrategy(0,sender=owner)
#     logs = list(tx.decode_logs(debt_allo.StrategyRemoved))
#     assert logs[0].strategyRemoved == AAVE_STRATEGY_ADDRESS


# def saveSnapshot_1(debt_allo, owner):
#     with reverts("STRATEGY_NUL"):
#         debt_allo.saveSnapshot_1(sender=owner2)


# # TODO: WIP
# def test_rewards(debt_allo, owner, rewards_streamer, rewards_payer, rewards_token, rewards_per_week):
#     tx = rewards_streamer.createStream(debt_allo.address, rewards_per_week)
#     event = list(tx.decode_logs(rewards_streamer.StreamCreated))
#     stream_id = event[0].streamId
    
#     assert rewards_streamer.streamToStart(stream_id) > 0




