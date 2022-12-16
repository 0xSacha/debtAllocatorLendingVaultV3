//SPDX-License-Identifier: UNLICENSED

pragma solidity >=0.7.0 <0.9.0;

contract testStrategyData {
    uint256[] public dataSaved;
    
    function getStrategiesData(
            address[] memory contracts, 
            bytes[] memory checkdata, 
            uint256[] memory offset) public returns(uint256[] memory dataStrategies) {
        delete dataSaved;
        uint256[] memory dataStrategies_ = new uint256[](contracts.length);
        for(uint256 j; j < contracts.length; j++) {
            (, bytes memory data) = contracts[j].call(checkdata[j]);
            dataStrategies_[j] = uint256(bytesToBytes32(data, offset[j]));
            dataSaved.push(dataStrategies_[j]);
        }
       return(dataStrategies_);
    }

    function bytesToBytes32(bytes memory b, uint offset) private pure returns (bytes32) {
        bytes32 out;
        for (uint i = 0; i < 32; i++) {
            out |= bytes32(b[offset + i] & 0xFF) >> (i * 8);
        }
        return out;
    }


}

