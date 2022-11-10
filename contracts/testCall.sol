//SPDX-License-Identifier: UNLICENSED

pragma solidity >=0.7.0 <0.9.0;


interface ICairoVerifier {
    function isValid(bytes32) external view returns (bool);
}

contract testCall {

    function getStrategiesData(address contract_address,bytes calldata checkdata,uint256 offset) public returns(uint256 result) {
        (bool success, bytes memory data) = contract_address.call(checkdata);
        require(success == true, "call didn't succeed");
        bytes32 resultss = bytesToBytes32(data, offset);
        return(uint256(resultss));
    }

   

        
    function bytesToBytes32(bytes memory b, uint offset) private pure returns (bytes32) {
        bytes32 out;
        for (uint i = 0; i < 32; i++) {
            out |= bytes32(b[offset + i] & 0xFF) >> (i * 8);
        }
        return out;
    }
}

