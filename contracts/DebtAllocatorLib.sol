//SPDX-License-Identifier: UNLICENSED

    uint256 constant PRECISION = 1e27;
    uint256 constant STALE_SNAPSHOT_PERIOD = 24 * 3600;
    uint256 constant MINIMUM_APY_INCREASE = 1e23;


    struct PackedStrategies {
        address[] addresses;
        uint256[] callLen;
        address[] contracts;
        bytes4[] selectors;
        bytes32[][] callData;
        uint256[] offset;
        uint256[] calculationsLen;
        uint256[] calculations;
        uint256[] conditionsLen;
        uint256[] conditions;
    }

    struct StrategyParam {
        uint256 callLen;
        address[] contracts;
        bytes4[] selectors;
        bytes32[][] callData;
        uint256[] offset;
        uint256 calculationsLen;
        uint256[] calculations;
        uint256 conditionsLen;
        uint256[] conditions;
    }

    struct ProgramOutput {
        uint256 inputHash;
        uint256[] currentTargetAllocation;
        uint256[] newTargetAllocation;
        uint256 currentSolution;
        uint256 newSolution;
    }

    struct UpdateU256Len {
        uint256[] callLen;
        uint256[] array;
        uint256 newCallLen;
        uint256[] newArray;
        uint256 index;
    }


