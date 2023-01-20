//SPDX-License-Identifier: UNLICENSED
import "../interfaces/IVault.sol" as IVault;

struct StrategyParams {
    uint256 activation;
    uint256 last_report;
    uint256 current_debt;
    uint256 max_debt;
}

contract MockVault {
    uint256 public totalAssets = 50 * 10**18;
    mapping(address => StrategyParams) public strategies;

    function addStrategy(address strategy, StrategyParams memory params)
        public
    {
        strategies[strategy] = params;
    }

    function update_debt(address strategy, uint256 target_debt) public {}

    function tend_strategy(address) external {}

    function process_report(address) external {}
}
