# StarkDebtAllocator
The objective of this PoC is decentralizing even more the process to choose strategy weights within a vault. 

StarkDebtAllocator is the contract in charge of receiving and validating debt ratio proposals, that will come from any proposer.  

It uses (zk-)STARKS through Starware's Cairo, SHARP prover and L1 verifier to generate proofs that make it possible to be sure that they are valid solutions without spending a ton of gas running the computation on-chain.	

To incentivize people running the calculations and proposing solutions, the solution proposer will earn rewards during the time their solution is used. 	

## Intro	
Currently, debt ratios are proposed by vault managers and approved by a multisig. Vault managers analyze how each of the strategies is performing, checking their different APYs and then come up with a set of debt ratios, which are set manually. 

{	
    "strategy1": 2500,
    "strategy2": 2500,
    "strategy3": 3500,	
    "strategy4": 1500	
}	

This process requires manual intervention and brings a lot of overhead with it.	

## Solution	
The PoC is composed of 2 parts: L1 smart contract and Cairo Program	

StarkDebtAllocator is one Ethereum L1 smart contract. 	

It implements two (main) functions:	
- saveSnapshot(): reads all the on-chain data that will be used as inputs for the Cairo Program and hashes them all, then saves the hash. 
- verifySolution(uint256[] programOutput): 	
	- Check not staled Snapshot (we need to make sure we calculate the APY with fresh data)
	- parses programOutput to the following values: uint256 inputsHash, uint256[] current_debt_ration, _new_debt_ration, current_solution, new_solution.
	- checks that the inputsHash has been saved before as is not stale and that it corresponds to the inputsHash used in the cairo program (from programOutput). Note that cairo felt isn't big enought to support 256 bits (252 bits max), that's why 2 slot of the programOutput are used to calculate the input hash from strategies input, 128 bits each.	
	- checks that each debt ratio is not bigger than the maxValue stored for the associated strategy. Also check the sum of the new debt ratio tab elements = 100%, and the current debt ratio is the same as the saved one.
	- checks that the new solution is better than the previous solution, for user experience purpose, a minimum increase is necessary so the proposer won't change for a certain moment. Also the current solution is calculated in the cairo script better than the saved one in storage so we make sure we get real the current APY (with valid inputs).
	- checks that the CairoVerifier from Starkware has received the proof and confirmed it is correct	
	- sets the new winning solution, the new debt ratio array and store the address of the user and his performance.	

apy_calculator.cairo is the Cairo program that takes a set of debt ratios for certain strategies and calculates the weighted average APY for the whole set of strategies. 	

This Cairo program will compute a hash of all the inputs it has used to calculate APYs to send it to the L1 smart contract, so inputs can be validated. 	

## Details	
![Diagram](./starkdebtallocator.png)	


## Test

To Add test/debtAllocatorTest.js


## Script	

Follow these steps: 	
- add account with brownie

- Deploy DebtAllocator.sol providing by running brownie run deployDebtAllocator (you can find the cairo programHash running sh programhash.sh and the cairo verifier address here https://www.cairo-lang.org/playground-sharp-alpha/)

- Add Strategies with brownie run addStrategy , you need to provide the strategy address, the contracts to call, the selectors and also the offset, 0 by default and set it to 32*wanted value index from the returned tupple. 
Provide the calculation logic and the condition logic (more details below). Supply rate from Aave V2 and compoundv2 (including liquidity mining) are provided as example.

- brownie run saveSnapshot. The function returns the strategies input tab, (data, calculation & conditions), use it to fill apy_calculator_input.json. 	For cairo script input, it is necessary to add the tab len before the array.

- Provide the current debt ratio and the new debt ratio configuration for the stratgies and add it in apy_calculator_input.json ("debt_ratio":[2000, 7500, 500] for exemple).Compile, run the cairo program and send its proof to the SHARP, you can use sh run.sh to do it in one step.	
![Diagram](./Screenshot_output.png)


- Invoke verifySolution providing the output you got from the last step.


## Calculation Logic

Each Strategy APY is calculated in the cairo program hash. Better than modifying the cairo program every time a new strategy is added (which involves modifying the cairo program hash on the debtAllocator contract), the strategy APY calculation is given as an input. 

The calculation follow this logic: 

Each step performs an operation of 2 operands.
The operand is between 0 and 10000, we take the value of the input data
The operand is between 10000 and 20000, we take the value of the last calculation steps.
The operand is more than 20000, we take the value - 20 000
the operation is described by a uint, 0 = +, 1 = -, 2 = x, 3 = /

Exemple for a strategy: 
Input: [4,7,2]
Calculation_logic: [4, 1,0,0, 10000,2,2, 10001,20010,1, 10002,2,3]

step0 -> 7(input 1) + 4 (input 0)

step1 -> 11 (step0) * 2 (input 2)

step2 -> 22 (step1) - 10 (20010 - 20000)

step3 -> 12(step2) / 2 (input 2)

res = 6 ✨

The Strategy APR can be different following some conditions.

The cairo script can perfom calculations and check if the last step is lower or equal to a value. If it does, a new calculation tab is extracted from the original one, following the offset and the new calculation len.

Condition logic: [2, 0, 2, 2, 1, 20002, 1, 10001, 10000, 26, 20]

Step 0 ->  4 (input 0) x 2 (input 2)

Step 1 ->  7 (input 1) - 2 (20002 - 20000)

FinalStep ->  5(step1) <= 8(step0) ? 
oui -> jump offset 26 and tab len = 20

