//SPDX-License-Identifier: UNLICENSED

import "./.cache/OpenZeppelin/v4.8.0/access/Ownable.sol";
import "./.cache/OpenZeppelin/v4.8.0/security/Pausable.sol";
import "./.cache/OpenZeppelin/v4.8.0/token/ERC20/IERC20.sol";
import "./.cache/OpenZeppelin/v4.8.0/token/ERC20/utils/SafeERC20.sol";
import {IStrategy} from "./interfaces/IStrategy.sol";


// import "OpenZeppelin/openzeppelin-contracts@4.8.0/contracts/access/Ownable.sol";
// import "OpenZeppelin/openzeppelin-contracts@4.8.0/contracts/security/Pausable.sol";

pragma solidity >=0.7.0 <0.9.0;


interface ICairoVerifier {
    function isValid(bytes32) external view returns (bool);
}

interface IStreamer {
    function token() external view returns (IERC20);
    function streamToStart(bytes32) external view returns (uint256);
    function withdraw(address from, address to, uint216 amountPerSec) external;
    function getStreamId(address from, address to, uint216 amountPerSec) external view returns (bytes32);
}

contract DebtAllocator is Ownable, Pausable {

    using SafeERC20 for IERC20;

    uint256 PRECISION = 10**18;

    ICairoVerifier public cairoVerifier = ICairoVerifier(address(0));
    bytes32 public cairoProgramHash = 0x0;

    struct PackedStrategies{
    	address[] addresses;
        uint256[] callLen;
        address[] contracts; 
        bytes[] checkdata; 
        uint256[] offset; 
        uint256[]  calculationsLen;
        uint256[]  calculations; 
        uint256[] conditionsLen;
        uint256[] conditions;
    }

    struct StrategyParam{
        uint256 callLen;
        address[] contracts; 
        bytes[] checkdata; 
        uint256[] offset; 
        uint256 calculationsLen;
        uint256[]  calculations; 
        uint256  conditionsLen;
        uint256[]  conditions;
    }


    uint256[] public targetAllocation;

    // Everyone is free to propose a new solution, the address is stored so the user can get rewarded
    address public proposer;
    uint256 public proposerPerformance;
    uint256 public currentAPY;
    uint256 public lastUpdate;
    uint256 public strategiesHash;
    uint256 public inputHash;
    mapping(uint256 => uint256) public snapshotTimestamp;

    uint256 public staleSnapshotPeriod = 24 * 3600;
    uint256 public stalePeriod = 24 * 3600;

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

    event StrategyAdded(address[] Strategies,uint256[] StrategiesCallLen, address[] Contracts, bytes4[] Checkdata, uint256[] Offset, uint256[] CalculationsLen, uint256[] Calculations, uint256[] ConditionsLen, uint256[] Conditions);
    event StrategyUpdated(address[] Strategies,uint256[] StrategiesCallLen, address[] Contracts, bytes4[] Checkdata, uint256[] Offset, uint256[] CalculationsLen, uint256[] Calculations, uint256[] ConditionsLen, uint256[] Conditions);
    event StrategyRemoved(address[] Strategies,uint256[] StrategiesCallLen, address[] Contracts, bytes4[] Checkdata, uint256[] Offset, uint256[] CalculationsLen, uint256[] Calculations, uint256[] ConditionsLen, uint256[] Conditions);


    event NewSnapshot(uint256[] dataStrategies, uint256[] calculation, uint256[] condition,uint256 inputHash, uint256[] targetAllocation, uint256 timestamp);
    event NewSolution(uint256 newApy, uint256[] newTargetAllocation, address proposer, uint256 proposerPerformance,uint256 timestamp);

    event NewCairoProgramHash(bytes32 newCairoProgramHash);
    event NewCairoVerifier(address newCairoVerifier);
    event NewStalePeriod(uint256 newStalePeriod);
    event NewStaleSnapshotPeriod(uint256 newStaleSnapshotPeriod);
    event targetAllocationForced(uint256[] newTargetAllocation);

    // TODO: add role based access control to invoke those functions

    function updateRewardsConfig(address _rewardsPayer, address _rewardsStreamer, uint216 _rewardsPerSec) external onlyOwner {
        bytes32 streamId = IStreamer(_rewardsStreamer).getStreamId(_rewardsPayer, address(this), _rewardsPerSec);
        require(IStreamer(_rewardsStreamer).streamToStart(streamId) > 0, "stream does not exist");
        rewardsPayer = _rewardsPayer;
        rewardsStreamer = _rewardsStreamer;
        rewardsPerSec = _rewardsPerSec;
    }

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

    function updateStalePeriod(uint256 _stalePeriod) public onlyOwner {
        stalePeriod = _stalePeriod;
        emit NewStalePeriod(_stalePeriod);
    }

    function updateStaleSnapshotPeriod(uint256 _staleSnapshotPeriod) public onlyOwner {
        staleSnapshotPeriod = _staleSnapshotPeriod;
        emit NewStaleSnapshotPeriod(_staleSnapshotPeriod);
    }

    function forceTargetAllocation(uint256[] memory _newTargetAllocation) public onlyOwner whenPaused {
        require(strategiesHash != 0, "NO_STRATEGIES_REGISTERED");   
        require(_newTargetAllocation.length == targetAllocation.length, "INVALIDE_LENGTH");
        for(uint256 j; j < _newTargetAllocation.length; j++) {
            targetAllocation[j] = _newTargetAllocation[j];
        }
        emit targetAllocationForced(_newTargetAllocation);
    }

    function addStrategy(
            PackedStrategies memory _packedStrategies,
            address _newStrategy,
            StrategyParam memory _newStrategyParam) external onlyOwner{
        // Checks previous strategies data valid 
        
        bytes4[] memory checkdata = new bytes4[](_packedStrategies.checkdata.length);
        for(uint256 i = 0 ; i < _packedStrategies.checkdata.length; i++) {
            checkdata[i] = bytes4(_packedStrategies.checkdata[i]);
        }

        if(strategiesHash != 0){         
            require(strategiesHash == uint256(keccak256(abi.encodePacked(_packedStrategies.addresses, _packedStrategies.callLen, _packedStrategies.contracts, checkdata, _packedStrategies.offset, _packedStrategies.calculationsLen, _packedStrategies.calculations, _packedStrategies.conditionsLen, _packedStrategies.conditions))), "INVALID_DATA");   
        }

        for(uint256 i = 0 ; i < _packedStrategies.addresses.length; i++) {
            if(_packedStrategies.addresses[i] == _newStrategy){
                revert("STRATEGY_EXISTS");
            }
        }


        // Checks strategy is yearn v3
        try IStrategy(_newStrategy).apiVersion() returns (uint256) {} catch {
            revert("INVALID_STRATEGY");
        }

        // Checks call data valid
        require(_newStrategyParam.callLen == _newStrategyParam.contracts.length && _newStrategyParam.callLen == _newStrategyParam.checkdata.length && _newStrategyParam.callLen == _newStrategyParam.offset.length && _newStrategyParam.calculationsLen == _newStrategyParam.calculations.length && _newStrategyParam.conditionsLen == _newStrategyParam.conditions.length, "INVALID_ARRAY_LEN");
        for (uint256 i = 0; i < _newStrategyParam.callLen; i++) {
            (bool success,) = _newStrategyParam.contracts[i].call(_newStrategyParam.checkdata[i]);
                require(success == true, "INVALID_CALLDATA");
            // Should we check for offset?
        }

        // Build new arrays for the Strategy Hash and the Event
        address[] memory strategies = new address[](_packedStrategies.addresses.length + 1);
        for(uint256 i = 0 ; i < _packedStrategies.addresses.length; i++) {
            strategies[i] = _packedStrategies.addresses[i];
        }
        strategies[_packedStrategies.addresses.length] = _newStrategy;

        uint256[] memory strategiesCallLen = new uint256[](_packedStrategies.callLen.length + 1);
        for(uint256 i = 0 ; i < _packedStrategies.callLen.length; i++) {
            strategiesCallLen[i] = _packedStrategies.callLen[i];
        }
        strategiesCallLen[_packedStrategies.callLen.length] = _newStrategyParam.callLen;

        address[] memory contracts = new address[](_packedStrategies.contracts.length + _newStrategyParam.callLen);
        for(uint256 i = 0 ; i < _packedStrategies.contracts.length; i++) {
            contracts[i] = _packedStrategies.contracts[i];
        }
        for(uint256 i = 0 ; i < _newStrategyParam.callLen; i++) {
            contracts[i + _packedStrategies.contracts.length] = _newStrategyParam.contracts[i];
        }

        checkdata = new bytes4[](_packedStrategies.checkdata.length + _newStrategyParam.callLen);
        for(uint256 i = 0 ; i < _packedStrategies.checkdata.length; i++) {
            checkdata[i] = bytes4(_packedStrategies.checkdata[i]);
        }

        for(uint256 i = 0 ; i < _newStrategyParam.callLen; i++) {
            checkdata[i + _packedStrategies.checkdata.length] = bytes4(_newStrategyParam.checkdata[i]);
        }

        uint256[] memory offset = new uint256[](_packedStrategies.offset.length + _newStrategyParam.callLen);
        for(uint256 i = 0 ; i < _packedStrategies.offset.length; i++) {
            offset[i] = _packedStrategies.offset[i];
        }
        for(uint256 i = 0 ; i < _newStrategyParam.callLen; i++) {
            offset[i + _packedStrategies.offset.length] = _newStrategyParam.offset[i];
        }

        uint256[] memory calculationsLen = new uint256[](_packedStrategies.calculationsLen.length + 1);
        for(uint256 i = 0 ; i < _packedStrategies.calculationsLen.length; i++) {
            calculationsLen[i] = _packedStrategies.calculationsLen[i];
        }
        calculationsLen[_packedStrategies.calculationsLen.length] = _newStrategyParam.calculationsLen;

        uint256[] memory calculations = new uint256[](_packedStrategies.calculations.length + _newStrategyParam.calculationsLen);
        for(uint256 i = 0 ; i < _packedStrategies.calculations.length; i++) {
            calculations[i] = _packedStrategies.calculations[i];
        }
        for(uint256 i = 0 ; i < _newStrategyParam.calculationsLen; i++) {
            calculations[i + _packedStrategies.calculations.length] = _newStrategyParam.calculations[i];
        }

        uint256[] memory conditionsLen = new uint256[](_packedStrategies.conditionsLen.length + 1);
        for(uint256 i = 0 ; i < _packedStrategies.conditionsLen.length; i++) {
            conditionsLen[i] = _packedStrategies.conditionsLen[i];
        }
        conditionsLen[_packedStrategies.conditionsLen.length] = _newStrategyParam.conditionsLen;

        uint256[] memory conditions = new uint256[](_packedStrategies.conditions.length + _newStrategyParam.conditionsLen);
        for(uint256 i = 0 ; i < _packedStrategies.conditions.length; i++) {
            conditions[i] = _packedStrategies.conditions[i];
        }
        for(uint256 i = 0 ; i < _newStrategyParam.conditionsLen; i++) {
            conditions[i + _packedStrategies.conditions.length] = _newStrategyParam.conditions[i];
        }

        strategiesHash = uint256(keccak256(abi.encodePacked(strategies, strategiesCallLen, contracts, checkdata, offset, calculationsLen, calculations, conditionsLen ,conditions)));

        // New strategy allocation always set to 0, people can then send new solution
        targetAllocation.push(0);

        emit StrategyAdded(strategies, strategiesCallLen, contracts, checkdata, offset, calculationsLen, calculations, conditionsLen, conditions);
    }

    function updateStrategy(
            PackedStrategies memory _packedStrategies,
            uint256 indexStrategyToUpdate,
            StrategyParam memory _newStrategyParam) external onlyOwner {
        // Checks at least one strategy is registered
        require(strategiesHash != 0, "NO_STRATEGIES_REGISTERED");   

        // Checks strategies data is valid 
        bytes4[] memory checkdata = new bytes4[](_packedStrategies.checkdata.length);
        for(uint256 i = 0 ; i < _packedStrategies.checkdata.length; i++) {
            checkdata[i] = bytes4(_packedStrategies.checkdata[i]);
        }
        require(strategiesHash == uint256(keccak256(abi.encodePacked(_packedStrategies.addresses, _packedStrategies.callLen, _packedStrategies.contracts, checkdata, _packedStrategies.offset, _packedStrategies.calculationsLen, _packedStrategies.calculations, _packedStrategies.conditionsLen, _packedStrategies.conditions))), "INVALID_DATA");   
        
        // Checks index in range
        require(indexStrategyToUpdate < _packedStrategies.addresses.length, "INDEX_OUT_OF_RANGE");

        // Checks call data valid
        require(_newStrategyParam.callLen == _newStrategyParam.contracts.length && _newStrategyParam.callLen == _newStrategyParam.checkdata.length && _newStrategyParam.callLen == _newStrategyParam.offset.length && _newStrategyParam.calculationsLen == _newStrategyParam.calculations.length && _newStrategyParam.conditionsLen == _newStrategyParam.conditions.length, "INVALID_ARRAY_LEN");
        for (uint256 i = 0; i < _newStrategyParam.callLen; i++) {
            (bool success,) = _newStrategyParam.contracts[i].call(_newStrategyParam.checkdata[i]);
                require(success == true, "INVALID_CALLDATA");
            // Should we check for offset?
        }

        // Build new arrays for the Strategy Hash and the Event

        uint256[] memory strategiesCallLen = new uint256[](_packedStrategies.callLen.length);
        uint256[] memory calculationsLen = new uint256[](_packedStrategies.calculationsLen.length);
        uint256[] memory conditionsLen = new uint256[](_packedStrategies.conditionsLen.length);
        address[] memory contracts = new address[](_packedStrategies.contracts.length - _packedStrategies.callLen[indexStrategyToUpdate] + _newStrategyParam.callLen);
        checkdata = new bytes4[](_packedStrategies.checkdata.length - _packedStrategies.callLen[indexStrategyToUpdate] + _newStrategyParam.callLen);
        uint256[] memory offset = new uint256[](_packedStrategies.offset.length - _packedStrategies.callLen[indexStrategyToUpdate] + _newStrategyParam.callLen);
        uint256[] memory calculations = new uint256[](_packedStrategies.calculations.length - _packedStrategies.calculationsLen[indexStrategyToUpdate] + _newStrategyParam.calculationsLen);
        uint256[] memory conditions = new uint256[](_packedStrategies.conditions.length - _packedStrategies.conditionsLen[indexStrategyToUpdate] + _newStrategyParam.conditionsLen);
        uint256 offsetCalldata = indexStrategyToUpdate;
        if(indexStrategyToUpdate == _packedStrategies.addresses.length - 1){
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                strategiesCallLen[i] = _packedStrategies.callLen[i];
            }
            strategiesCallLen[offsetCalldata] = _newStrategyParam.callLen;
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                    calculationsLen[i] = _packedStrategies.calculationsLen[i];
            }
            calculationsLen[offsetCalldata] = _newStrategyParam.calculationsLen;
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                conditionsLen[i] = _packedStrategies.conditionsLen[i];
            }
            conditionsLen[offsetCalldata] = _newStrategyParam.conditionsLen;

            offsetCalldata = 0;
            for(uint256 i = 0 ; i < indexStrategyToUpdate; i++) {
                offsetCalldata += _packedStrategies.callLen[i];
            }
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                contracts[i] = _packedStrategies.contracts[i];
            }
            for(uint256 i = 0 ; i < _newStrategyParam.callLen; i++) {
                contracts[i + offsetCalldata] = _newStrategyParam.contracts[i];
            }
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                checkdata[i] = bytes4(_packedStrategies.checkdata[i]);
            }
            for(uint256 i = 0 ; i < _newStrategyParam.callLen; i++) {
                checkdata[i + offsetCalldata] = bytes4(_newStrategyParam.checkdata[i]);
            }
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                offset[i] = _packedStrategies.offset[i];
            }
            for(uint256 i = 0 ; i < _newStrategyParam.callLen; i++) {
                offset[i + offsetCalldata] = _newStrategyParam.offset[i];
            }
            
            offsetCalldata = 0;
            for(uint256 i = 0 ; i < indexStrategyToUpdate; i++) {
                offsetCalldata += _packedStrategies.calculationsLen[i];
            }
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                calculations[i] = _packedStrategies.calculations[i];
            }
            for(uint256 i = 0 ; i <  _newStrategyParam.calculationsLen; i++) {
                calculations[i + offsetCalldata] = _newStrategyParam.calculations[i];
            }

            offsetCalldata = 0;
            for(uint256 i = 0 ; i < indexStrategyToUpdate; i++) {
                offsetCalldata += _packedStrategies.conditionsLen[i];
            }
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                conditions[i] = _packedStrategies.conditions[i];
            }
            for(uint256 i = 0 ; i <  _newStrategyParam.conditionsLen; i++) {
                conditions[i + offsetCalldata] = _newStrategyParam.conditions[i];
            }
        } else {
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                strategiesCallLen[i] = _packedStrategies.callLen[i];
            }
            strategiesCallLen[offsetCalldata] = _newStrategyParam.callLen;
            for(uint256 i = offsetCalldata + 1 ; i < _packedStrategies.callLen.length; i++) {
                strategiesCallLen[i] = _packedStrategies.callLen[i];
            }
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                    calculationsLen[i] = _packedStrategies.calculationsLen[i];
            }
            calculationsLen[offsetCalldata] = _newStrategyParam.calculationsLen;
            for(uint256 i = offsetCalldata + 1 ; i < _packedStrategies.calculationsLen.length; i++) {
                calculationsLen[i] = _packedStrategies.calculationsLen[i];
            }
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                conditionsLen[i] = _packedStrategies.conditionsLen[i];
            }
            conditionsLen[offsetCalldata] = _newStrategyParam.conditionsLen;
            for(uint256 i = offsetCalldata + 1 ; i < _packedStrategies.conditionsLen.length; i++) {
                conditionsLen[i] = _packedStrategies.conditionsLen[i];
            }


            uint256 totalCallLen = 0;
            offsetCalldata = 0;
            for(uint256 i = 0 ; i < _packedStrategies.addresses.length; i++) {
                if(i == indexStrategyToUpdate){
                    offsetCalldata = totalCallLen;
                }
                totalCallLen += _packedStrategies.callLen[i];
            }
            uint256 offsetCalldataAfter = offsetCalldata + _packedStrategies.callLen[indexStrategyToUpdate];
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                contracts[i] = _packedStrategies.contracts[i];
            }
            for(uint256 i = 0 ; i < _newStrategyParam.callLen; i++) {
                contracts[i + offsetCalldata] = _newStrategyParam.contracts[i];
            }
            for(uint256 i = 0 ; i < totalCallLen - offsetCalldataAfter; i++) {
                contracts[i + offsetCalldata + _newStrategyParam.callLen] = _packedStrategies.contracts[offsetCalldataAfter + i];
            }
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                checkdata[i] = bytes4(_packedStrategies.checkdata[i]);
            }
            for(uint256 i = 0 ; i < _newStrategyParam.callLen; i++) {
                checkdata[i + offsetCalldata] = bytes4(_newStrategyParam.checkdata[i]);
            }
            for(uint256 i = 0 ; i < totalCallLen - offsetCalldataAfter; i++) {
                checkdata[i + offsetCalldata + _newStrategyParam.callLen] = bytes4(_packedStrategies.checkdata[offsetCalldataAfter + i]);
            }
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                offset[i] = _packedStrategies.offset[i];
            }
            for(uint256 i = 0 ; i < _newStrategyParam.callLen; i++) {
                offset[i + offsetCalldata] = _newStrategyParam.offset[i];
            }
            for(uint256 i = 0 ; i < totalCallLen - offsetCalldataAfter; i++) {
                offset[i + offsetCalldata + _newStrategyParam.callLen] = _packedStrategies.offset[offsetCalldataAfter + i];
            }

            uint256 totalCalculationsLen = 0;
            offsetCalldata = 0;
            for(uint256 i = 0 ; i < _packedStrategies.addresses.length; i++) {
                if(i == indexStrategyToUpdate){
                    offsetCalldata = totalCalculationsLen;
                }
                totalCalculationsLen += _packedStrategies.calculationsLen[i];
            }
            offsetCalldataAfter = offsetCalldata + _packedStrategies.calculationsLen[indexStrategyToUpdate];
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                calculations[i] = _packedStrategies.calculations[i];
            }
            for(uint256 i = 0 ; i <  _newStrategyParam.calculationsLen; i++) {
                calculations[i + offsetCalldata] = _newStrategyParam.calculations[i];
            }
            for(uint256 i = 0 ; i < totalCalculationsLen - offsetCalldataAfter; i++) {
                calculations[i + offsetCalldata + _newStrategyParam.calculationsLen] = _packedStrategies.calculations[offsetCalldataAfter + i];
            }


            uint256 totalConditionsLen = 0;
            offsetCalldata = 0;
            for(uint256 i = 0 ; i < _packedStrategies.addresses.length; i++) {
                if(i == indexStrategyToUpdate){
                    offsetCalldata = totalConditionsLen;
                }
                totalConditionsLen += _packedStrategies.conditionsLen[i];
            }
            offsetCalldataAfter = offsetCalldata + _packedStrategies.conditionsLen[indexStrategyToUpdate];
            for(uint256 i = 0 ; i < offsetCalldata; i++) {
                conditions[i] = _packedStrategies.conditions[i];
            }
            for(uint256 i = 0 ; i <  _newStrategyParam.conditionsLen; i++) {
                conditions[i + offsetCalldata] = _newStrategyParam.conditions[i];
            }
            for(uint256 i = 0 ; i < totalConditionsLen - offsetCalldataAfter; i++) {
                conditions[i + offsetCalldata + _newStrategyParam.conditionsLen] = _packedStrategies.conditions[offsetCalldataAfter + i];
            }
        }
        strategiesHash = uint256(keccak256(abi.encodePacked(_packedStrategies.addresses, strategiesCallLen, contracts, checkdata, offset, calculationsLen, calculations, conditionsLen ,conditions)));
        emit StrategyUpdated(_packedStrategies.addresses, strategiesCallLen, contracts, checkdata, offset, calculationsLen, calculations, conditionsLen, conditions);
    }


    function removeStrategy(
            PackedStrategies memory _packedStrategies,
            uint256 indexStrategyToRemove) external onlyOwner {
        // Checks at least one strategy is registered
        require(strategiesHash != 0, "NO_STRATEGIES_REGISTERED");   

        bytes4[] memory checkdata = new bytes4[](_packedStrategies.checkdata.length);
        for(uint256 i = 0 ; i < _packedStrategies.checkdata.length; i++) {
            checkdata[i] = bytes4(_packedStrategies.checkdata[i]);
        }

        // Checks strategies data is valid 
        require(strategiesHash == uint256(keccak256(abi.encodePacked(_packedStrategies.addresses, _packedStrategies.callLen, _packedStrategies.contracts, checkdata, _packedStrategies.offset, _packedStrategies.calculationsLen, _packedStrategies.calculations, _packedStrategies.conditionsLen, _packedStrategies.conditions))), "INVALID_DATA");   
        
        // Checks index in range
        require(indexStrategyToRemove < _packedStrategies.addresses.length);

        // Build new arrays for the Strategy Hash and the Event
        uint256[] memory strategiesCallLen = new uint256[](_packedStrategies.callLen.length - 1);
        uint256[] memory calculationsLen = new uint256[](_packedStrategies.calculationsLen.length - 1);
        uint256[] memory conditionsLen = new uint256[](_packedStrategies.conditionsLen.length - 1);
        address[] memory contracts = new address[](_packedStrategies.contracts.length - _packedStrategies.callLen[indexStrategyToRemove]);
        checkdata = new bytes4[](_packedStrategies.checkdata.length - _packedStrategies.callLen[indexStrategyToRemove]);
        uint256[] memory offset = new uint256[](_packedStrategies.offset.length - _packedStrategies.callLen[indexStrategyToRemove]);
        uint256[] memory calculations = new uint256[](_packedStrategies.calculations.length - _packedStrategies.calculationsLen[indexStrategyToRemove]);
        uint256[] memory conditions = new uint256[](_packedStrategies.conditions.length - _packedStrategies.conditionsLen[indexStrategyToRemove]);
        uint256 offsetCalldata = indexStrategyToRemove;
        for(uint256 i = 0 ; i < offsetCalldata; i++) {
            strategiesCallLen[i] = _packedStrategies.callLen[i];
        }
        for(uint256 i = 0 ; i < _packedStrategies.addresses.length - (offsetCalldata + 1); i++) {
            strategiesCallLen[offsetCalldata + i] = _packedStrategies.callLen[offsetCalldata + 1 + i];
        }
        for(uint256 i = 0 ; i < offsetCalldata; i++) {
            calculationsLen[i] = _packedStrategies.calculationsLen[i];
        }
        for(uint256 i = 0 ; i < _packedStrategies.addresses.length - (offsetCalldata + 1); i++) {
            calculationsLen[offsetCalldata + i] = _packedStrategies.calculationsLen[offsetCalldata + 1 + i];
        }
        for(uint256 i = 0 ; i < offsetCalldata; i++) {
            conditionsLen[i] = _packedStrategies.conditionsLen[i];
        }
        for(uint256 i = 0 ; i < _packedStrategies.addresses.length - (offsetCalldata + 1); i++) {
            conditionsLen[offsetCalldata + i] = _packedStrategies.conditionsLen[offsetCalldata + 1 + i];
        }

        uint256 totalCallLen = 0;
        offsetCalldata = 0;
        for(uint256 i = 0 ; i < _packedStrategies.addresses.length; i++) {
            if(i == indexStrategyToRemove){
                offsetCalldata = totalCallLen;
            }
            totalCallLen += _packedStrategies.callLen[i];
        }

        for(uint256 i = 0 ; i < offsetCalldata; i++) {
            contracts[i] = _packedStrategies.contracts[i];
        }
        for(uint256 i = 0 ; i < totalCallLen - (offsetCalldata + _packedStrategies.callLen[indexStrategyToRemove]); i++) {
            contracts[i + offsetCalldata] = _packedStrategies.contracts[offsetCalldata + _packedStrategies.callLen[indexStrategyToRemove] + i];
        }
        for(uint256 i = 0 ; i < offsetCalldata; i++) {
            checkdata[i] = bytes4(_packedStrategies.checkdata[i]);
        }
        for(uint256 i = 0 ; i < totalCallLen - (offsetCalldata + _packedStrategies.callLen[indexStrategyToRemove]); i++) {
            checkdata[i + offsetCalldata] = bytes4(_packedStrategies.checkdata[offsetCalldata + _packedStrategies.callLen[indexStrategyToRemove] + i]);
        }
        for(uint256 i = 0 ; i < offsetCalldata; i++) {
            offset[i] = _packedStrategies.offset[i];
        }
        for(uint256 i = 0 ; i < totalCallLen - (offsetCalldata + _packedStrategies.callLen[indexStrategyToRemove]); i++) {
            offset[i + offsetCalldata] = _packedStrategies.offset[offsetCalldata + _packedStrategies.callLen[indexStrategyToRemove] + i];
        }

        uint256 totalCalculationsLen = 0;
        offsetCalldata = 0;
        for(uint256 i = 0 ; i < _packedStrategies.addresses.length; i++) {
            if(i == indexStrategyToRemove){
                offsetCalldata = totalCalculationsLen;
            }
            totalCalculationsLen += _packedStrategies.calculationsLen[i];
        }
        for(uint256 i = 0 ; i < offsetCalldata; i++) {
            calculations[i] = _packedStrategies.calculations[i];
        }
        for(uint256 i = 0 ; i < totalCalculationsLen - (offsetCalldata + _packedStrategies.calculationsLen[indexStrategyToRemove]); i++) {
            calculations[i + offsetCalldata] = _packedStrategies.calculations[offsetCalldata + _packedStrategies.calculationsLen[indexStrategyToRemove] + i];
        }

        uint256 totalConditionsLen = 0;
        offsetCalldata = 0;
        for(uint256 i = 0 ; i < _packedStrategies.addresses.length; i++) {
            if(i == indexStrategyToRemove){
                offsetCalldata = totalConditionsLen;
            }
            totalConditionsLen += _packedStrategies.conditionsLen[i];
        }
        for(uint256 i = 0 ; i < offsetCalldata; i++) {
            conditions[i] = _packedStrategies.conditions[i];
        }
        for(uint256 i = 0 ; i < totalConditionsLen - (offsetCalldata + _packedStrategies.conditionsLen[indexStrategyToRemove]); i++) {
            conditions[i + offsetCalldata] = _packedStrategies.conditions[offsetCalldata + _packedStrategies.conditionsLen[indexStrategyToRemove] + i];
        }
        
        strategiesHash = uint256(keccak256(abi.encodePacked(_packedStrategies.addresses, strategiesCallLen, contracts, checkdata, offset, calculationsLen, calculations, conditionsLen ,conditions)));
        emit StrategyRemoved(_packedStrategies.addresses, strategiesCallLen, contracts, checkdata, offset, calculationsLen, calculations, conditionsLen, conditions);
    }


    //Can't set only view, .call potentially modify state (should not arrive)
    function getStrategiesData(
            address[] memory contracts, 
            bytes[] memory checkdata, 
            uint256[] memory offset) public returns(uint256[] memory dataStrategies) {
        uint256[] memory dataStrategies_ = new uint256[](contracts.length);
        for(uint256 j; j < contracts.length; j++) {
            (bool success, bytes memory data) = contracts[j].call(checkdata[j]);
            require(success == true, "call didn't succeed");
            dataStrategies_[j] = uint256(bytesToBytes32(data, offset[j]));
        }
       return(dataStrategies_);
    }

     function updateTargetAllocation(address[] memory strategies) internal {
        uint256[] memory realAllocations = new uint256[](strategies.length);
        uint256 cumulativeAmountRealAllocations = 0;
        uint256 cumulativeAmountTargetAllocations = 0;
        for(uint256 j; j < strategies.length; j++) {
            realAllocations[j] = IStrategy(strategies[j]).totalAssets();
            cumulativeAmountRealAllocations += realAllocations[j];
            cumulativeAmountTargetAllocations += targetAllocation[j];
        }

        if(cumulativeAmountTargetAllocations == 0){
            targetAllocation = realAllocations;
        } else {
            if(cumulativeAmountTargetAllocations <= cumulativeAmountRealAllocations){
            uint256 diff = cumulativeAmountRealAllocations - cumulativeAmountTargetAllocations;
            // We need to add this amount respecting the different strategies allocation ratio 
            for (uint256 i = 0; i < strategies.length; i++) {
                uint256 strategyAllocationRatio = (PRECISION * targetAllocation[i]) / cumulativeAmountTargetAllocations;
                targetAllocation[i] += (strategyAllocationRatio * diff) / PRECISION;
            }
        } else {
            uint256 diff = cumulativeAmountTargetAllocations - cumulativeAmountRealAllocations;
            // We need to substract this amount respecting the different strategies allocation ratio 
            for (uint256 i = 0; i < strategies.length; i++) {
                uint256 strategyAllocationRatio = (PRECISION * targetAllocation[i]) / cumulativeAmountTargetAllocations;
                targetAllocation[i] -= (strategyAllocationRatio * diff) / PRECISION;
            }
        }
        }
    }

    function saveSnapshot(PackedStrategies memory _packedStrategies) external {
        // Checks at least one strategy is registered
        require(strategiesHash != 0, "NO_STRATEGIES_REGISTERED");   

        bytes4[] memory checkdata = new bytes4[](_packedStrategies.checkdata.length);
        for(uint256 i = 0 ; i < _packedStrategies.checkdata.length; i++) {
            checkdata[i] = bytes4(_packedStrategies.checkdata[i]);
        }

        // Checks strategies data is valid 
        require(strategiesHash == uint256(keccak256(abi.encodePacked(_packedStrategies.addresses, _packedStrategies.callLen, _packedStrategies.contracts, checkdata, _packedStrategies.offset, _packedStrategies.calculationsLen, _packedStrategies.calculations, _packedStrategies.conditionsLen, _packedStrategies.conditions))), "INVALID_DATA");
        updateTargetAllocation(_packedStrategies.addresses);
        uint256[] memory dataStrategies = getStrategiesData(_packedStrategies.contracts, _packedStrategies.checkdata, _packedStrategies.offset);
        inputHash = uint256(keccak256(abi.encodePacked(dataStrategies, _packedStrategies.calculations, _packedStrategies.conditions)));
        snapshotTimestamp[inputHash] = block.timestamp;
        emit NewSnapshot(dataStrategies, _packedStrategies.calculations, _packedStrategies.conditions, inputHash, targetAllocation, block.timestamp);
    }


    function verifySolution(uint256[] memory programOutput) external whenNotPaused returns(bytes32){
        // NOTE: Check current snapshot not stale
        uint256 _snapshotTimestamp = snapshotTimestamp[inputHash];
        require(_snapshotTimestamp + staleSnapshotPeriod > block.timestamp, "STALE_SNAPSHOT_PERIOD");

        // NOTE: We get the data from parsing the program output
        (uint256 inputHash_,  uint256[] memory current_target_allocation, uint256[] memory new_target_allocation, uint256 current_solution, uint256 new_solution) = parseProgramOutput(programOutput); 
        
        // check inputs
        require(inputHash_==inputHash, "INVALID_INPUTS");

        // check target allocation len
        require(targetAllocation.length == current_target_allocation.length && targetAllocation.length == new_target_allocation.length,"INVALID_TARGET_ALLOCATION_LENGTH");
            
        // check if the new solution better than previous one
        require(new_solution - minimumApyIncreaseForNewSolution >= current_solution,"NEW_SOLUTION_TOO_BAD");
        
        // Check with cairoVerifier
        bytes32 outputHash = keccak256(abi.encodePacked(programOutput));
        bytes32 fact = keccak256(abi.encodePacked(cairoProgramHash, outputHash));
        require(cairoVerifier.isValid(fact), "MISSING_CAIRO_PROOF");

        // check no one has improven it in stale period (in case market conditions deteriorated)
        // require(_newSolution > currentAPY || block.timestamp - lastUpdate >= stalePeriod, "WRONG_SOLUTION");
        currentAPY = new_solution;
        targetAllocation = new_target_allocation;
        lastUpdate = block.timestamp;

        sendRewardsToCurrentProposer();
        proposer = msg.sender;
        proposerPerformance = new_solution - current_solution;

        emit NewSolution(new_solution, new_target_allocation, msg.sender, proposerPerformance,block.timestamp);
        return(fact);
    }

    function parseProgramOutput(uint256[] memory programOutput) public view returns (uint256 _inputHash, uint256[] memory _current_target_allocation, uint256[] memory _new_target_allocation, uint256 _current_solution, uint256 _new_solution) {
        uint256 inputHashUint256 = programOutput[0] << 128;
        inputHashUint256 += programOutput[1];

        uint256[] memory current_target_allocation = new uint256[](programOutput[2]);
        uint256[] memory new_target_allocation = new uint256[](programOutput[2]);

        for(uint256 i = 0; i < programOutput[2] ; i++) {
            // NOTE: skip the 2 first value + array len 
            current_target_allocation[i] = programOutput[i + 3];
            new_target_allocation[i] = programOutput[i + 4 + programOutput[2]];
        }
        return(inputHashUint256, current_target_allocation, new_target_allocation, programOutput[programOutput.length - 2], programOutput[programOutput.length - 1]);
    }

    function sendRewardsToCurrentProposer() internal {
        IStreamer _rewardsStreamer = IStreamer(rewardsStreamer);
        if(address(_rewardsStreamer) == address(0)){
            return;
        }
        bytes32 streamId = _rewardsStreamer.getStreamId(rewardsPayer, address(this), rewardsPerSec);
        if(_rewardsStreamer.streamToStart(streamId) == 0) {
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
        require(msg.sender == proposer, "not allowed");
        sendRewardsToCurrentProposer();
    }

    function bytesToBytes32(bytes memory b, uint offset) private pure returns (bytes32) {
        bytes32 out;
        for (uint i = 0; i < 32; i++) {
            out |= bytes32(b[offset + i] & 0xFF) >> (i * 8);
        }
        return out;
    }
}

