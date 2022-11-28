const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");
const { expect, assert } = require("chai");
const { ethers } = require("hardhat");
// const { ethers } = require("ethers");


const CAIRO_VERIFIER_2 = "0x3468Ef8426530842F4044cbb1D0A2e175d88628F";
const CAIRO_VERIFIER = "0x47312450B3Ac8b5b8e247a6bB6d523e7605bDb60";
const CAIRO_PROGRAM_HASH = "0x00bfd3c17a344350521b3f4c254de74e98ef52cbb2a305be36c72f8af8b6b282";
const CAIRO_PROGRAM_HASH2 = "0x01bfd3c17a344350521b3f4c254de74e98ef52cbb2a305be36c72f8af8b6b282";

const sel1 = "0x60d586f8"
const sel2 = "0xc515205d"
const sel3 = "0xf2d14b00"
const sel4 = "0xbfd68858"

// Calcul 1 means (op1+op2) * op1
const calcul1= [{operand1: 0, operand2: 1, operation: 0}, {operand1: 10000, operand2: 0, operation: 2}]

// Calcul 2 means ((op1*op2) + op3 - 1) * 2
const calcul2= [{operand1: 0, operand2: 1, operation: 2}, {operand1: 10000, operand2: 2, operation: 0}, {operand1: 10001, operand2: 20001, operation: 1}, {operand1: 10002, operand2: 20002, operation: 2}]

