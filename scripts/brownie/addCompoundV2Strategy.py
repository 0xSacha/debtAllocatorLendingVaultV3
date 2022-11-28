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

## Head to https://docs.compound.finance/v2/#networks, get the wanted Comptroller address get the compSupplySpeeds

## Head to https://docs.chain.link/docs/data-feeds/price-feeds/addresses/ get the oracle pair COMP/USD, call() pair and the 


## The following data is valid for Goerli, with cUSDC ASSET, implementation for weth differ from mainet
WANTED_TOKEN = "0x07865c6E87B9F70255377e024ace6630C1Eaa37F"
cTOKEN = "0x73506770799Eb04befb5AaE4734e58C2C624F493"
INTEREST_RATE_cTOKEN = "0xef5ae06093bdFc54Fbc804C7627B15dAE98Ca5e7"
Comptroller = "0x05Df6C772A563FfB37fD3E04C1A279Fb30228621"
## not available on goerli so DAI/USD is taken 
COMP_USD = "0x0d79df66BE487753B02D015Fb622DED7f0E9798d"
## usdc token as wanted token
WANTED_TOKEN_USD = "0xAb5c49580294Aff77670F839ea425f5b78ab3Ae7"


## getCash
CONTRACT_ADDRESS_0 = cTOKEN
## 0x3b1d21a2 (selector from getCash())
CHECKDATA_0 = "0x3b1d21a2"
STRATEGYY_OFFSET_0 = 0

## totalBorrows()
CONTRACT_ADDRESS_1 = cTOKEN
## 0x47bd3718 (selector from totalBorrows()) 
CHECKDATA_1 = "0x47bd3718"
STRATEGYY_OFFSET_1 = 0

## totalReserves() 
CONTRACT_ADDRESS_2 = cTOKEN
## 0x8f840ddd (selector from totalReserves())
CHECKDATA_2 = "0x8f840ddd"
STRATEGYY_OFFSET_2 = 0

## reserveFactorMantissa() 
CONTRACT_ADDRESS_3 = cTOKEN
## 0x173b9904 (selector from reserveFactorMantissa()) 
CHECKDATA_3 = "0x173b9904"
STRATEGYY_OFFSET_3 = 0

## Optimal utilization rate  
CONTRACT_ADDRESS_4 = INTEREST_RATE_cTOKEN
## 0x35ea6a75 (selector from kink() ) 
CHECKDATA_4 = "0xfd2da339"
STRATEGYY_OFFSET_4 = 0

## multiplierPerBlock R1
CONTRACT_ADDRESS_5 = INTEREST_RATE_cTOKEN
## 0x8726bb89 (selector from multiplierPerBlock() ) 
CHECKDATA_5 = "0x8726bb89"
STRATEGYY_OFFSET_5 = 0

## jumpMultiplierPerBlock R2
CONTRACT_ADDRESS_6 = INTEREST_RATE_cTOKEN
## 0xb9f9850a (selector from jumpMultiplierPerBlock() ) 
CHECKDATA_6 = "0xb9f9850a"
STRATEGYY_OFFSET_6 = 0

## baseRatePerBlock R0
CONTRACT_ADDRESS_7 = INTEREST_RATE_cTOKEN
## 0xf14039de (selector from baseRatePerBlock() ) 
CHECKDATA_7 = "0xf14039de"
STRATEGYY_OFFSET_7 = 0

## blocksPerYear() R0
CONTRACT_ADDRESS_8 = INTEREST_RATE_cTOKEN
## 0xa385fb96 (selector from blocksPerYear() ) 
CHECKDATA_8 = "0xa385fb96"
STRATEGYY_OFFSET_8 = 0

##compSupplySpeeds(address)
CONTRACT_ADDRESS_9 = Comptroller
## 0x6aa875b5 (selector from compSupplySpeeds(address) ) 
CHECKDATA_9 = "0x6aa875b500000000000000000000000073506770799Eb04befb5AaE4734e58C2C624F493"
STRATEGYY_OFFSET_9 = 0

