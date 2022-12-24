//SPDX-License-Identifier: UNLICENSED

pragma solidity >=0.7.0 <0.9.0;

contract DebtAllocatorUtils {

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

    // UTILS
    function checkStrategyHash(
        PackedStrategies memory _packedStrategies,
        uint256 strategiesHash
    ) internal pure {

        bytes32[] memory callDataReduced = getReducedBytes32Array(_packedStrategies.callData);
        require(
            strategiesHash ==
                uint256(
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
                ),
            "DATA"
        );
    }

    function parseProgramOutput(
        uint256[] calldata programOutput
    )
        public
        pure
        returns (
            uint256 _inputHash,
            uint256[] memory _currentTargetAllocation,
            uint256[] memory _newTargetAllocation,
            uint256 _currentSolution,
            uint256 _newSolution
        )
    {
        _inputHash = programOutput[0] << 128;
        _inputHash += programOutput[1];

        _currentTargetAllocation = new uint256[](programOutput[2]);

        _newTargetAllocation = new uint256[](programOutput[2]);

        for (uint256 i = 0; i < programOutput[2]; i++) {
            // NOTE: skip the 2 first value + array len
            _currentTargetAllocation[i] = programOutput[i + 3];
            _newTargetAllocation[i] = programOutput[i + 4 + programOutput[2]];
        }
        return (
            _inputHash,
            _currentTargetAllocation,
            _newTargetAllocation,
            programOutput[programOutput.length - 2],
            programOutput[programOutput.length - 1]
        );
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

    function bytesToBytes32(
        bytes memory b,
        uint offset
    ) internal pure returns (bytes32 result) {
        offset += 32;
        assembly {
            result := mload(add(b, offset))
        }
    }

    function castCheckdataToBytes4 (
        bytes[] memory oldCheckdata
    ) internal pure returns (bytes4[] memory checkdata) {
        checkdata = new bytes4[](oldCheckdata.length);
        for (uint256 i = 0; i < oldCheckdata.length; i++) {
            checkdata[i] = bytes4(oldCheckdata[i]);
        }
    }

    function checkValidityOfData(
        StrategyParam memory _newStrategyParam
    ) internal {
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

    function appendAddressToArray(
        address[] memory array,
        address newItem
    ) internal pure returns (address[] memory newArray) {
        newArray = new address[](array.length + 1);
        for (uint256 i = 0; i < array.length; i++) {
            newArray[i] = array[i];
        }
        newArray[array.length] = newItem;
    }

    function appendUint256ToArray(
        uint256[] memory array,
        uint256 newItem
    ) internal pure returns (uint256[] memory newArray) {
        newArray = new uint256[](array.length + 1);
        for (uint256 i = 0; i < array.length; i++) {
            newArray[i] = array[i];
        }
        newArray[array.length] = newItem;
    }

    function concatenateUint256ArrayToUint256Array(
        uint256[] memory arrayA,
        uint256[] memory arrayB
    ) internal pure returns (uint256[] memory newArray) {
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
    ) internal pure returns (address[] memory newArray) {
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
    ) internal pure returns (bytes4[] memory newArray) {
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
    ) internal pure returns (bytes32[][] memory newArray) {
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
    ) internal pure returns (uint256[] memory newArray) {
        newArray = array;
        newArray[index] = newItem;
    }

    function updateAddressArrayWithLen(
        uint256[] memory callLen,
        address[] memory array,
        uint256 newCallLen,
        address[] memory newArray,
        uint256 index
    ) internal pure returns (address[] memory newAddressArray) {
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
    ) internal pure returns (bytes4[] memory newBytes4Array) {
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
    ) internal pure returns (bytes32[][] memory newBytes32DoubleArray) {
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
        uint256[] memory callLen,
        uint256[] memory array,
        uint256 newCallLen,
        uint256[] memory newArray,
        uint256 index
    ) internal pure returns (uint256[] memory newUint256Array) {
        newUint256Array = new uint256[](array.length - callLen[index] + newCallLen);
        uint256 offsetCalldata = 0;
        for (uint256 i = 0; i < index; i++) {
            for (uint256 j = offsetCalldata; j < offsetCalldata + callLen[i]; j++) {
                newUint256Array[j] = array[j];
            }
            offsetCalldata += callLen[i];
        }
        for (uint256 i = 0; i < newCallLen; i++) {
            newUint256Array[offsetCalldata + i] = newArray[i];
        }
        for (uint256 i = 0; i < array.length - (offsetCalldata + callLen[index]); i++) {
            newUint256Array[offsetCalldata + newCallLen + i] = array[array.length - (offsetCalldata + callLen[index]) + i];
        }
    }

    function removeUint256Array(
        uint256[] memory array,
        uint256 index
    ) internal pure returns (uint256[] memory newArray) {
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
    ) internal pure returns (address[] memory newArray) {
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
    ) internal pure returns (bytes4[] memory newArray) {
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
    ) internal pure returns (bytes32[][] memory newArray) {
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
    ) internal pure returns (uint256[] memory newArray) {
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