describe("deploy debt allocator and 2 dummy", function () {
  async function deployTokenFixture() {
    const DebtAllocatorTest = await ethers.getContractFactory("DebtAllocatorTest1");
    const dummy1 = await ethers.getContractFactory("dummy");
    const dummy2 = await ethers.getContractFactory("dummy");
    const [owner] = await ethers.getSigners();
    const starkDebtContract = await DebtAllocatorTest.deploy(CAIRO_VERIFIER, CAIRO_PROGRAM_HASH);
    await starkDebtContract.deployed();

    const dummy1Contract = await dummy1.deploy();
    await dummy1Contract.deployed();

    const dummy2Contract = await dummy2.deploy();
    await dummy2Contract.deployed();

    // Fixtures can return anything you consider useful for your tests
    return { starkDebtContract, dummy1Contract, dummy2Contract, owner };
  }

  it("Should add a strategy, check event, storage and getters", async function () {
    const { starkDebtContract, dummy1Contract, dummy2Contract } = await loadFixture(deployTokenFixture);
    const strat1 = await starkDebtContract.addStrategy(dummy1Contract.address, 7000,[dummy1Contract.address, dummy1Contract.address], [sel1, sel2], calcul1);
    const receipt1 = await strat1.wait()
    const newStrategyEvent1 = receipt1.events.find(x => x.event === "NewStrategy");
    assert.equal(newStrategyEvent1.args.newStrategy, dummy1Contract.address);
    assert.equal(newStrategyEvent1.args.strategyMaxDebtRatio, 7000);
    assert.equal(newStrategyEvent1.args.strategyContracts[0], dummy1Contract.address);
    assert.equal(newStrategyEvent1.args.strategyContracts[1], dummy1Contract.address);
    assert.equal(newStrategyEvent1.args.strategyCheckData[0], sel1);
    assert.equal(newStrategyEvent1.args.strategyCheckData[1], sel2);
    assert.equal(newStrategyEvent1.args.strategyCalculation[0][0], 0);
    assert.equal(newStrategyEvent1.args.strategyCalculation[0][1], 1);
    assert.equal(newStrategyEvent1.args.strategyCalculation[0][2], 0);
    assert.equal(newStrategyEvent1.args.strategyCalculation[1][0], 10000);
    assert.equal(newStrategyEvent1.args.strategyCalculation[1][1], 0);
    assert.equal(newStrategyEvent1.args.strategyCalculation[1][2], 2);

    const strategyContract1 = await starkDebtContract.strategyContracts(dummy1Contract.address, 0);
    const strategyContract2 = await starkDebtContract.strategyContracts(dummy1Contract.address, 1);
    const strategyCheckdata1 = await starkDebtContract.strategyCheckdata(dummy1Contract.address, 0);
    const strategyCheckdata2 = await starkDebtContract.strategyCheckdata(dummy1Contract.address, 1);
    const strategyCalculation1 =  await starkDebtContract.strategyCalculation(dummy1Contract.address, 0);
    const strategyCalculation2 =  await starkDebtContract.strategyCalculation(dummy1Contract.address, 1);
    assert.equal(strategyContract1, dummy1Contract.address);
    assert.equal(strategyContract2, dummy1Contract.address);
    assert.equal(strategyCheckdata1, sel1);
    assert.equal(strategyCheckdata2, sel2);
    assert.equal(strategyCalculation1[0], 0);
    assert.equal(strategyCalculation1[1], 1);
    assert.equal(strategyCalculation1[2], 0);
    assert.equal(strategyCalculation2[0], 10000);
    assert.equal(strategyCalculation2[1], 0);
    assert.equal(strategyCalculation2[2], 2);

    // callstatic because we can't set the function as view
    const strategyData = await starkDebtContract.callStatic.getStrategiesData();
    assert.equal(strategyData[0][0], 1);
    assert.equal(strategyData[0][1], 2);

    const strategyCalcul = await starkDebtContract.getStrategiesCalculation();
    assert.equal(strategyCalcul[0][0][0], 0);
    assert.equal(strategyCalcul[0][0][1], 1);
    assert.equal(strategyCalcul[0][0][2], 0);
    assert.equal(strategyCalcul[0][1][0], 10000);
    assert.equal(strategyCalcul[0][1][1], 0);
    assert.equal(strategyCalcul[0][1][2], 2);

    await starkDebtContract.addStrategy(dummy2Contract.address, 5000,[dummy2Contract.address, dummy2Contract.address, dummy2Contract.address], [sel1, sel3, sel4], calcul2);

    const strategyData2 = await starkDebtContract.callStatic.getStrategiesData();
    assert.equal(strategyData2[0][0], 1);
    assert.equal(strategyData2[0][1], 2);
    assert.equal(strategyData2[1][0], 1);
    assert.equal(strategyData2[1][1], 3);
    assert.equal(strategyData2[1][2], 4);

    const strategyCalcul2 = await starkDebtContract.getStrategiesCalculation();
    assert.equal(strategyCalcul2[0][0][0], 0);
    assert.equal(strategyCalcul2[0][0][1], 1);
    assert.equal(strategyCalcul2[0][0][2], 0);
    assert.equal(strategyCalcul2[0][1][0], 10000);
    assert.equal(strategyCalcul2[0][1][1], 0);
    assert.equal(strategyCalcul2[0][1][2], 2);

    assert.equal(strategyCalcul2[1][0][0], 0);
    assert.equal(strategyCalcul2[1][0][1], 1);
    assert.equal(strategyCalcul2[1][0][2], 2);
    assert.equal(strategyCalcul2[1][1][0], 10000);
    assert.equal(strategyCalcul2[1][1][1], 2);
    assert.equal(strategyCalcul2[1][1][2], 0);
    assert.equal(strategyCalcul2[1][2][0], 10001);
    assert.equal(strategyCalcul2[1][2][1], 20001);
    assert.equal(strategyCalcul2[1][2][2], 1);
    assert.equal(strategyCalcul2[1][3][0], 10002);
    assert.equal(strategyCalcul2[1][3][1], 20002);
    assert.equal(strategyCalcul2[1][3][2], 2);

    await expect(starkDebtContract.addStrategy(dummy2Contract.address, 5000,[dummy2Contract.address, dummy2Contract.address], [sel1, sel3, sel4], calcul2)).to.be.revertedWith('Strategy exists');
    await expect(starkDebtContract.addStrategy("0x25cd6c173248CF7d3cAABAE4c816A0467838Cd0a", 5000,[dummy2Contract.address, dummy2Contract.address], [sel1, sel3, sel4], calcul2)).to.be.revertedWith('different tab length');
  });

  it("Should add a strategy, update strategy parameters and delete it", async function () {
    const { starkDebtContract, dummy1Contract, dummy2Contract } = await loadFixture(deployTokenFixture);
    await starkDebtContract.addStrategy(dummy1Contract.address, 7000,[dummy1Contract.address, dummy1Contract.address], [sel1, sel2], calcul1);
    const updateStrat = await starkDebtContract.updateStrategy(dummy1Contract.address, 5000,[dummy2Contract.address, dummy2Contract.address, dummy2Contract.address], [sel1, sel3, sel4], calcul2);
    const receipt1 = await updateStrat.wait()
    const newStrategyEvent1 = receipt1.events.find(x => x.event === "StrategyUpdated");
    assert.equal(newStrategyEvent1.args.newStrategy, dummy1Contract.address);
    assert.equal(newStrategyEvent1.args.strategyMaxDebtRatio, 5000);
    assert.equal(newStrategyEvent1.args.strategyContracts[0], dummy2Contract.address);
    assert.equal(newStrategyEvent1.args.strategyContracts[1], dummy2Contract.address);
    assert.equal(newStrategyEvent1.args.strategyContracts[2], dummy2Contract.address);
    assert.equal(newStrategyEvent1.args.strategyCheckData[0], sel1);
    assert.equal(newStrategyEvent1.args.strategyCheckData[1], sel3);
    assert.equal(newStrategyEvent1.args.strategyCheckData[2], sel4);
    assert.equal(newStrategyEvent1.args.strategyCalculation[0][0], 0);
    assert.equal(newStrategyEvent1.args.strategyCalculation[0][1], 1);
    assert.equal(newStrategyEvent1.args.strategyCalculation[0][2], 2);
    assert.equal(newStrategyEvent1.args.strategyCalculation[1][0], 10000);
    assert.equal(newStrategyEvent1.args.strategyCalculation[1][1], 2);
    assert.equal(newStrategyEvent1.args.strategyCalculation[1][2], 0);
    assert.equal(newStrategyEvent1.args.strategyCalculation[2][0], 10001);
    assert.equal(newStrategyEvent1.args.strategyCalculation[2][1], 20001);
    assert.equal(newStrategyEvent1.args.strategyCalculation[2][2], 1);
    assert.equal(newStrategyEvent1.args.strategyCalculation[3][0], 10002);
    assert.equal(newStrategyEvent1.args.strategyCalculation[3][1], 20002);
    assert.equal(newStrategyEvent1.args.strategyCalculation[3][2], 2);

    const strategyData = await starkDebtContract.callStatic.getStrategiesData();
    assert.equal(strategyData[0][0], 1);
    assert.equal(strategyData[0][1], 3);
    assert.equal(strategyData[0][2], 4);

    const strategyCalcul = await starkDebtContract.getStrategiesCalculation();
    assert.equal(strategyCalcul[0][0][0], 0);
    assert.equal(strategyCalcul[0][0][1], 1);
    assert.equal(strategyCalcul[0][0][2], 2);
    assert.equal(strategyCalcul[0][1][0], 10000);
    assert.equal(strategyCalcul[0][1][1], 2);
    assert.equal(strategyCalcul[0][1][2], 0);
    assert.equal(strategyCalcul[0][2][0], 10001);
    assert.equal(strategyCalcul[0][2][1], 20001);
    assert.equal(strategyCalcul[0][2][2], 1);
    assert.equal(strategyCalcul[0][3][0], 10002);
    assert.equal(strategyCalcul[0][3][1], 20002);
    assert.equal(strategyCalcul[0][3][2], 2);

    await expect(starkDebtContract.updateStrategy(dummy2Contract.address, 5000,[dummy2Contract.address, dummy2Contract.address], [sel1, sel3, sel4], calcul2)).to.be.revertedWith('Strategy not found');
    await expect(starkDebtContract.updateStrategy(dummy1Contract.address, 5000,[dummy2Contract.address, dummy2Contract.address], [sel1, sel4, sel4], calcul2)).to.be.revertedWith('different tab length');


    await expect(starkDebtContract.removeStrategy(1)).to.be.revertedWith('index out of range');
    const removeStrat = await starkDebtContract.removeStrategy(0);
    const receipt2 = await removeStrat.wait()
    const newStrategyEvent2 = receipt2.events.find(x => x.event === "StrategyRemoved");
    assert.equal(newStrategyEvent2.args.strategyRemoved, dummy1Contract.address);

    await expect(starkDebtContract.strategyContracts(dummy1Contract.address, 0)).to.be.reverted;
    await expect(starkDebtContract.strategyCheckdata(dummy1Contract.address, 0)).to.be.reverted;
    await expect(starkDebtContract.strategyCalculation(dummy1Contract.address, 0)).to.be.reverted;
    const maxdebtratioStrat = await starkDebtContract.strategyMaxDebtRatio(dummy1Contract.address);
    assert.equal(maxdebtratioStrat, 0);
  });

  it("Should add a strategy, update strategy parameters and delete it", async function () {
    const { starkDebtContract, dummy1Contract, dummy2Contract } = await loadFixture(deployTokenFixture);
    await starkDebtContract.addStrategy(dummy1Contract.address, 7000,[dummy1Contract.address, dummy1Contract.address], [sel1, sel2], calcul1);
    const updateStrat = await starkDebtContract.updateStrategy(dummy1Contract.address, 5000,[dummy2Contract.address, dummy2Contract.address, dummy2Contract.address], [sel1, sel3, sel4], calcul2);
    const receipt1 = await updateStrat.wait()
    const newStrategyEvent1 = receipt1.events.find(x => x.event === "StrategyUpdated");
    assert.equal(newStrategyEvent1.args.newStrategy, dummy1Contract.address);
    assert.equal(newStrategyEvent1.args.strategyMaxDebtRatio, 5000);
    assert.equal(newStrategyEvent1.args.strategyContracts[0], dummy2Contract.address);
    assert.equal(newStrategyEvent1.args.strategyContracts[1], dummy2Contract.address);
    assert.equal(newStrategyEvent1.args.strategyContracts[2], dummy2Contract.address);
    assert.equal(newStrategyEvent1.args.strategyCheckData[0], sel1);
    assert.equal(newStrategyEvent1.args.strategyCheckData[1], sel3);
    assert.equal(newStrategyEvent1.args.strategyCheckData[2], sel4);
    assert.equal(newStrategyEvent1.args.strategyCalculation[0][0], 0);
    assert.equal(newStrategyEvent1.args.strategyCalculation[0][1], 1);
    assert.equal(newStrategyEvent1.args.strategyCalculation[0][2], 2);
    assert.equal(newStrategyEvent1.args.strategyCalculation[1][0], 10000);
    assert.equal(newStrategyEvent1.args.strategyCalculation[1][1], 2);
    assert.equal(newStrategyEvent1.args.strategyCalculation[1][2], 0);
    assert.equal(newStrategyEvent1.args.strategyCalculation[2][0], 10001);
    assert.equal(newStrategyEvent1.args.strategyCalculation[2][1], 20001);
    assert.equal(newStrategyEvent1.args.strategyCalculation[2][2], 1);
    assert.equal(newStrategyEvent1.args.strategyCalculation[3][0], 10002);
    assert.equal(newStrategyEvent1.args.strategyCalculation[3][1], 20002);
    assert.equal(newStrategyEvent1.args.strategyCalculation[3][2], 2);

    const strategyData = await starkDebtContract.callStatic.getStrategiesData();
    assert.equal(strategyData[0][0], 1);
    assert.equal(strategyData[0][1], 3);
    assert.equal(strategyData[0][2], 4);

    const strategyCalcul = await starkDebtContract.getStrategiesCalculation();
    assert.equal(strategyCalcul[0][0][0], 0);
    assert.equal(strategyCalcul[0][0][1], 1);
    assert.equal(strategyCalcul[0][0][2], 2);
    assert.equal(strategyCalcul[0][1][0], 10000);
    assert.equal(strategyCalcul[0][1][1], 2);
    assert.equal(strategyCalcul[0][1][2], 0);
    assert.equal(strategyCalcul[0][2][0], 10001);
    assert.equal(strategyCalcul[0][2][1], 20001);
    assert.equal(strategyCalcul[0][2][2], 1);
    assert.equal(strategyCalcul[0][3][0], 10002);
    assert.equal(strategyCalcul[0][3][1], 20002);
    assert.equal(strategyCalcul[0][3][2], 2);

    await expect(starkDebtContract.updateStrategy(dummy2Contract.address, 5000,[dummy2Contract.address, dummy2Contract.address], [sel1, sel3, sel4], calcul2)).to.be.revertedWith('Strategy not found');
    await expect(starkDebtContract.updateStrategy(dummy1Contract.address, 5000,[dummy2Contract.address, dummy2Contract.address], [sel1, sel4, sel4], calcul2)).to.be.revertedWith('different tab length');


    await expect(starkDebtContract.removeStrategy(1)).to.be.revertedWith('index out of range');
    const removeStrat = await starkDebtContract.removeStrategy(0);
    const receipt2 = await removeStrat.wait()
    const newStrategyEvent2 = receipt2.events.find(x => x.event === "StrategyRemoved");
    assert.equal(newStrategyEvent2.args.strategyRemoved, dummy1Contract.address);

    await expect(starkDebtContract.strategyContracts(dummy1Contract.address, 0)).to.be.reverted;
    await expect(starkDebtContract.strategyCheckdata(dummy1Contract.address, 0)).to.be.reverted;
    await expect(starkDebtContract.strategyCalculation(dummy1Contract.address, 0)).to.be.reverted;
    const maxdebtratioStrat = await starkDebtContract.strategyMaxDebtRatio(dummy1Contract.address);
    assert.equal(maxdebtratioStrat, 0);
  });

  it("Should update general parameters", async function () {
    const { starkDebtContract } = await loadFixture(deployTokenFixture);
    const updatecairoPH = await starkDebtContract.updateCairoProgramHash(CAIRO_PROGRAM_HASH2);
    const receipt1 = await updatecairoPH.wait()
    const event1 = receipt1.events.find(x => x.event === "NewCairoProgramHash");
    assert.equal(event1.args.newCairoProgramHash, CAIRO_PROGRAM_HASH2);

    const CPHash = await starkDebtContract.cairoProgramHash();
    assert.equal(CPHash, CAIRO_PROGRAM_HASH2);

    const updatecairoV = await starkDebtContract.updateCairoVerifier(CAIRO_VERIFIER_2);
    const receipt2 = await updatecairoV.wait()
    const event2 = receipt2.events.find(x => x.event === "NewCairoVerifier");
    assert.equal(event2.args.newCairoVerifier, CAIRO_VERIFIER_2);

    const CVerif = await starkDebtContract.cairoVerifier();
    assert.equal(CVerif, CAIRO_VERIFIER_2);


    const updateSn = await starkDebtContract.updateStaleSnapshotPeriod(55);
    const receipt3 = await updateSn.wait()
    const event3 = receipt3.events.find(x => x.event === "NewStaleSnapshotPeriod");
    assert.equal(event3.args.newStaleSnapshotPeriod, 55);

    const SNVerif = await starkDebtContract.staleSnapshotPeriod();
    assert.equal(SNVerif, 55);


    const updateStale = await starkDebtContract.updateStalePeriod(25);
    const receipt4 = await updateStale.wait();
    const event4 = receipt4.events.find(x => x.event === "NewStalePeriod");
    assert.equal(event4.args.newStalePeriod, 25);

    const STVerif = await starkDebtContract.stalePeriod();
    assert.equal(STVerif, 25);

  });

  it("Should add strategies and execute saveSnapshot", async function () {
    const { starkDebtContract, dummy1Contract, dummy2Contract, owner } = await loadFixture(deployTokenFixture);
    await expect(starkDebtContract.saveSnapshot()).to.be.revertedWith('no strategies registered');
    await starkDebtContract.addStrategy(dummy1Contract.address, 7000,[dummy1Contract.address, dummy1Contract.address], [sel1, sel2], calcul1);
    await starkDebtContract.addStrategy(dummy2Contract.address, 6000,[dummy2Contract.address, dummy2Contract.address, dummy2Contract.address], [sel1, sel3, sel4], calcul2);
    const saveSnapshot = await starkDebtContract.saveSnapshot();
    const receipt1 = await saveSnapshot.wait()
    const event1 = receipt1.events.find(x => x.event === "NewSnapshot");
    assert.equal(event1.args.dataStrategies[0][0], 1);
    assert.equal(event1.args.dataStrategies[0][1], 2);
    assert.equal(event1.args.dataStrategies[1][0], 1);
    assert.equal(event1.args.dataStrategies[1][1], 3);
    assert.equal(event1.args.dataStrategies[1][2], 4);
    assert.equal(event1.args.calculation[0][0][0], 0);
    assert.equal(event1.args.calculation[0][0][1], 1);
    assert.equal(event1.args.calculation[0][0][2], 0);
    assert.equal(event1.args.calculation[0][1][0], 10000);
    assert.equal(event1.args.calculation[0][1][1], 0);
    assert.equal(event1.args.calculation[0][1][2], 2);
    assert.equal(event1.args.calculation[1][0][0], 0);
    assert.equal(event1.args.calculation[1][0][1], 1);
    assert.equal(event1.args.calculation[1][0][2], 2);
    assert.equal(event1.args.calculation[1][1][0], 10000);
    assert.equal(event1.args.calculation[1][1][1], 2);
    assert.equal(event1.args.calculation[1][1][2], 0);
    assert.equal(event1.args.calculation[1][2][0], 10001);
    assert.equal(event1.args.calculation[1][2][1], 20001);
    assert.equal(event1.args.calculation[1][2][2], 1);
    assert.equal(event1.args.calculation[1][3][0], 10002);
    assert.equal(event1.args.calculation[1][3][1], 20002);
    assert.equal(event1.args.calculation[1][3][2], 2);
    console.log(event1.args.timestamp);

    // cairo program output (with the previous input)

    const cairoOutput = ["0xA1379B44985D42B50FAB0F18582FF245","0xD4AB653D04C1F9EF70197D772B4BD38C", 2, 5000, 5000, 7];
    const verifySolution = await starkDebtContract.verifySolution(cairoOutput);
    const receipt2 = await verifySolution.wait()
    const event2 = receipt2.events.find(x => x.event === "NewSolution");
    assert.equal(event2.args.newApy, 7);
    assert.equal(event2.args.newDebtRatio[0], 5000);
    assert.equal(event2.args.newDebtRatio[1], 5000);
    assert.equal(event2.args.proposer, owner.address);

    const currentAPY = await starkDebtContract.currentAPY();
    const proposer = await starkDebtContract.proposer();
    
    assert.equal(currentAPY, 7);
    assert.equal(proposer, owner.address);

    const cairoOutput_error_input = ["0xA1376B44985D42B50FAB0F18582FF245","0xD4AB653D04C1F9EF70197D772B4BD38C", 2, 5000, 5000, 7];
    const cairoOutput_error_max_debt = ["0xA1379B44985D42B50FAB0F18582FF245","0xD4AB653D04C1F9EF70197D772B4BD38C", 2, 9000, 9000, 7];
    await expect(starkDebtContract.verifySolution(cairoOutput_error_input)).to.be.revertedWith('INVALID_INPUTS');
    await expect(starkDebtContract.verifySolution(cairoOutput_error_max_debt)).to.be.revertedWith('not allowed debt ratio');
  });
});