pragma solidity 0.8.17;

contract MockVerifier {
    mapping(bytes32 => bool) public isValid;

    function verifyProgramOutput(bytes32 fact) external {
        isValid[fact] = true;
    }
}