##latestAnswer()
CONTRACT_ADDRESS_10 = COMP_USD
## 0x50d25bcd (selector from latestAnswer() ) 
CHECKDATA_10 = "0x50d25bcd"
STRATEGYY_OFFSET_10 = 0

##decimals()
CONTRACT_ADDRESS_11 = COMP_USD
## 0x313ce567 (selector from decimals() ) 
CHECKDATA_11 = "0x313ce567"
STRATEGYY_OFFSET_11 = 0

##latestAnswer()
CONTRACT_ADDRESS_12 = WANTED_TOKEN_USD
## 0x50d25bcd (selector from latestAnswer() ) 
CHECKDATA_12 = "0x50d25bcd"
STRATEGYY_OFFSET_12 = 0

##decimals()
CONTRACT_ADDRESS_13 = WANTED_TOKEN_USD
## 0x313ce567 (selector from decimals() ) 
CHECKDATA_13 = "0x313ce567"
STRATEGYY_OFFSET_13 = 0

##decimals()
CONTRACT_ADDRESS_14 = WANTED_TOKEN
## 0x313ce567 (selector from decimals() ) 
CHECKDATA_14 = "0x313ce567"
STRATEGYY_OFFSET_14 = 0

# concerned strategy address
STRATEGY_ADDRESS= "0x76aFA2b8C29E1B277A3BB1CD320b2756c1674c91" 

MAX_STRATEGY_DEBT_RATIO = 10000

# contracts to get data from
STRATEGY_CONTRACTS = [CONTRACT_ADDRESS_0, CONTRACT_ADDRESS_1, CONTRACT_ADDRESS_2, CONTRACT_ADDRESS_3, CONTRACT_ADDRESS_4, CONTRACT_ADDRESS_5, CONTRACT_ADDRESS_6, CONTRACT_ADDRESS_7, CONTRACT_ADDRESS_8, CONTRACT_ADDRESS_9, CONTRACT_ADDRESS_10, CONTRACT_ADDRESS_11, CONTRACT_ADDRESS_12, CONTRACT_ADDRESS_13, CONTRACT_ADDRESS_14]

# checkdata (selector + neccessary args bytes32)
STRATEGYY_CHECKDATA = [CHECKDATA_0, CHECKDATA_1, CHECKDATA_2, CHECKDATA_3, CHECKDATA_4, CHECKDATA_5, CHECKDATA_6, CHECKDATA_7, CHECKDATA_8, CHECKDATA_9, CHECKDATA_10, CHECKDATA_11, CHECKDATA_12, CHECKDATA_13, CHECKDATA_14]

# offset, which args we need from the data received from the call, 0 by default
STRATEGYY_OFFSET = [STRATEGYY_OFFSET_0, STRATEGYY_OFFSET_1, STRATEGYY_OFFSET_2, STRATEGYY_OFFSET_3, STRATEGYY_OFFSET_4, STRATEGYY_OFFSET_5, STRATEGYY_OFFSET_6, STRATEGYY_OFFSET_7,STRATEGYY_OFFSET_8, STRATEGYY_OFFSET_9, STRATEGYY_OFFSET_10, STRATEGYY_OFFSET_11, STRATEGYY_OFFSET_12,STRATEGYY_OFFSET_13, STRATEGYY_OFFSET_14]


# ////////CASE Ut > Uo

## Precision 10^18 kink, reserve factor  
# calcul cash + total borrow
# Step0 = 0, 1, 0

# calcul step1 - reserve     total supply asset
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

# Calcul ( VT * step11) 
# Step13 = 10012, 1000000000000020000, 3                      Supply rate per block step 13 

# Calcul Step13 * Ut (10^18)
# Step14 = 10013, 10003, 2

# Calcul Step14 / Precision
# Step15 = 10014, 1000000000000020000, 3