library StrategiesUtils {
    
    function checkStrategiesHash(
        PackedStrategies memory _packedStrategies,
        uint256 strategiesHash
    ) public pure {
        uint256 currentHash = getStrategiesHash(_packedStrategies);
        require(
            strategiesHash == currentHash,
            "DATA"
        );
    }

    function getStrategiesHash(
        PackedStrategies memory _packedStrategies
    ) public pure returns (uint256 newHash) {
        bytes32[] memory callDataReduced = getReducedBytes32Array(_packedStrategies.callData);
        newHash = uint256(
            keccak256(
                abi.encodePacked(
                    _packedStrategies.addresses,
                    _packedStrategies.callLen,
                    _packedStrategies.contracts,
                    _packedStrategies.selectors,
                    callDataReduced,
                    _packedStrategies.offset,
                    _packedStrategies.calculationsLen,
                    _packedStrategies.calculations,
                    _packedStrategies.conditionsLen,
                    _packedStrategies.conditions
                )
            )
        );
    }

    


    function getReducedBytes32Array(
        bytes32[][] memory callData
    ) public pure returns (bytes32[] memory result) {
        uint256 callDataTotalLen = 0;
        for (uint i = 0; i < callData.length; i++) 
        {
            callDataTotalLen += callData[i].length;
        }
        bytes32[] memory results = new bytes32[](callDataTotalLen);
        uint256 index = 0;
        for (uint i = 0; i < callData.length; i++) 
        {
            for (uint j = 0; j < callData[i].length; j++) 
            {
            results[index] = callData[i][j];
            index++;
            }
        }
        return (results);
    }


    function checkMessageSenderIsProposer(
        address sender,
        address proposer
    ) public pure {
        require(sender == proposer, "NOT_ALLOWED");
    }
    

    function checkValidityOfPreviousAndNewData(
        uint256 strategiesHash,
        PackedStrategies calldata _packedStrategies,
        address _newStrategy,
        StrategyParam memory _newStrategyParam
    ) public {
        
        // Checks previous strategies data valid

        if (strategiesHash != 0) {
            checkStrategiesHash(_packedStrategies, strategiesHash);
        } else {
            require(_packedStrategies.addresses.length == 0, "FIRST_DATA");
        }
  
        for (uint256 i = 0; i < _packedStrategies.addresses.length; i++) {
            if (_packedStrategies.addresses[i] == _newStrategy) {
                revert("STRATEGY_EXISTS");
            }
        }

        checkValidityOfData(_newStrategyParam);
    }
    

    function checkValidityOfData(
        StrategyParam memory _newStrategyParam
    ) public {
        // check lengths
        require(
            _newStrategyParam.callLen == _newStrategyParam.contracts.length &&
                _newStrategyParam.callLen == _newStrategyParam.selectors.length &&
                _newStrategyParam.callLen == _newStrategyParam.callData.length &&
                _newStrategyParam.callLen == _newStrategyParam.offset.length &&
                _newStrategyParam.calculationsLen ==
                _newStrategyParam.calculations.length &&
                _newStrategyParam.conditionsLen ==
                _newStrategyParam.conditions.length,
            "ARRAY_LEN"
        );

        bytes[] memory checkdatas = selectorAndCallDataToBytes(_newStrategyParam.selectors, _newStrategyParam.callData);

        // check success of calls
        for (uint256 i = 0; i < _newStrategyParam.callLen; i++) {

            (bool success, ) = _newStrategyParam.contracts[i].call(
                checkdatas[i]
            );
            require(success == true, "CALLDATA");
            // Should we check for offset?
        }
    }

    function checkSnapshotNotStaled(
        uint256 _snapshotTimestamp,
        uint256 _staleSnapshotPeriod,
        uint256 _block_timestamp) public pure {
        require(
            _snapshotTimestamp + _staleSnapshotPeriod > _block_timestamp,
            "STALE_SNAPSHOT"
        );
    }

    function checkAtLeastOneStrategy(
        uint256 strategiesHash) public pure {
        require(strategiesHash != 0, "NO_STRATEGIES");
    }

    function checkIndexInRange(
        uint256 index,
        uint256 stratLen) public pure {
        require(
            index < stratLen,
            "INDEX_OUT_OF_RANGE"
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


    function parseProgramOutput(
        uint256[] calldata programOutput
    )
        public
        pure
        returns (
            ProgramOutput memory _programOutput
        )
    {
        uint256 _inputHash = programOutput[0] << 128;
        _inputHash += programOutput[1];

        uint256[] memory _currentTargetAllocation = new uint256[](programOutput[2]);

        uint256[] memory _newTargetAllocation = new uint256[](programOutput[2]);

        for (uint256 i = 0; i < programOutput[2]; i++) {
            // NOTE: skip the 2 first value + array len
            _currentTargetAllocation[i] = programOutput[i + 3];
            _newTargetAllocation[i] = programOutput[i + 4 + programOutput[2]];
        }
        _programOutput = ProgramOutput(_inputHash, _currentTargetAllocation, _newTargetAllocation, programOutput[programOutput.length - 2], programOutput[programOutput.length - 1]);
    }

    function checkProgramOutput(
        ProgramOutput calldata programOutput,
        uint256 inputHash,
        uint256[] calldata targetAllocation,
        uint256 minimumApyIncreaseForNewSolution
    )
        public
        pure
    {
         // check inputs
        require(programOutput.inputHash == inputHash, "HASH");

        // check target allocation is current allocation + current vs new allocation length
        require(
            targetAllocation.length == programOutput.currentTargetAllocation.length &&
                targetAllocation.length == programOutput.newTargetAllocation.length,
            "TARGET_ALLOCATION_LENGTH"
        );


        // check if the new solution better than previous one
        require(
            programOutput.newSolution - minimumApyIncreaseForNewSolution >= programOutput.currentSolution,
            "TOO_BAD"
        );
    }

    function getFact(
        uint256[] calldata programOutput,
        bytes32 programHash
    ) public pure returns (bytes32 fact) {
        bytes32 outputHash = keccak256(abi.encodePacked(programOutput));
        fact = keccak256(abi.encodePacked(programHash, outputHash));
    }
    


    function selectorAndCallDataToBytes(
        bytes4[] memory selector,
        bytes32[][] memory callData
    ) public pure returns (bytes[] memory result) {
        bytes[] memory results = new bytes[](selector.length);
        for (uint i=0; i< selector.length; i++) 
        {
            results[i] = abi.encodePacked(selector[i], callData[i]);
        }
        return (results);
    }


    function bytesToBytes32(
        bytes memory b,
        uint offset
    ) public pure returns (bytes32 result) {
        offset += 32;
        assembly {
            result := mload(add(b, offset))
        }
    }

    function castCheckdataToBytes4 (
        bytes[] memory oldCheckdata
    ) public pure returns (bytes4[] memory checkdata) {
        checkdata = new bytes4[](oldCheckdata.length);
        for (uint256 i = 0; i < oldCheckdata.length; i++) {
            checkdata[i] = bytes4(oldCheckdata[i]);
        }
    }

  }





library ArrayUtils {

    function getPackedStrategiesAfterAdd(
        PackedStrategies memory _packedStrategies,
        address _newStrategy,
        StrategyParam memory _newStrategyParam
    ) public pure returns (PackedStrategies memory newPacked) {
        
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
        newPacked = PackedStrategies(strategies, strategiesCallLen, contracts, selectors, callData, offset, calculationsLen, calculations, conditionsLen, conditions);
    }



    function getPackedStrategiesAfterUpdate(
        PackedStrategies memory _packedStrategies,
        uint256 indexStrategyToUpdate,
        StrategyParam memory _newStrategyParam
    ) public pure returns (PackedStrategies memory newPacked) {
        uint256[] memory strategiesCallLen = updateUint256Array(_packedStrategies.callLen, _newStrategyParam.callLen, indexStrategyToUpdate);
        uint256[] memory calculationsLen = updateUint256Array(_packedStrategies.calculationsLen, _newStrategyParam.calculationsLen, indexStrategyToUpdate);
        uint256[] memory conditionsLen =updateUint256Array(_packedStrategies.conditionsLen, _newStrategyParam.conditionsLen, indexStrategyToUpdate);
        address[] memory contracts = updateAddressArrayWithLen(_packedStrategies.callLen, _packedStrategies.contracts, _newStrategyParam.callLen, _newStrategyParam.contracts, indexStrategyToUpdate);
        bytes4[] memory selectors = updateBytes4ArrayWithLen(_packedStrategies.callLen, _packedStrategies.selectors, _newStrategyParam.callLen, _newStrategyParam.selectors, indexStrategyToUpdate);
        bytes32[][] memory callData = updateBytes32ArrayWithLen(_packedStrategies.callLen, _packedStrategies.callData, _newStrategyParam.callLen, _newStrategyParam.callData, indexStrategyToUpdate);
        uint256[] memory offset = updateUint256ArrayWithLen(UpdateU256Len(_packedStrategies.callLen, _packedStrategies.offset, _newStrategyParam.callLen, _newStrategyParam.offset, indexStrategyToUpdate));
        uint256[] memory calculations = updateUint256ArrayWithLen(UpdateU256Len(_packedStrategies.calculationsLen, _packedStrategies.calculations, _newStrategyParam.calculationsLen, _newStrategyParam.calculations, indexStrategyToUpdate));
        uint256[] memory conditions = updateUint256ArrayWithLen(UpdateU256Len(_packedStrategies.conditionsLen, _packedStrategies.conditions, _newStrategyParam.callLen, _newStrategyParam.conditions, indexStrategyToUpdate));
        newPacked = PackedStrategies(_packedStrategies.addresses, strategiesCallLen, contracts, selectors, callData, offset, calculationsLen, calculations, conditionsLen, conditions);
    }


    function getPackedStrategiesAfterRemove(
        PackedStrategies memory _packedStrategies, uint256 indexStrategyToRemove) public pure returns (PackedStrategies memory newPacked) {
        address[] memory addresses = removeAddressArray(_packedStrategies.addresses, indexStrategyToRemove);
        uint256[] memory strategiesCallLen = removeUint256Array(_packedStrategies.callLen, indexStrategyToRemove);
        uint256[] memory calculationsLen = removeUint256Array(_packedStrategies.calculationsLen, indexStrategyToRemove);
        uint256[] memory conditionsLen =removeUint256Array(_packedStrategies.conditionsLen, indexStrategyToRemove);
        address[] memory contracts = removeAddressArrayWithLen(_packedStrategies.callLen, _packedStrategies.contracts, indexStrategyToRemove);
        bytes4[] memory selectors = removeBytes4ArrayWithLen(_packedStrategies.callLen, _packedStrategies.selectors, indexStrategyToRemove);
        bytes32[][] memory callData = removeBytes32ArrayWithLen(_packedStrategies.callLen, _packedStrategies.callData, indexStrategyToRemove);
        uint256[] memory offset = removeUint256ArrayWithLen(_packedStrategies.callLen, _packedStrategies.offset, indexStrategyToRemove);
        uint256[] memory calculations = removeUint256ArrayWithLen(_packedStrategies.calculationsLen, _packedStrategies.calculations, indexStrategyToRemove);
        uint256[] memory conditions = removeUint256ArrayWithLen(_packedStrategies.conditionsLen, _packedStrategies.conditions, indexStrategyToRemove);
        newPacked = PackedStrategies(addresses, strategiesCallLen, contracts, selectors, callData, offset, calculationsLen, calculations, conditionsLen, conditions);
    }


    function appendAddressToArray(
        address[] memory array,
        address newItem
    ) public pure returns (address[] memory newArray) {
        newArray = new address[](array.length + 1);
        for (uint256 i = 0; i < array.length; i++) {
            newArray[i] = array[i];
        }
        newArray[array.length] = newItem;
    }

    function appendUint256ToArray(
        uint256[] memory array,
        uint256 newItem
    ) public pure returns (uint256[] memory newArray) {
        newArray = new uint256[](array.length + 1);
        for (uint256 i = 0; i < array.length; i++) {
            newArray[i] = array[i];
        }
        newArray[array.length] = newItem;
    }

    function concatenateUint256ArrayToUint256Array(
        uint256[] memory arrayA,
        uint256[] memory arrayB
    ) public pure returns (uint256[] memory newArray) {
        newArray = new uint256[](arrayA.length + arrayB.length);
        for (uint256 i = 0; i < arrayA.length; i++) {
            newArray[i] = arrayA[i];
        }
        uint256 lenA = arrayA.length;
        for (uint256 i = 0; i < arrayB.length; i++) {
            newArray[i + lenA] = arrayB[i];
        }
    }

    function concatenateAddressArrayToAddressArray(
        address[] memory arrayA,
        address[] memory arrayB
    ) public pure returns (address[] memory newArray) {
        newArray = new address[](arrayA.length + arrayB.length);
        for (uint256 i = 0; i < arrayA.length; i++) {
            newArray[i] = arrayA[i];
        }
        uint256 lenA = arrayA.length;
        for (uint256 i = 0; i < arrayB.length; i++) {
            newArray[i + lenA] = arrayB[i];
        }
    }

    function concatenateBytes4ArrayToBytes4(
        bytes4[] memory arrayA,
        bytes4[] memory arrayB
    ) public pure returns (bytes4[] memory newArray) {
        newArray = new bytes4[](arrayA.length + arrayB.length);
        for (uint256 i = 0; i < arrayA.length; i++) {
            newArray[i] = arrayA[i];
        }
        uint256 lenA = arrayA.length;
        for (uint256 i = 0; i < arrayB.length; i++) {
            newArray[i + lenA] = arrayB[i];
        }
    }

    function concatenateDoubleArrayBytes32ArrayToDoubleArrayBytes32(
        bytes32[][] memory arrayA,
        bytes32[][] memory arrayB
    ) public pure returns (bytes32[][] memory newArray) {
        newArray = new bytes32[][](arrayA.length + arrayB.length);
        for (uint256 i = 0; i < arrayA.length; i++) {
            newArray[i] = arrayA[i];
        }
        uint256 lenA = arrayA.length;
        for (uint256 i = 0; i < arrayB.length; i++) {
            newArray[i + lenA] = arrayB[i];
        }
    }

    function updateUint256Array(
        uint256[] memory array,
        uint256 newItem,
        uint256 index
    ) public pure returns (uint256[] memory newArray) {
        newArray = array;
        newArray[index] = newItem;
    }

    function updateAddressArrayWithLen(
        uint256[] memory callLen,
        address[] memory array,
        uint256 newCallLen,
        address[] memory newArray,
        uint256 index
    ) public pure returns (address[] memory newAddressArray) {
        newAddressArray = new address[](array.length - callLen[index] + newCallLen);
        uint256 offsetCalldata = 0;
        for (uint256 i = 0; i < index; i++) {
            for (uint256 j = offsetCalldata; j < offsetCalldata + callLen[i]; j++) {
                newAddressArray[j] = array[j];
            }
            offsetCalldata += callLen[i];
        }
        for (uint256 i = 0; i < newCallLen; i++) {
            newAddressArray[offsetCalldata + i] = newArray[i];
        }
        for (uint256 i = 0; i < array.length - (offsetCalldata + callLen[index]); i++) {
            newAddressArray[offsetCalldata + newCallLen + i] = array[array.length - (offsetCalldata + callLen[index]) + i];
        }
    }

    function updateBytes4ArrayWithLen(
        uint256[] memory callLen,
        bytes4[] memory array,
        uint256 newCallLen,
        bytes4[] memory newArray,
        uint256 index
    ) public pure returns (bytes4[] memory newBytes4Array) {
        newBytes4Array = new bytes4[](array.length - callLen[index] + newCallLen);
        uint256 offsetCalldata = 0;
        for (uint256 i = 0; i < index; i++) {
            for (uint256 j = offsetCalldata; j < offsetCalldata + callLen[i]; j++) {
                newBytes4Array[j] = array[j];
            }
            offsetCalldata += callLen[i];
        }
        for (uint256 i = 0; i < newCallLen; i++) {
            newBytes4Array[offsetCalldata + i] = newArray[i];
        }
        for (uint256 i = 0; i < array.length - (offsetCalldata + callLen[index]); i++) {
            newBytes4Array[offsetCalldata + newCallLen + i] = array[array.length - (offsetCalldata + callLen[index]) + i];
        }
    }

    function updateBytes32ArrayWithLen(
        uint256[] memory callLen,
        bytes32[][] memory array,
        uint256 newCallLen,
        bytes32[][] memory newArray,
        uint256 index
    ) public pure returns (bytes32[][] memory newBytes32DoubleArray) {
        newBytes32DoubleArray = new bytes32[][](array.length - callLen[index] + newCallLen);
        uint256 offsetCalldata = 0;
        for (uint256 i = 0; i < index; i++) {
            for (uint256 j = offsetCalldata; j < offsetCalldata + callLen[i]; j++) {
                newBytes32DoubleArray[j] = array[j];
            }
            offsetCalldata += callLen[i];
        }
        for (uint256 i = 0; i < newCallLen; i++) {
            newBytes32DoubleArray[offsetCalldata + i] = newArray[i];
        }
        for (uint256 i = 0; i < array.length - (offsetCalldata + callLen[index]); i++) {
            newBytes32DoubleArray[offsetCalldata + newCallLen + i] = array[array.length - (offsetCalldata + callLen[index]) + i];
        }
    }

    function updateUint256ArrayWithLen(
        UpdateU256Len memory U256Len
    ) public pure returns (uint256[] memory newUint256Array) {
        newUint256Array = new uint256[](U256Len.array.length - U256Len.callLen[U256Len.index] + U256Len.newCallLen);
        uint256 offsetCalldata = 0;
        for (uint256 i = 0; i < U256Len.index; i++) {
            for (uint256 j = offsetCalldata; j < offsetCalldata + U256Len.callLen[i]; j++) {
                newUint256Array[j] = U256Len.array[j];
            }
            offsetCalldata += U256Len.callLen[i];
        }
        for (uint256 i = 0; i < U256Len.newCallLen; i++) {
            newUint256Array[offsetCalldata + i] = U256Len.newArray[i];
        }
        for (uint256 i = 0; i < U256Len.array.length - (offsetCalldata + U256Len.callLen[U256Len.index]); i++) {
            newUint256Array[offsetCalldata + U256Len.newCallLen + i] = U256Len.array[U256Len.array.length - (offsetCalldata + U256Len.callLen[U256Len.index]) + i];
        }
    }

    function removeAddressArray(
        address[] memory array,
        uint256 index
    ) public pure returns (address[] memory newArray) {
        newArray = new address[](array.length - 1);
        for (uint256 i = 0; i < index; i++) {
            newArray[i] = array[i];
        }
        for (uint256 i = index + 1; i < array.length; i++) {
            newArray[i - 1] = array[i];
        }
    }

    function removeUint256Array(
        uint256[] memory array,
        uint256 index
    ) public pure returns (uint256[] memory newArray) {
        newArray = new uint256[](array.length - 1);
        for (uint256 i = 0; i < index; i++) {
            newArray[i] = array[i];
        }
        for (uint256 i = index + 1; i < array.length; i++) {
            newArray[i - 1] = array[i];
        }
    }

    function removeAddressArrayWithLen(
        uint256[] memory callLen,
        address[] memory array,
        uint256 index
    ) public pure returns (address[] memory newArray) {
        newArray = new address[](array.length - callLen[index]);
        uint256 offsetCalldata = 0;
        for (uint256 i = 0; i < index; i++) {
            for (uint256 j = offsetCalldata; j < offsetCalldata + callLen[i]; j++) {
                newArray[j] = array[j];
            }
            offsetCalldata += callLen[i];
        }
        for (uint256 i = 0; i < array.length - (offsetCalldata + callLen[index]); i++) {
            newArray[offsetCalldata + i] = array[array.length - (offsetCalldata + callLen[index]) + i];
        }
    }

    function removeBytes4ArrayWithLen(
        uint256[] memory callLen,
        bytes4[] memory array,
        uint256 index
    ) public pure returns (bytes4[] memory newArray) {
        newArray = new bytes4[](array.length - callLen[index]);
        uint256 offsetCalldata = 0;
        for (uint256 i = 0; i < index; i++) {
            for (uint256 j = offsetCalldata; j < offsetCalldata + callLen[i]; j++) {
                newArray[j] = array[j];
            }
            offsetCalldata += callLen[i];
        }
        for (uint256 i = 0; i < array.length - (offsetCalldata + callLen[index]); i++) {
            newArray[offsetCalldata + i] = array[array.length - (offsetCalldata + callLen[index]) + i];
        }
    }

    function removeBytes32ArrayWithLen(
        uint256[] memory callLen,
        bytes32[][] memory array,
        uint256 index
    ) public pure returns (bytes32[][] memory newArray) {
        newArray = new bytes32[][](array.length - callLen[index]);
        uint256 offsetCalldata = 0;
        for (uint256 i = 0; i < index; i++) {
            for (uint256 j = offsetCalldata; j < offsetCalldata + callLen[i]; j++) {
                newArray[j] = array[j];
            }
            offsetCalldata += callLen[i];
        }
        for (uint256 i = 0; i < array.length - (offsetCalldata + callLen[index]); i++) {
            newArray[offsetCalldata + i] = array[array.length - (offsetCalldata + callLen[index]) + i];
        }
    }

    function removeUint256ArrayWithLen(
        uint256[] memory callLen,
        uint256[] memory array,
        uint256 index
    ) public pure returns (uint256[] memory newArray) {
        newArray = new uint256[](array.length - callLen[index]);
        uint256 offsetCalldata = 0;
        for (uint256 i = 0; i < index; i++) {
            for (uint256 j = offsetCalldata; j < offsetCalldata + callLen[i]; j++) {
                newArray[j] = array[j];
            }
            offsetCalldata += callLen[i];
        }
        for (uint256 i = 0; i < array.length - (offsetCalldata + callLen[index]); i++) {
            newArray[offsetCalldata + i] = array[array.length - (offsetCalldata + callLen[index]) + i];
        }
    }

}