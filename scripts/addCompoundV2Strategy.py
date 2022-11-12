from brownie import DebtAllocator, accounts


## Supply rate = Ut *  Vt * (1 - Rt)
# Ut, the utilisation ratio
# Vt, the variable rate
# Rt, the reserve factor

# average variable rate Vt = R0 + (Ut/Uo)* R1 if Ut < Uo, R0 + R1 + (Ut - Uo)/ (1 - Uo)R2v else
# R0, Base Variable Borrow Rate
# R1, Variable Rate Slope 1
# R2, Variable Rate Slope 2
# Uo, optimal utilization rate

## Ut = available liquidity / (available liquidity  + variable debt - reservepool)

## Head to https://docs.compound.finance/v2/#networks, get the wanted cToken address and call getCash(), totalBorrows(), totalReserves(), reserveFactorMantissa()

## Head to https://docs.compound.finance/v2/#networks, get the wanted cToken address get the interest rate contract address and call  kink(), multiplierPerBlock(), jumpMultiplierPerBlock(), baseRatePerBlock()


## The following data is valid for Goerli, with WETH ASSET
cETH = "0x64078a6189Bf45f80091c6Ff2fCEe1B15Ac8dbde"
INTEREST_RATE_CETH = "0xB24D5c2F5d881689C14F69Dd4a7118C89747D403"

## getCash
CONTRACT_ADDRESS_0 = cETH
## 0x3b1d21a2 (selector from getCash())
CHECKDATA_0 = "0x3b1d21a2"
STRATEGYY_OFFSET_0 = 0

## totalBorrows()
CONTRACT_ADDRESS_1 = cETH
## 0x47bd3718 (selector from totalBorrows()) 
CHECKDATA_1 = "0x47bd3718"
STRATEGYY_OFFSET_1 = 0

## totalReserves() 
CONTRACT_ADDRESS_2 = cETH
## 0x8f840ddd (selector from totalReserves())
CHECKDATA_2 = "0x8f840ddd"
STRATEGYY_OFFSET_2 = 0

## reserveFactorMantissa() 
CONTRACT_ADDRESS_3 = cETH
## 0x173b9904 (selector from reserveFactorMantissa()) 
CHECKDATA_3 = "0x173b9904"
STRATEGYY_OFFSET_3 = 0

## Optimal utilization rate  
CONTRACT_ADDRESS_4 = INTEREST_RATE_CETH
## 0x35ea6a75 (selector from kink() ) 
CHECKDATA_4 = "0xfd2da339"
STRATEGYY_OFFSET_4 = 0

## multiplierPerBlock R1
CONTRACT_ADDRESS_5 = INTEREST_RATE_CETH
## 0x8726bb89 (selector from multiplierPerBlock() ) 
CHECKDATA_5 = "0x8726bb89"
STRATEGYY_OFFSET_5 = 0

## jumpMultiplierPerBlock R2
CONTRACT_ADDRESS_6 = INTEREST_RATE_CETH
## 0xb9f9850a (selector from jumpMultiplierPerBlock() ) 
CHECKDATA_6 = "0xb9f9850a"
STRATEGYY_OFFSET_6 = 0

## baseRatePerBlock R0
CONTRACT_ADDRESS_7 = INTEREST_RATE_CETH
## 0xf14039de (selector from baseRatePerBlock() ) 
CHECKDATA_7 = "0xf14039de"
STRATEGYY_OFFSET_7 = 0

# concerned strategy address
STRATEGY_ADDRESS= "0x76aFA2b8C29E1B277A3BB1CD320b2756c1674c91" 

MAX_STRATEGY_DEBT_RATIO = 10000

# contracts to get data from
STRATEGY_CONTRACTS = [CONTRACT_ADDRESS_0, CONTRACT_ADDRESS_1, CONTRACT_ADDRESS_2, CONTRACT_ADDRESS_3, CONTRACT_ADDRESS_4, CONTRACT_ADDRESS_5, CONTRACT_ADDRESS_6, CONTRACT_ADDRESS_7]

# checkdata (selector + neccessary args bytes32)
STRATEGYY_CHECKDATA = [CHECKDATA_0, CHECKDATA_1, CHECKDATA_2, CHECKDATA_3, CHECKDATA_4, CHECKDATA_5, CHECKDATA_6, CHECKDATA_7]

# offset, which args we need from the data received from the call, 0 by default
STRATEGYY_OFFSET = [STRATEGYY_OFFSET_0, STRATEGYY_OFFSET_1, STRATEGYY_OFFSET_2, STRATEGYY_OFFSET_3, STRATEGYY_OFFSET_4, STRATEGYY_OFFSET_5, STRATEGYY_OFFSET_6, STRATEGYY_OFFSET_7]


# ////////CASE Ut > Uo

# calcul cash + total borrow
# Step0 = 0, 1, 0

# calcul step1 - reserve
# Step1 = 10000, 2, 1

# calcul totalBorrow * precision 10^18
# Step2 = 1, 1000000000000020000, 2

# calcul Step2 / step 1                         
# Step3 = 10002, 10001, 3             Step3: Ut (10^18)

# calcul kink x R1
# Step4 = 4, 5, 2