# Calcul Step15 * blockperyear
# Step16 = 10015, 8, 2                          APR supply * 10^18

###### LiquidityMining APY`

# Calcul compSupplySpeeds() per year ( * block/year) 
# Step17 = 9, 8, 2                                  COMP for supplier per Year step 17

# Calcul 10^wantedtoken decimals
# Step18 = 20010, 14, 4

# Calcul step 17 * 10^wantedtoken decimals 
# Step19 = 10017, 10018, 2

# Calcul  comp in a year / total in supply =         APR in COMP step 20
# Step20 = 10019, 10001, 3   

# Calcul Step 20 in USD * 10^oracle decimals
# Step21 = 10020, 10, 2                    

# Calcul 10^decimals oracle comp usd
# Step22 = 20010, 11, 4

# Calcul  Step 18 in USD
# Step23 = 10021, 10022, 3                              APR in USD step 23

# Calcul 10^decimals oracle wanted token usd
# Step24 = 20010, 13, 4

# Calcul Step23 * 10^oracle decimals 
# Step25 = 10023, 10024, 2

# Calcul Step 18 in Wanted token
# Step26 = 10025, 12, 3                                 APR in WANTED token Step 26 (10^18)

# Calcul totoal apr 10^18           TOTAL APR (10^18)
# Step27 = 10026, 10016, 0 

# Calcul (total APR 10^27)                          TOTAL APR (10^27)
# Step28 = 10027, 1000020000, 2 

## 28 step      LEN = 29

# 1, 5 and last each lign
# [0, 1, 0, 
# 10000, 2, 1, 1, 1000000000000020000, 2, 10002, 10001, 3, 4, 5, 2, 10004, 1000000000000020000, 3,
# 10005, 7, 0, 10003, 4, 1, 10007, 6, 2, 10008, 1000000000000020000, 3, 10009, 10006, 0, 
# 1000000000000020000, 3, 1, 10010, 10011, 2, 10012, 1000000000000020000, 3, 10013, 10003, 2, 10014, 1000000000000020000, 3,
# 10015, 8, 2, 9, 8, 2, 20010, 14, 4, 10017, 10018, 2, 10019, 10001, 3,
# 10020, 10, 2, 20010, 11, 4, 10021, 10022, 3, 20010, 13, 4, 10023, 10024, 2,
# 10025, 12, 3, 10026, 10016, 0 , 10027, 1000020000, 2]


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

# Calcul (Ut*R1 + R0) * (1 - Rt) *(10^18)
# Step8 = 10007, 10006, 2

# Calcul Step8 / Precision
# Step9 = 10008, 1000000000000020000, 3    

# Calcul Step9 * Ut (10^18)
# Step10 = 10009, 10003, 2

# Calcul Step10 / Precision
# Step11 = 10010, 1000000000000020000, 3

# Calcul Step11 * blockperyear
# Step12 = 10011, 8, 2                          APR supply * 10^18

###### LiquidityMining APY`

# Calcul compSupplySpeeds() per year ( * block/year) 
# Step13 = 9, 8, 2                                  COMP for supplier per Year step 13

# Calcul 10^wantedtoken decimals
# Step14 = 20010, 14, 4

# Calcul step 13 * 10^wantedtoken decimals 
# Step15 = 10013, 10014, 2

# Calcul  comp in a year / total in supply =         APR in COMP step 18
# Step16 = 10015, 10001, 3   

# Calcul Step 16 in USD * 10^oracle decimals
# Step17 = 10016, 10, 2                    

# Calcul 10^decimals oracle comp usd
# Step18 = 20010, 11, 4

# Calcul  Step 18 in USD
# Step19 = 10017, 10018, 3                              APR in USD step 19

# Calcul 10^decimals oracle wanted token usd
# Step20 = 20010, 13, 4

# Calcul Step19 * 10^oracle decimals 
# Step21 = 10019, 20020, 2

