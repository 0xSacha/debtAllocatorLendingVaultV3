//SPDX-License-Identifier: UNLICENSED

import "@openzeppelin/access/Ownable.sol";
import "@openzeppelin/token/ERC20/IERC20.sol";
import "@openzeppelin/token/ERC20/utils/SafeERC20.sol";
import "./DebtAllocatorLib.sol";


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

contract DebtAllocator is Ownable {
    using SafeERC20 for IERC20;

    ICairoVerifier public cairoVerifier = ICairoVerifier(address(0));
    bytes32 public cairoProgramHash = 0x0;


    uint256[] public targetAllocation;

    // Everyone is free to propose a new solution, the address is stored so the user can get rewarded
    address public proposer;
    uint256 public lastUpdate;
    uint256 public strategiesHash;
    uint256 public inputHash;
    mapping(uint256 => uint256) public snapshotTimestamp;

    uint256 public staleSnapshotPeriod = STALE_SNAPSHOT_PERIOD;

    // Rewards config
    address public rewardsPayer;
    address public rewardsStreamer;
    uint216 public rewardsPerSec;

    // 100% APY = 10^27, minimum increased = 10^23 = 0,01%
    uint256 public minimumApyIncreaseForNewSolution = MINIMUM_APY_INCREASE;


    event StrategyAdded(
        PackedStrategies Strategies
    );

    event StrategyUpdated(
        PackedStrategies Strategies
    );

    event StrategyRemoved(
        PackedStrategies Strategies
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
    event NewMinimumApyIncrease(uint256 newStaleSnapshotPeriod);
    // event TargetAllocationForced(uint256[] newTargetAllocation);


    constructor(address _cairoVerifier, bytes32 _cairoProgramHash) payable {
        updateCairoVerifier(_cairoVerifier);
        updateCairoProgramHash(_cairoProgramHash);
    }

    //  // ============== PARAMETERS MANAGEMENT  ================

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

    function updateMinimumApyIncrease(
        uint256 _minimumApyIncrease
    ) external onlyOwner {
        minimumApyIncreaseForNewSolution = _minimumApyIncrease;
        emit NewMinimumApyIncrease(_minimumApyIncrease);
    }


    // ============== FRESH DATA  ================

    function saveSnapshot(
        PackedStrategies calldata _packedStrategies
    ) external {

        StrategiesUtils.checkAtLeastOneStrategy(strategiesHash);

        // Checks strategies data is valid
        StrategiesUtils.checkStrategiesHash(_packedStrategies, strategiesHash);

        bytes[] memory checkdatas = StrategiesUtils.selectorAndCallDataToBytes(_packedStrategies.selectors, _packedStrategies.callData);
        uint256[] memory dataStrategies = StrategiesUtils.getStrategiesData(
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


     // ============== SOLUTION  ================

    function verifySolution(
        uint256[] calldata programOutput
    ) external returns (bytes32) {

        // NOTE: Check current snapshot not stale
        StrategiesUtils.checkSnapshotNotStaled(snapshotTimestamp[inputHash], staleSnapshotPeriod, block.timestamp);
        
        // NOTE: We get the data from parsing the program output
        ProgramOutput memory programOutputParsed =  StrategiesUtils.parseProgramOutput(programOutput);
        StrategiesUtils.checkProgramOutput(programOutputParsed, inputHash, targetAllocation, minimumApyIncreaseForNewSolution);

        // Check with cairoVerifier
        bytes32 fact = StrategiesUtils.getFact(programOutput, cairoProgramHash);
        require(cairoVerifier.isValid(fact), "PROOF");

        targetAllocation = programOutputParsed.newTargetAllocation;
        lastUpdate = block.timestamp;
        sendRewardsToCurrentProposer();
        proposer = msg.sender;

        emit NewSolution(
            programOutputParsed.newSolution,
            programOutputParsed.newTargetAllocation,
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
        StrategiesUtils.checkMessageSenderIsProposer(msg.sender, proposer);
        sendRewardsToCurrentProposer();
    }



    // ============== STRATEGY MANAGEMENT ================

    function addStrategy(
        PackedStrategies calldata _packedStrategies,
        address _newStrategy,
        StrategyParam calldata _newStrategyParam
    ) external onlyOwner {

        // Checks data valid
        StrategiesUtils.checkValidityOfPreviousAndNewData(strategiesHash,_packedStrategies, _newStrategy,_newStrategyParam);

        // get New array and calculate Hash
        PackedStrategies memory newPackedStrategies = ArrayUtils.getPackedStrategiesAfterAdd(_packedStrategies, _newStrategy, _newStrategyParam);
        strategiesHash = StrategiesUtils.getStrategiesHash(newPackedStrategies);

        // New strategy allocation always set to 0, people can then send new solution
        targetAllocation.push(0);

        emit StrategyAdded(newPackedStrategies);
    }

    // TODO: use utils functions
    function updateStrategy(
        PackedStrategies memory _packedStrategies,
        uint256 indexStrategyToUpdate,
        StrategyParam memory _newStrategyParam
    ) external onlyOwner {

        StrategiesUtils.checkAtLeastOneStrategy(strategiesHash);
        StrategiesUtils.checkStrategiesHash(_packedStrategies, strategiesHash);
        StrategiesUtils.checkIndexInRange(indexStrategyToUpdate, _packedStrategies.addresses.length);

        // Checks call data valid
        StrategiesUtils.checkValidityOfData(_newStrategyParam);
        PackedStrategies memory newPackedStrategies = ArrayUtils.getPackedStrategiesAfterUpdate(_packedStrategies, indexStrategyToUpdate, _newStrategyParam);
        strategiesHash = StrategiesUtils.getStrategiesHash(newPackedStrategies);
        emit StrategyUpdated(newPackedStrategies);
    }


    function removeStrategy(
        PackedStrategies memory _packedStrategies,
        uint256 indexStrategyToRemove
    ) external onlyOwner {

        StrategiesUtils.checkAtLeastOneStrategy(strategiesHash);
        StrategiesUtils.checkStrategiesHash(_packedStrategies, strategiesHash);
        StrategiesUtils.checkIndexInRange(indexStrategyToRemove, _packedStrategies.addresses.length);

        PackedStrategies memory newPackedStrategies = ArrayUtils.getPackedStrategiesAfterRemove(_packedStrategies, indexStrategyToRemove);
        targetAllocation = ArrayUtils.removeUint256Array(targetAllocation, indexStrategyToRemove);
        strategiesHash = StrategiesUtils.getStrategiesHash(newPackedStrategies);
        
        emit StrategyRemoved(newPackedStrategies);
    }

}






// ============== TO THINK  ================

// function forceTargetAllocation(
//         uint256[] calldata _newTargetAllocation
//     ) public onlyOwner {
//         StrategiesUtils.checkAtLeastOneStrategy(strategiesHash);
//         require(
//             _newTargetAllocation.length == targetAllocation.length,
//             "LENGTH"
//         );
//         for (uint256 j; j < _newTargetAllocation.length; j++) {
//             targetAllocation[j] = _newTargetAllocation[j];
//         }
//         emit targetAllocationForced(_newTargetAllocation);
//     }


// function updateTargetAllocation(address[] memory strategies) internal {
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