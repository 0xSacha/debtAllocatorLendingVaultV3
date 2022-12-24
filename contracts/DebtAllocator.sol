//SPDX-License-Identifier: UNLICENSED

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "./DebtAllocatorUtils.sol";

pragma solidity >=0.7.0 <0.9.0;

interface ICairoVerifier {
    function isValid(bytes32) external view returns (bool);
}

interface IStreamer {
    function token() external view returns (IERC20);

    function streamToStart(bytes32) external view returns (uint256);

    function withdraw(address from, address to, uint216 amountPerSec) external;

    function getStreamId(
        address from,
        address to,
        uint216 amountPerSec
    ) external view returns (bytes32);
}

contract DebtAllocator is Ownable, DebtAllocatorUtils {
    using SafeERC20 for IERC20;

    uint256 PRECISION = 10 ** 18;

    ICairoVerifier public cairoVerifier = ICairoVerifier(address(0));
    bytes32 public cairoProgramHash = 0x0;


    uint256[] public targetAllocation;

    // Everyone is free to propose a new solution, the address is stored so the user can get rewarded
    address public proposer;
    uint256 public lastUpdate;
    uint256 public strategiesHash;
    uint256 public inputHash;
    mapping(uint256 => uint256) public snapshotTimestamp;

    uint256 public staleSnapshotPeriod = 24 * 3600;

    // Rewards config
    address public rewardsPayer;
    address public rewardsStreamer;
    uint216 public rewardsPerSec;

    // 100% APY = 10^27, minimum increased = 10^23 = 0,01%
    uint256 public minimumApyIncreaseForNewSolution = 100000000000000000000000;

    constructor(address _cairoVerifier, bytes32 _cairoProgramHash) payable {
        updateCairoVerifier(_cairoVerifier);
        updateCairoProgramHash(_cairoProgramHash);
    }

    event StrategyAdded(
        address[] Strategies,
        uint256[] StrategiesCallLen,
        address[] Contracts,
        bytes4[] Selectors,
        bytes32[][] CallData,
        uint256[] Offset,
        uint256[] CalculationsLen,
        uint256[] Calculations,
        uint256[] ConditionsLen,
        uint256[] Conditions
    );
    event StrategyUpdated(
        address[] Strategies,
        uint256[] StrategiesCallLen,
        address[] Contracts,
        bytes4[] Selectors,
        bytes32[][] CallData,
        uint256[] Offset,
        uint256[] CalculationsLen,
        uint256[] Calculations,
        uint256[] ConditionsLen,
        uint256[] Conditions
    );
    event StrategyRemoved(
        address[] Strategies,
        uint256[] StrategiesCallLen,
        address[] Contracts,
        bytes4[] Selectors,
        bytes32[][] CallData,
        uint256[] Offset,
        uint256[] CalculationsLen,
        uint256[] Calculations,
        uint256[] ConditionsLen,
        uint256[] Conditions
    );

    event NewSnapshot(
        uint256[] dataStrategies,
        uint256[] calculation,
        uint256[] condition,
        uint256[] targetAllocations
    );
    event NewSolution(
        uint256 newApy,
        uint256[] newTargetAllocation,
        address proposer,
        uint256 timestamp
    );

    event NewCairoProgramHash(bytes32 newCairoProgramHash);
    event NewCairoVerifier(address newCairoVerifier);
    event NewStalePeriod(uint256 newStalePeriod);
    event NewStaleSnapshotPeriod(uint256 newStaleSnapshotPeriod);
    event targetAllocationForced(uint256[] newTargetAllocation);

    function updateRewardsConfig(
        address _rewardsPayer,
        address _rewardsStreamer,
        uint216 _rewardsPerSec
    ) external onlyOwner {
        bytes32 streamId = IStreamer(_rewardsStreamer).getStreamId(
            _rewardsPayer,
            address(this),
            _rewardsPerSec
        );
        require(
            IStreamer(_rewardsStreamer).streamToStart(streamId) > 0,
            "STREAM"
        );
        rewardsPayer = _rewardsPayer;
        rewardsStreamer = _rewardsStreamer;
        rewardsPerSec = _rewardsPerSec;
    }

    function updateCairoProgramHash(
        bytes32 _cairoProgramHash
    ) public onlyOwner {
        cairoProgramHash = _cairoProgramHash;
        emit NewCairoProgramHash(_cairoProgramHash);
    }

    function updateCairoVerifier(address _cairoVerifier) public onlyOwner {
        cairoVerifier = ICairoVerifier(_cairoVerifier);
        emit NewCairoVerifier(_cairoVerifier);
    }

    function updateStaleSnapshotPeriod(
        uint256 _staleSnapshotPeriod
    ) external onlyOwner {
        staleSnapshotPeriod = _staleSnapshotPeriod;
        emit NewStaleSnapshotPeriod(_staleSnapshotPeriod);
    }

    function forceTargetAllocation(
        uint256[] calldata _newTargetAllocation
    ) public onlyOwner {
        require(strategiesHash != 0, "NO_STRATEGIES");
        require(
            _newTargetAllocation.length == targetAllocation.length,
            "LENGTH"
        );
        for (uint256 j; j < _newTargetAllocation.length; j++) {
            targetAllocation[j] = _newTargetAllocation[j];
        }
        emit targetAllocationForced(_newTargetAllocation);
    }

    function saveSnapshot(
        PackedStrategies calldata _packedStrategies
    ) external {
        // Checks at least one strategy is registered
        require(strategiesHash != 0, "NO_STRATEGIES");

        // Checks strategies data is valid
        checkStrategyHash(_packedStrategies, strategiesHash);

        bytes[] memory checkdatas = selectorAndCallDataToBytes(_packedStrategies.selectors, _packedStrategies.callData);

        uint256[] memory dataStrategies = getStrategiesData(
            _packedStrategies.contracts,
            checkdatas,
            _packedStrategies.offset);

        inputHash = uint256(
            keccak256(
                abi.encodePacked(
                    dataStrategies,
                    _packedStrategies.calculations,
                    _packedStrategies.conditions
                )
            )
        );

        snapshotTimestamp[inputHash] = block.timestamp;
        // TODO: do we need current debt in each strategy? (to be able to take into account withdrawals)
        emit NewSnapshot(
            dataStrategies,
            _packedStrategies.calculations,
            _packedStrategies.conditions,
            targetAllocation
        );
    }

    function verifySolution(
        uint256[] calldata programOutput
    ) external returns (bytes32) {
        // NOTE: Check current snapshot not stale
        uint256 _inputHash = inputHash;
        uint256 _snapshotTimestamp = snapshotTimestamp[_inputHash];

        require(
            _snapshotTimestamp + staleSnapshotPeriod > block.timestamp,
            "STALE_SNAPSHOT"
        );

        // NOTE: We get the data from parsing the program output
        (
            uint256 inputHash_,
            uint256[] memory currentTargetAllocation,
            uint256[] memory newTargetAllocation,
            uint256 currentSolution,
            uint256 newSolution
        ) = parseProgramOutput(programOutput);

        // check inputs
        require(inputHash_ == _inputHash, "HASH");

        // check target allocation len
        require(
            targetAllocation.length == currentTargetAllocation.length &&
                targetAllocation.length == newTargetAllocation.length,
            "TARGET_ALLOCATION_LENGTH"
        );

        // check if the new solution better than previous one
        require(
            newSolution - minimumApyIncreaseForNewSolution >= currentSolution,
            "TOO_BAD"
        );

        // Check with cairoVerifier
        bytes32 outputHash = keccak256(abi.encodePacked(programOutput));
        bytes32 fact = keccak256(
            abi.encodePacked(cairoProgramHash, outputHash)
        );

        require(cairoVerifier.isValid(fact), "MISSING_PROOF");

        targetAllocation = newTargetAllocation;
        lastUpdate = block.timestamp;

        sendRewardsToCurrentProposer();
        proposer = msg.sender;

        emit NewSolution(
            newSolution,
            newTargetAllocation,
            msg.sender,
            block.timestamp
        );
        return (fact);
    }

    // =============== REWARDS =================
    function sendRewardsToCurrentProposer() internal {
        IStreamer _rewardsStreamer = IStreamer(rewardsStreamer);
        if (address(_rewardsStreamer) == address(0)) {
            return;
        }
        bytes32 streamId = _rewardsStreamer.getStreamId(
            rewardsPayer,
            address(this),
            rewardsPerSec
        );
        if (_rewardsStreamer.streamToStart(streamId) == 0) {
            // stream does not exist
            return;
        }
        IERC20 _rewardsToken = IERC20(_rewardsStreamer.token());
        // NOTE: if the stream does not have enough to pay full amount, it will pay less than expected
        // WARNING: if this happens and the proposer is changed, the old proposer will lose the rewards
        // TODO: create a way to ensure previous proposer gets the rewards even when payers balance is not enough (by saving how much he's owed)
        _rewardsStreamer.withdraw(rewardsPayer, address(this), rewardsPerSec);
        uint256 rewardsBalance = _rewardsToken.balanceOf(address(this));
        _rewardsToken.safeTransfer(proposer, rewardsBalance);
    }

    function claimRewards() external {
        require(msg.sender == proposer, "NOT_ALLOWED");
        sendRewardsToCurrentProposer();
    }

    // ============== STRATEGY MANAGEMENT ================

    function addStrategy(
        PackedStrategies calldata _packedStrategies,
        address _newStrategy,
        StrategyParam calldata _newStrategyParam
    ) external onlyOwner {
        // Checks previous strategies data valid

        if (strategiesHash != 0) {
            checkStrategyHash(_packedStrategies, strategiesHash);
        } else {
            require(_packedStrategies.addresses.length == 0, "FIRST_DATA");
        }

        for (uint256 i = 0; i < _packedStrategies.addresses.length; i++) {
            if (_packedStrategies.addresses[i] == _newStrategy) {
                revert("STRATEGY_EXISTS");
            }
        }

        // Checks call data valid
        checkValidityOfData(_newStrategyParam);

        // Build new arrays for the Strategy Hash and the Event
        address[] memory strategies = appendAddressToArray(
            _packedStrategies.addresses,
            _newStrategy
        );

        uint256[] memory strategiesCallLen = appendUint256ToArray(
            _packedStrategies.callLen,
            _newStrategyParam.callLen
        );

        address[] memory contracts = concatenateAddressArrayToAddressArray(
            _packedStrategies.contracts, 
            _newStrategyParam.contracts);

        bytes4[] memory selectors = concatenateBytes4ArrayToBytes4(
            _packedStrategies.selectors, 
            _newStrategyParam.selectors
        );

        bytes32[][] memory callData = concatenateDoubleArrayBytes32ArrayToDoubleArrayBytes32(
            _packedStrategies.callData, 
            _newStrategyParam.callData
        );
       

        uint256[] memory offset = concatenateUint256ArrayToUint256Array(
            _packedStrategies.offset,
            _newStrategyParam.offset
        );

        uint256[] memory calculationsLen = appendUint256ToArray(
            _packedStrategies.calculationsLen,
            _newStrategyParam.calculationsLen
        );

        uint256[] memory calculations = concatenateUint256ArrayToUint256Array(
            _packedStrategies.calculations,
            _newStrategyParam.calculations
        );

        uint256[] memory conditionsLen = appendUint256ToArray(
            _packedStrategies.conditionsLen,
            _newStrategyParam.conditionsLen
        );

        uint256[] memory conditions = concatenateUint256ArrayToUint256Array(
            _packedStrategies.conditions,
            _newStrategyParam.conditions
        );

        bytes32[] memory callDataReduced = getReducedBytes32Array(callData);

        strategiesHash = uint256(
            keccak256(
                abi.encodePacked(
                    strategies,
                    strategiesCallLen,
                    contracts,
                    selectors,
                    callDataReduced,
                    offset,
                    calculationsLen,
                    calculations,
                    conditionsLen,
                    conditions
                )
            )
        );

        // New strategy allocation always set to 0, people can then send new solution
        targetAllocation.push(0);

        emit StrategyAdded(
            strategies,
            strategiesCallLen,
            contracts,
            selectors,
            callData,
            offset,
            calculationsLen,
            calculations,
            conditionsLen,
            conditions
        );
    }

    // TODO: use utils functions
    function updateStrategy(
        PackedStrategies memory _packedStrategies,
        uint256 indexStrategyToUpdate,
        StrategyParam memory _newStrategyParam
    ) external onlyOwner {
        // Checks at least one strategy is registered
        require(strategiesHash != 0, "NO_STRATEGIES");

        checkStrategyHash(_packedStrategies, strategiesHash);

        // Checks index in range
        require(
            indexStrategyToUpdate < _packedStrategies.addresses.length,
            "INDEX_OUT_OF_RANGE"
        );

        // Checks call data valid
        checkValidityOfData(_newStrategyParam);

        // Build new arrays for the Strategy Hash and the Event
        uint256[] memory strategiesCallLen = updateUint256Array(_packedStrategies.callLen, _newStrategyParam.callLen, indexStrategyToUpdate);
        uint256[] memory calculationsLen = updateUint256Array(_packedStrategies.calculationsLen, _newStrategyParam.calculationsLen, indexStrategyToUpdate);
        uint256[] memory conditionsLen =updateUint256Array(_packedStrategies.conditionsLen, _newStrategyParam.conditionsLen, indexStrategyToUpdate);
        address[] memory contracts = updateAddressArrayWithLen(_packedStrategies.callLen, _packedStrategies.contracts, _newStrategyParam.callLen, _newStrategyParam.contracts, indexStrategyToUpdate);
        bytes4[] memory selectors = updateBytes4ArrayWithLen(_packedStrategies.callLen, _packedStrategies.selectors, _newStrategyParam.callLen, _newStrategyParam.selectors, indexStrategyToUpdate);
        bytes32[][] memory callData = updateBytes32ArrayWithLen(_packedStrategies.callLen, _packedStrategies.callData, _newStrategyParam.callLen, _newStrategyParam.callData, indexStrategyToUpdate);
        uint256[] memory offset = updateUint256ArrayWithLen(_packedStrategies.callLen, _packedStrategies.offset, _newStrategyParam.callLen, _newStrategyParam.offset, indexStrategyToUpdate);
        uint256[] memory calculations = updateUint256ArrayWithLen(_packedStrategies.calculationsLen, _packedStrategies.calculations, _newStrategyParam.calculationsLen, _newStrategyParam.calculations, indexStrategyToUpdate);
        uint256[] memory conditions = updateUint256ArrayWithLen(_packedStrategies.conditionsLen, _packedStrategies.conditions, _newStrategyParam.callLen, _newStrategyParam.conditions, indexStrategyToUpdate);
        
        bytes32[] memory callDataReduced = getReducedBytes32Array(callData);

        strategiesHash = uint256(
            keccak256(
                abi.encodePacked(
                    _packedStrategies.addresses,
                    strategiesCallLen,
                    contracts,
                    callDataReduced,
                    offset,
                    calculationsLen,
                    calculations,
                    conditionsLen,
                    conditions
                )
            )
        );

        emit StrategyUpdated(
            _packedStrategies.addresses,
            strategiesCallLen,
            contracts,
            selectors,
            callData,
            offset,
            calculationsLen,
            calculations,
            conditionsLen,
            conditions
        );
    }


    function removeStrategy(
        PackedStrategies memory _packedStrategies,
        uint256 indexStrategyToRemove
    ) external onlyOwner {
        // Checks at least one strategy is registered
        require(strategiesHash != 0, "NO_STRATEGIES");

        // Checks strategies data is valid
        checkStrategyHash(_packedStrategies, strategiesHash);

        // Checks index in range
        require(indexStrategyToRemove < _packedStrategies.addresses.length);

        // Build new arrays for the Strategy Hash and the Event
        uint256[] memory strategiesCallLen = removeUint256Array(_packedStrategies.callLen, indexStrategyToRemove);
        uint256[] memory calculationsLen = removeUint256Array(_packedStrategies.calculationsLen, indexStrategyToRemove);
        uint256[] memory conditionsLen =removeUint256Array(_packedStrategies.conditionsLen, indexStrategyToRemove);
        address[] memory contracts = removeAddressArrayWithLen(_packedStrategies.callLen, _packedStrategies.contracts, indexStrategyToRemove);
        bytes4[] memory selectors = removeBytes4ArrayWithLen(_packedStrategies.callLen, _packedStrategies.selectors, indexStrategyToRemove);
        bytes32[][] memory callData = removeBytes32ArrayWithLen(_packedStrategies.callLen, _packedStrategies.callData, indexStrategyToRemove);
        uint256[] memory offset = removeUint256ArrayWithLen(_packedStrategies.callLen, _packedStrategies.offset, indexStrategyToRemove);
        uint256[] memory calculations = removeUint256ArrayWithLen(_packedStrategies.calculationsLen, _packedStrategies.calculations, indexStrategyToRemove);
        uint256[] memory conditions = removeUint256ArrayWithLen(_packedStrategies.conditionsLen, _packedStrategies.conditions, indexStrategyToRemove);
        
        bytes32[] memory callDataReduced = getReducedBytes32Array(callData);
        strategiesHash = uint256(
            keccak256(
                abi.encodePacked(
                    _packedStrategies.addresses,
                    strategiesCallLen,
                    contracts,
                    selectors,
                    callDataReduced,
                    offset,
                    calculationsLen,
                    calculations,
                    conditionsLen,
                    conditions
                )
            )
        );
        emit StrategyRemoved(
            _packedStrategies.addresses,
            strategiesCallLen,
            contracts,
            selectors,
            callData,
            offset,
            calculationsLen,
            calculations,
            conditionsLen,
            conditions
        );
    }

    //Can't set only view, .call potentially modify state (should not arrive)
    function getStrategiesData(
        address[] calldata contracts,
        bytes[] memory checkdata,
        uint256[] calldata offset
    ) public returns (uint256[] memory dataStrategies) {
        uint256[] memory dataStrategies_ = new uint256[](contracts.length);
        for (uint256 j; j < contracts.length; j++) {
            (, bytes memory data) = contracts[j].call(checkdata[j]);
            dataStrategies_[j] = uint256(bytesToBytes32(data, offset[j]));
        }
        return (dataStrategies_);
    }

    //     function updateTargetAllocation(address[] memory strategies) internal {
    //         uint256[] memory realAllocations = new uint256[](strategies.length);
    //         uint256 cumulativeAmountRealAllocations = 0;
    //         uint256 cumulativeAmountTargetAllocations = 0;
    //         for (uint256 j; j < strategies.length; j++) {
    //             realAllocations[j] = IStrategy(strategies[j]).totalAssets();
    //             cumulativeAmountRealAllocations += realAllocations[j];
    //             cumulativeAmountTargetAllocations += targetAllocation[j];
    //         }
    //
    //         if (cumulativeAmountTargetAllocations == 0) {
    //             targetAllocation = realAllocations;
    //         } else {
    //             if (
    //                 cumulativeAmountTargetAllocations <=
    //                 cumulativeAmountRealAllocations
    //             ) {
    //                 uint256 diff = cumulativeAmountRealAllocations -
    //                     cumulativeAmountTargetAllocations;
    //                 // We need to add this amount respecting the different strategies allocation ratio
    //                 for (uint256 i = 0; i < strategies.length; i++) {
    //                     uint256 strategyAllocationRatio = (PRECISION *
    //                         targetAllocation[i]) /
    //                         cumulativeAmountTargetAllocations;
    //                     targetAllocation[i] +=
    //                         (strategyAllocationRatio * diff) /
    //                         PRECISION;
    //                 }
    //             } else {
    //                 uint256 diff = cumulativeAmountTargetAllocations -
    //                     cumulativeAmountRealAllocations;
    //                 // We need to substract this amount respecting the different strategies allocation ratio
    //                 for (uint256 i = 0; i < strategies.length; i++) {
    //                     uint256 strategyAllocationRatio = (PRECISION *
    //                         targetAllocation[i]) /
    //                         cumulativeAmountTargetAllocations;
    //                     targetAllocation[i] -=
    //                         (strategyAllocationRatio * diff) /
    //                         PRECISION;
    //                 }
    //             }
    //         }
    //     }
    //

}