# Calcul Step 18 in Wanted token
# Step22 = 10021, 12, 3                                 APR in WANTED token Step 24 (10^18)

# Calcul totoal apr 10^18           TOTAL APR (10^18)
# Step23 = 10022, 10012, 0 

# Calcul (total APR 10^27)                          TOTAL APR (10^27)
# Step24 = 10023, 1000020000, 2 


## 24 step      LEN = 25

# [0, 1, 0, 
# 10000, 2, 1, 1, 1000000000000020000, 2, 10002, 10001, 3, 10003, 5, 2, 10004, 1000000000000020000, 3,
# 10005, 7, 0, 1000000000000020000, 3, 1, 10007, 10006, 2, 10008, 1000000000000020000, 3, 10009, 10003, 2,
# 10010, 1000000000000020000, 3, 10011, 8, 2, 9, 8, 2, 20010, 14, 4, 10013, 10014, 2,
# 10015, 10001, 3, 10016, 10, 2, 20010, 11, 4, 10017, 10018, 3, 20010, 13, 4,
# 20019, 20020, 2, 10021, 12, 3, 10022, 10012, 0, 10023, 1000020000, 2]



## Not ok len = 29 + ok len 25 tot 54, offset 29

STRATEGYY_CALCULATION = [0, 1, 0, 10000, 2, 1, 1, 1000000000000020000, 2, 10002, 10001, 3, 4, 5, 2, 10004, 1000000000000020000, 3, 10005, 7, 0, 10003, 4, 1, 10007, 6, 2, 10008, 1000000000000020000, 3, 10009, 10006, 0, 
1000000000000020000, 3, 1, 10010, 10011, 2, 10012, 1000000000000020000, 3, 10013, 10003, 2, 10014, 1000000000000020000, 3, 10015, 8, 2, 9, 8, 2, 20010, 14, 4, 10017, 10018, 2, 10019, 10001, 3,
10020, 10, 2, 20010, 11, 4, 10021, 10022, 3, 20010, 13, 4, 10023, 10024, 2, 10025, 12, 3, 10026, 10016, 0 , 10027, 1000020000, 2, 0, 1, 0, 10000, 2, 1, 1, 1000000000000020000, 2, 10002, 10001, 3, 10003, 5, 2, 10004, 1000000000000020000, 3,
10005, 7, 0, 1000000000000020000, 3, 1, 10007, 10006, 2, 10008, 1000000000000020000, 3, 10009, 10003, 2, 10010, 1000000000000020000, 3, 10011, 8, 2, 9, 8, 2, 20010, 14, 4, 10013, 10014, 2,
10015, 10001, 3, 10016, 10, 2, 20010, 11, 4, 10017, 10018, 3, 20010, 13, 4, 10019, 20020, 2, 10021, 12, 3, 10022, 10012, 0, 10023, 1000020000, 2]
## ! add len 54 script cairo


# calcul cash + total borrow
# Step0 = 0, 1, 0

# calcul step1 - reserve
# Step1 = 10000, 2, 1

# calcul totalBorrow * precision 10^18
# Step2 = 1, 1000000000000020000, 2

# calcul Step2 / step 1                         
# Step3 = 10002, 10001, 3             Step3: Ut (10^18)

# final Step                        
# finalStep = 10003, 4, 29, 25             Step3: Ut (10^18)

CALCULATION_CONDITION = [0, 1, 0, 10000, 2, 1, 1, 1000000000000020000, 2, 10002, 10001, 3, 10003, 4, 29, 25]
## add len 4 for cairo script 

def main():
    acct = accounts.load('sach')
    DebtAllocator[0].addStrategy(STRATEGY_ADDRESS, MAX_STRATEGY_DEBT_RATIO, STRATEGY_CONTRACTS, STRATEGYY_CHECKDATA, STRATEGYY_OFFSET, STRATEGYY_CALCULATION, CALCULATION_CONDITION,{'from': acct})