# calcul step 4 / Precision         R1*kink
# Step5 = 10004, 1000000000000020000, 3     

# calcul step 5 + RO
# Step6 = 10005, 7, 0           R1*kink + RO

# calcul Ut(10^18) - Uo (kink)
# Step7 = 10003, 4, 1


# calcul step7 * R2
# Step8 = 10007, 6, 2      

# calcul Step8 / Precision
# Step9 = 10008, 1000000000000020000, 3      R2(Ut - Uo)

# calcul R1*kink + RO + R2(Ut - Uo)
# Step10 = 10009, 10006, 0                     Vt = R1*kink + RO + R2(Ut - Uo) Step 10

# Calcul ( 10^18 - reserveFactorMantissa) 
# Step11 = 1000000000000020000, 3, 1

# Calcul ( VT * step11*(10^18)) 
# Step12 = 10010, 10011, 2

# [0, 1, 0, 10000, 2, 1, 1, 1000000000000020000, 2, 10002, 10001, 3, 4, 5, 2, 10004, 1000000000000020000, 
# 3, 4, 5, 2, 10004, 1000000000000020000, 3, 10005, 7, 0, 10003, 4, 1, 10007, 6, 2, 10008, 1000000000000020000, 3,
# 1000000000000020000, 3, 1, 10010, 10011, 2, 10012, 1000000000000020000, 3, 10013, 10003, 2, 10015, 1000000000000020000, 3]

# Calcul Step13 / Precision
# Step13 = 10012, 1000000000000020000, 3

# Step 13 * Ut(10^18)
# Step14 = 10013, 10003, 2

# Step 15 Supply rate per block
# Step15 = 10015, 1000000000000020000, 3



# ////////CASE Ut <= Uo

# calcul cash + total borrow
# Step0 = 0, 1, 0

# calcul step1 - reserve
# Step1 = 10000, 2, 1

# calcul totalBorrow * precision 10^18
# Step2 = 1, 1000000000000020000, 2

# calcul Step2 / step 1                         
# Step3 = 10002, 10001, 3             Step3: Ut (10^18)

# calcul Step3 * R1                   
# Step4 = 10003, 5, 2

# calcul Step3 / Precision                   
# Step5 = 10004, 1000000000000020000, 3

# calcul Step4 + RO                    
# Step6 = 10005, 7, 0                   Step6: Ut*R1 + R0 

# Calcul ( 10^18 - reserveFactorMantissa) 
# Step7 = 1000000000000020000, 3, 1

# [0, 1, 0, 10000, 2, 1, 1, 1000000000000020000, 2, 10002, 10001, 3 , 10003, 5, 2, 10004, 1000000000000020000, 3
# 10005, 7, 0 , 1000000000000020000, 3, 1, 10007, 10006, 2, 10008, 1000000000000020000, 3, 10009, 10003, 2, 10010, 1000000000000020000, 3]

# Calcul (Ut*R1 + R0) * (1 - Rt) *(10^18)
# Step8 = 10007, 10006, 2

# Calcul Step8 / Precision
# Step9 = 10008, 1000000000000020000, 3    

# Calcul Step9 * Ut (10^18)
# Step10 = 10009, 10003, 2

# Calcul Step10 / Precision
# Step11 = 10010, 1000000000000020000, 3

## Not ok len = 16 + ok len 11 tot 27, offset 16
STRATEGYY_CALCULATION = [0, 1, 0, 10000, 2, 1, 1, 1000000000000020000, 2, 10002, 10001, 3, 4, 5, 2, 10004, 1000000000000020000, 3, 4, 5, 2, 10004, 1000000000000020000, 3, 10005, 7, 0, 10003, 4, 1, 10007, 6, 2, 10008, 1000000000000020000, 3, 1000000000000020000, 3, 1, 10010, 10011, 2, 10012, 1000000000000020000, 3, 10013, 10003, 2, 10015, 1000000000000020000, 3, 0, 1, 0, 10000, 2, 1, 1, 1000000000000020000, 2, 10002, 10001, 3 , 10003, 5, 2, 10004, 1000000000000020000, 310005, 7, 0 , 1000000000000020000, 3, 1, 10007, 10006, 2, 10008, 1000000000000020000, 3, 10009, 10003, 2, 10010, 1000000000000020000, 3]
## ! add 27 script


# calcul cash + total borrow
# Step0 = 0, 1, 0

# calcul step1 - reserve
# Step1 = 10000, 2, 1

# calcul totalBorrow * precision 10^18
# Step2 = 1, 1000000000000020000, 2

# calcul Step2 / step 1                         
# Step3 = 10002, 10001, 3             Step3: Ut (10^18)


CALCULATION_CONDITION = [0, 1, 0, 10000, 2, 1, 1, 1000000000000020000, 2, 10002, 10001, 3, 10003, 4, 16, 27]
## add len for script 4

def main():
    acct = accounts.load('sach')
    DebtAllocator[1].addStrategy(STRATEGY_ADDRESS, MAX_STRATEGY_DEBT_RATIO, STRATEGY_CONTRACTS, STRATEGYY_CHECKDATA, STRATEGYY_OFFSET, STRATEGYY_CALCULATION, CALCULATION_CONDITION,{'from': acct})
