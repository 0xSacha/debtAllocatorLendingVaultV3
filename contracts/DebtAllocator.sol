//SPDX-License-Identifier: UNLICENSED

import "OpenZeppelin/openzeppelin-contracts@4.8.0/contracts/access/Ownable.sol";
import "OpenZeppelin/openzeppelin-contracts@4.8.0/contracts/security/Pausable.sol";


pragma solidity >=0.7.0 <0.9.0;


interface ICairoVerifier {
    function isValid(bytes32) external view returns (bool);
}

contract DebtAllocator is Ownable, Pausable {

    ICairoVerifier public cairoVerifier = ICairoVerifier(address(0));
    bytes32 public cairoProgramHash = 0x0;

    address[] public strategies;
    uint256[] public debtRatios;

    //mapping to get strategy inputs, contracts address+selector
    mapping(address => address[]) public strategyContracts;
    mapping(address => bytes[]) public strategyCheckdata;
    mapping(address => uint256[]) public strategyOffset;
    mapping(address => uint256[]) public strategyCalculation;
    mapping(address => uint256[]) public strategyCondition;

    //Some strategies may be risky or involve lock, their allocation should be limited in the vault
    mapping(address => uint16) public strategyMaxDebtRatio;

    // Everyone is free to propose a new solution, the address is stored so the user can get rewarded
    address public proposer;
    uint256 public proposerPerformance;
    uint256 public currentAPY;
    uint256 public lastUpdate;
    uint256 public inputHash;
    mapping(uint256 => uint256) public snapshotTimestamp;

    uint256 public staleSnapshotPeriod = 3 * 3600;
    // uint256 public stalePeriod = 24 * 3600;


    // 100% APY = 10^27, minimum increased = 10^23 = 0,01%
    uint256 public minimumApyIncreaseForNewSolution = 100000000000000000000000;

    constructor(address _cairoVerifier, bytes32 _cairoProgramHash) payable {
        updateCairoVerifier(_cairoVerifier);
        updateCairoProgramHash(_cairoProgramHash);
    }

    event NewSnapshot(uint256[][] dataStrategies, uint256[][] calculation, uint256[][] condition,uint256 inputHash, uint256 timestamp);
    event NewStrategy(address newStrategy, uint16 strategyMaxDebtRatio,address[] strategyContracts,bytes[] strategyCheckData, uint256[] strategyCalculation);
    event StrategyUpdated(address newStrategy, uint16 strategyMaxDebtRatio,address[] strategyContracts,bytes[] strategyCheckData, uint256[] strategyCalculation);
    event StrategyRemoved(address strategyRemoved);
    event NewCairoProgramHash(bytes32 newCairoProgramHash);
    event NewCairoVerifier(address newCairoVerifier);
    // event NewStalePeriod(uint256 newStalePeriod);
    event NewStaleSnapshotPeriod(uint256 newStaleSnapshotPeriod);
    event NewSolution(uint256 newApy, uint256[] newDebtRatio, address proposer, uint256 proposerPerformance,uint256 timestamp);
    event debtRatioForced(uint256[] newDebtRatio);
    // TODO: add role based access control to invoke those functions

    function updateCairoProgramHash(bytes32 _cairoProgramHash) public onlyOwner {
        cairoProgramHash = _cairoProgramHash;
        emit NewCairoProgramHash(_cairoProgramHash);
    }

    function pause() public onlyOwner {
        _pause();
    }

    function unpause() public onlyOwner {
        _unpause();
    }

    function updateCairoVerifier(address _cairoVerifier) public onlyOwner {
        cairoVerifier = ICairoVerifier(_cairoVerifier);
        emit NewCairoVerifier(_cairoVerifier);
    }

    // function updateStalePeriod(uint256 _stalePeriod) public {
    //     // TODO: put some limits?
    //     stalePeriod = _stalePeriod;
    //     emit NewStalePeriod(_stalePeriod);
    // }

    function updateStaleSnapshotPeriod(uint256 _staleSnapshotPeriod) public onlyOwner {
        // TODO: put some limits?
        staleSnapshotPeriod = _staleSnapshotPeriod;
        emit NewStaleSnapshotPeriod(_staleSnapshotPeriod);
    }

    function forceDebtRatio(uint256[] memory _new_debt_ratio) public onlyOwner whenPaused {
        require(_new_debt_ratio.length == debtRatios.length, "INVALIDE_LENGTH");
        uint256 cumulative_debt_ratio = 0;
        for(uint256 j; j < strategies.length; j++) {
            debtRatios[j] = _new_debt_ratio[j];
            cumulative_debt_ratio += _new_debt_ratio[j];
        }
        require(_new_debt_ratio.length == debtRatios.length, "INVALIDE_DEBT_RATIO_SUM");
        emit debtRatioForced(_new_debt_ratio);
    }

    function addStrategy(address strategy, uint16 maxDebtRatio,address[] memory contracts, bytes[] memory checkdata, uint256[] memory offset, uint256[] memory calculations, uint256[] memory conditions) external onlyOwner{
        strategies.push(strategy);
        require(strategyMaxDebtRatio[strategy] == 0, "STRATEGY_EXISTS");
        require(contracts.length == checkdata.length, "INVALID_TAB_LEN_1");
        require(contracts.length == offset.length, "INVALID_TAB_LEN_1");
        for(uint256 i; i < contracts.length; i++) {
            strategyContracts[strategy].push(contracts[i]);
            strategyCheckdata[strategy].push(checkdata[i]);
        }

        for(uint256 j; j < offset.length; j++) {
            strategyOffset[strategy].push(offset[j]);
        }

        for(uint256 k; k < calculations.length; k++) {
            strategyCalculation[strategy].push(calculations[k]);
        }

        for(uint256 l; l < conditions.length; l++) {
            strategyCondition[strategy].push(conditions[l]);
        }

        strategyMaxDebtRatio[strategy] = maxDebtRatio;

        debtRatios.push(0);

        emit NewStrategy(strategy, strategyMaxDebtRatio[strategy] ,strategyContracts[strategy], strategyCheckdata[strategy], strategyCalculation[strategy]);
    }

    function updateStrategy(address strategy, uint16 maxDebtRatio,address[] memory contracts, bytes[] memory checkdata, uint256[] memory offset, uint256[] memory calculations, uint256[] memory conditions) external onlyOwner {
        require(strategyMaxDebtRatio[strategy] != 0, "Strategy not found");
        require(contracts.length == checkdata.length, "INVALID_TAB_LEN_1");
        require(contracts.length == offset.length, "INVALID_TAB_LEN_1");
        delete strategyContracts[strategy];
        delete strategyCheckdata[strategy];
        delete strategyOffset[strategy];
        delete strategyCalculation[strategy];
        delete strategyCondition[strategy];
        delete strategyMaxDebtRatio[strategy];

        for(uint256 i; i < contracts.length; i++) {
            strategyContracts[strategy].push(contracts[i]);
            strategyCheckdata[strategy].push(checkdata[i]);
        }

        for(uint256 j; j < offset.length; j++) {
            strategyOffset[strategy].push(offset[j]);
        }

        for(uint256 k; k < calculations.length; k++) {
            strategyCalculation[strategy].push(calculations[k]);
        }

        for(uint256 l; l < conditions.length; l++) {
            strategyCondition[strategy].push(conditions[l]);
        }

        strategyMaxDebtRatio[strategy] = maxDebtRatio;
        emit StrategyUpdated(strategy, strategyMaxDebtRatio[strategy] ,strategyContracts[strategy], strategyCheckdata[strategy], strategyCalculation[strategy]);
    }

    function removeStrategy(uint256 index) external onlyOwner{
        require(index < strategies.length && index >= 0, "INDEX_OUT_OF_RANGE");
        require(debtRatios[index] == 0, "DEBT_RATIO_NOT_NUL");
        address strategy = strategies[index];
        delete strategyContracts[strategy];
        delete strategyCheckdata[strategy];
        delete strategyOffset[strategy];
        delete strategyCalculation[strategy];
        delete strategyCondition[strategy];
        delete strategyMaxDebtRatio[strategy];
        strategies[index] = strategies[strategies.length-1];
        debtRatios[index] = debtRatios[strategies.length-1];
        strategies.pop();
        debtRatios.pop();
        emit StrategyRemoved(strategy);
    }




    //Can't set only view, .call potentially modify state (should not arrive)
    function getStrategiesData() public returns(uint256[][] memory _dataStrategies) {
        uint256[][] memory dataStrategies = new uint256[][](strategies.length);
        for(uint256 i; i < dataStrategies.length; i++) {
            bytes[] memory checkdata = strategyCheckdata[strategies[i]];
            uint256[] memory offset = strategyOffset[strategies[i]];
            address[] memory contracts = strategyContracts[strategies[i]];
            uint256[] memory dataStrategy = new uint256[](contracts.length);
            for(uint256 j; j < checkdata.length; j++) {
                (bool success, bytes memory data) = contracts[j].call(checkdata[j]);
                require(success == true, "call didn't succeed");
                dataStrategy[j] = uint256(bytesToBytes32(data, offset[j]));
            }
            dataStrategies[i] = dataStrategy;
        }
       return(dataStrategies);
    }

    function getStrategiesCalculation() public view returns(uint256[][] memory _calculationStrategies) {
        uint256[][] memory calculationStrategies = new uint256[][](strategies.length);
        for(uint256 i; i < calculationStrategies.length; i++) {
            calculationStrategies[i] = strategyCalculation[strategies[i]];
        }
       return(calculationStrategies);
    }

    function getStrategiesCondition() public view returns(uint256[][] memory _conditionStrategies) {
        uint256[][] memory conditionStrategies = new uint256[][](strategies.length);
        for(uint256 i; i < conditionStrategies.length; i++) {
            conditionStrategies[i] = strategyCondition[strategies[i]];
        }
       return(conditionStrategies);
    }

    function saveSnapshot() external {
        require(strategies.length > 0, "no strategies registered");

        uint256[][] memory dataStrategies = getStrategiesData(); 

        uint256 dataStratTotalLen = 0;
        for(uint256 i; i < dataStrategies.length; i++) {
            dataStratTotalLen += dataStrategies[i].length;
        }

        uint256 index1 = 0;
        uint256[] memory dataStrategiesConcat = new uint256[](dataStratTotalLen);
        for(uint256 k = 0; k < dataStrategies.length; k++) {
            for(uint256 l = 0; l < dataStrategies[k].length; l++) {
                dataStrategiesConcat[index1] = dataStrategies[k][l];
                index1++;
            }
        }

        uint256[][] memory calculationStrategies = getStrategiesCalculation();
        uint256 calculationStratTotalLen = 0;
        for(uint256 j; j < calculationStrategies.length; j++) {
            calculationStratTotalLen += calculationStrategies[j].length;
        }

        uint256 index2 = 0;
        uint256[] memory calculationStrategiesConcat = new uint256[](calculationStratTotalLen);
        for(uint256 m = 0; m < calculationStrategies.length; m++) {
            for(uint256 n = 0; n < calculationStrategies[m].length; n++) {
                calculationStrategiesConcat[index2] = calculationStrategies[m][n];
                index2++;
            }
        }

        uint256[][] memory conditionStrategies = getStrategiesCondition();
        uint256 conditionsStratTotalLen = 0;
        for(uint256 o; o < conditionStrategies.length; o++) {
            conditionsStratTotalLen += conditionStrategies[o].length;
        }

        uint256 index3 = 0;
        uint256[] memory conditionStrategiesConcat = new uint256[](conditionsStratTotalLen);
        for(uint256 p = 0; p < conditionStrategies.length; p++) {
            for(uint256 n = 0; n < conditionStrategies[p].length; n++) {
                conditionStrategiesConcat[index3] = conditionStrategies[p][n];
                index3++;
            }
        }

        inputHash = uint256(keccak256(abi.encodePacked(dataStrategiesConcat, calculationStrategiesConcat, conditionStrategiesConcat)));

        snapshotTimestamp[inputHash] = block.timestamp;

        emit NewSnapshot(dataStrategies, calculationStrategies, conditionStrategies,inputHash, block.timestamp);
    }

    

    function wutobo(uint256[] memory programOutput) external{
        require(1 == 2, "wuttetetetetetettt");
        uint256 _snapshotTimestamp = snapshotTimestamp[inputHash];
    }

    function verifySolution(uint256[] memory programOutput) external whenNotPaused returns(bytes32){
        // NOTE: Check current snapshot not stale
        uint256 _snapshotTimestamp = snapshotTimestamp[inputHash];
        require(_snapshotTimestamp + staleSnapshotPeriod > block.timestamp, "STALE_SNAPSHOT_PERIOD");

        // NOTE: We get the data from parsing the program output
        (uint256 inputHash_,  uint256[] memory current_debt_ratio, uint256[] memory new_debt_ratio, uint256 current_solution, uint256 new_solution) = parseProgramOutput(programOutput); 
        // check inputs
        require(inputHash_==inputHash, "INVALID_INPUTS");
            
        // check current debt ration and new debt ratio
        checkAllowedDebtRatio(current_debt_ratio, new_debt_ratio);

        // check if the new solution better than previous one
        require(new_solution - minimumApyIncreaseForNewSolution >= current_solution,"NEW_SOLUTION_TOO_BAD");
        
        // Check with cairoVerifier
        bytes32 outputHash = keccak256(abi.encodePacked(programOutput));
        bytes32 fact = keccak256(abi.encodePacked(cairoProgramHash, outputHash));
        require(cairoVerifier.isValid(fact), "MISSING_CAIRO_PROOF");

        // check no one has improven it in stale period (in case market conditions deteriorated)
        // require(_newSolution > currentAPY || block.timestamp - lastUpdate >= stalePeriod, "WRONG_SOLUTION");
        require(1 == 2, "wtf1");
        currentAPY = new_solution;
        debtRatios = new_debt_ratio;
        lastUpdate = block.timestamp;
        proposer = msg.sender;
        proposerPerformance = new_solution - current_solution;

        require(1 == 2, "wtf2");

        emit NewSolution(new_solution, new_debt_ratio, msg.sender, proposerPerformance,block.timestamp);
        return(fact);
    }

    function parseProgramOutput(uint256[] memory programOutput) public view returns (uint256 _inputHash, uint256[] memory _current_debt_ration, uint256[] memory _new_debt_ration, uint256 _current_solution, uint256 _new_solution) {
        uint256 inputHashUint256 = programOutput[0] << 128;
        inputHashUint256 += programOutput[1];
        uint256[] memory current_debt_ratio = new uint256[](strategies.length);
        uint256[] memory new_debt_ratio = new uint256[](strategies.length);

        for(uint256 i = 0; i < strategies.length ; i++) {
            // NOTE: skip the 2 first value + array len 
            current_debt_ratio[i] = programOutput[i + 3];
            new_debt_ratio[i] = programOutput[i + 4 + strategies.length];
        }
        return(inputHashUint256, current_debt_ratio, new_debt_ratio, programOutput[programOutput.length - 2], programOutput[programOutput.length - 1]);
    }

    function checkAllowedDebtRatio(uint256[] memory _current_debt_ratio, uint256[] memory _new_debt_ratio) public view {
        require(_current_debt_ratio.length == debtRatios.length,"INVALID_NEW_DEBT_RATIO");
        require(_new_debt_ratio.length == debtRatios.length,"INVALID_NEW_DEBT_RATIO");
        uint256 cumulative_new_debt = 0;
        for(uint256 i; i < debtRatios.length; i++) {
            require(_new_debt_ratio[i] <= strategyMaxDebtRatio[strategies[i]],"INVALID_NEW_DEBT_RATIO");
            require(_current_debt_ratio[i] == debtRatios[i], "INVALID_CURRENT_DEBT_RATIO");
            cumulative_new_debt += _new_debt_ratio[i];
        }
        require(cumulative_new_debt == 10000,"INVALID_NEW_DEBT_RATIO");
    }

        
    function bytesToBytes32(bytes memory b, uint offset) private pure returns (bytes32) {
        bytes32 out;
        for (uint i = 0; i < 32; i++) {
            out |= bytes32(b[offset + i] & 0xFF) >> (i * 8);
        }
        return out;
    }
}

