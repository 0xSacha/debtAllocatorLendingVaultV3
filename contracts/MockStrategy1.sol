//SPDX-License-Identifier: UNLICENSED

contract MockStrategy {
    uint256 public apiVersion = 2;
    uint256 public totalAssets = 50*10**18;

    function updateTotalAssets() public {
        totalAssets = 500*10**18;
    }

}

contract MockStrategy2 {
    uint256 public apiVersion = 2;
    uint256 public totalAssets = 10*10**18;

    function updateTotalAssets() public {
        totalAssets = 500*10**18;
    }

}

