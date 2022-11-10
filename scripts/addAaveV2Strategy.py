from brownie import DebtAllocator, accounts


## Supply rate = Ut * (SBt*St + VBt*Vt) * (1 - Rt)
# Ut, the utilisation ratio
# SBt, the share of stable borrows
# St, the average stable rate
# VBt, the share of variable borrows
# Vt, the variable rate
# Rt, the reserve factor

# average stable rate St = R0 + (Ut/Uo)* R1 if Ut < Uo, R0 + R1 + (Ut - Uo)/ (1 - Uo)R2s else
# R0, Base Variable Borrow Rate
# R1, stable Rate Slope 1
# R2, stable Rate Slope 2
# R2, stable Rate Slope 2
# Uo, optimal utilization rate

# average variable rate Vt = R0 + (Ut/Uo)* R1 if Ut < Uo, R0 + R1 + (Ut - Uo)/ (1 - Uo)R2v else
# R0, Base Variable Borrow Rate
# R1, Variable Rate Slope 1
# R2, Variable Rate Slope 2
# R2, Variable Rate Slope 2
# Uo, optimal utilization rate

## Ut = available liquidity / (available liquidity + stable debt + variable debt)
## Sbt = stable debt / (stable debt + variable debt)
## VBt = variable debt / (stable debt + variable debt)

## Head to https://docs.aave.com/developers/v/2.0/deployed-contracts/deployed-contracts, get the protocol data provider address and call getReserveConfigurationData(address)  providing the token address, and get the reserveFactor (5th from the tupple), 
## In the same conract call getReserveData(address) providing the token address and get: available liquidity (first), totalStableDebt (second), totalVariableDebt (third)

## Head to https://docs.aave.com/developers/v/2.0/deployed-contracts/deployed-contracts, get the lending pool address, call  getReserveData(address) providing the token address, and get the ReserveInterestRateStrategy adress
## (penultimate data from the returned tupple). From this contract, you'll have access to variableRateSlope1, variableRateSlope2, baseVariableBorrowRate, OPTIMAL_UTILIZATION_RATE, stableRateSlope1 and stableRateSlope2


## The following data is valid for Goerli, with WETH ASSET
WETH = "0xCCa7d1416518D095E729904aAeA087dBA749A4dC"
PROTOCOL_DATA_PROVIDER = "0x927F584d4321C1dCcBf5e2902368124b02419a1E"
RESERVE_INTEREST_RATE_STRATEGY= "0x5ecE040038c822d7228F24D9F2e1Fd41bc77A3c4"

## Reserve Data
CONTRACT_ADDRESS_0 = PROTOCOL_DATA_PROVIDER
## 0x3e150141 (selector from getReserveConfigurationData(address)) + 000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC wethadress to byte32
CHECKDATA_0 = "0x3e150141000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC"
## 5th arg so (5-1)*32 
STRATEGYY_OFFSET_0 = 128

## Available Liquidity
CONTRACT_ADDRESS_1 = PROTOCOL_DATA_PROVIDER
## 0x35ea6a75 (selector from getReserveData(address)) + 000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC wethadress to byte32
CHECKDATA_1 = "0x35ea6a75000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC"
## first arg so 0
STRATEGYY_OFFSET_1 = 0

## totalStableDebt 
CONTRACT_ADDRESS_2 = PROTOCOL_DATA_PROVIDER
## 0x35ea6a75 (selector from getReserveData(address)) + 000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC wethadress to byte32
CHECKDATA_2 = "0x35ea6a75000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC"
## second arg so 32
STRATEGYY_OFFSET_2 = 32

## totalVariableDebt 
CONTRACT_ADDRESS_3 = PROTOCOL_DATA_PROVIDER
## 0x35ea6a75 (selector from getReserveData(address)) + 000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC wethadress to byte32
CHECKDATA_3 = "0x35ea6a75000000000000000000000000CCa7d1416518D095E729904aAeA087dBA749A4dC"
## third arg so 64
STRATEGYY_OFFSET_3 = 64

## totalVariableDebt 
CONTRACT_ADDRESS_4 = RESERVE_INTEREST_RATE_STRATEGY
## 0x35ea6a75 (selector from OPTIMAL_UTILIZATION_RATE() ) 
CHECKDATA_4 = "0xa15f30ac"
STRATEGYY_OFFSET_4 = 0

CONTRACT_ADDRESS_5 = RESERVE_INTEREST_RATE_STRATEGY
## 0x0bdf953f (selector from stableRateSlope1() ) 
CHECKDATA_5 = "0x0bdf953f"
STRATEGYY_OFFSET_5 = 0

CONTRACT_ADDRESS_6 = RESERVE_INTEREST_RATE_STRATEGY
## 0xccab01a3 (selector from stableRateSlope2() ) 
CHECKDATA_6 = "0xccab01a3"
STRATEGYY_OFFSET_6 = 0

CONTRACT_ADDRESS_7 = RESERVE_INTEREST_RATE_STRATEGY
## 0x7b832f58 (selector from variableRateSlope1() ) 
CHECKDATA_7 = "0x7b832f58"
STRATEGYY_OFFSET_7 = 0

CONTRACT_ADDRESS_8 = RESERVE_INTEREST_RATE_STRATEGY
## 0x65614f81 (selector from variableRateSlope2() ) 
CHECKDATA_8 = "0x65614f81"
STRATEGYY_OFFSET_8 = 0

CONTRACT_ADDRESS_9 = RESERVE_INTEREST_RATE_STRATEGY
## 0xb2589544 (selector from baseVariableBorrowRate() ) 
CHECKDATA_9 = "0xb2589544"
STRATEGYY_OFFSET_9 = 0


# concerned strategy address
STRATEGY_ADDRESS= "0x76aFA2b6C29E1B277A3BB1CD320b2756c1674c91" 

MAX_STRATEGY_DEBT_RATIO = 10000

# contracts to get data from
STRATEGY_CONTRACTS = [CONTRACT_ADDRESS_0, CONTRACT_ADDRESS_1, CONTRACT_ADDRESS_2, CONTRACT_ADDRESS_3, CONTRACT_ADDRESS_4, CONTRACT_ADDRESS_5, CONTRACT_ADDRESS_6, CONTRACT_ADDRESS_7, CONTRACT_ADDRESS_8, CONTRACT_ADDRESS_9]

# checkdata (selector + neccessary args bytes32)
STRATEGYY_CHECKDATA = [CHECKDATA_0, CHECKDATA_1, CHECKDATA_2, CHECKDATA_3, CHECKDATA_4, CHECKDATA_5, CHECKDATA_6, CHECKDATA_7, CHECKDATA_8, CHECKDATA_9]

# offset, which args we need from the data received from the call, 0 by default
STRATEGYY_OFFSET = [STRATEGYY_OFFSET_0, STRATEGYY_OFFSET_1, STRATEGYY_OFFSET_2, STRATEGYY_OFFSET_3, STRATEGYY_OFFSET_4, STRATEGYY_OFFSET_5, STRATEGYY_OFFSET_6, STRATEGYY_OFFSET_7, STRATEGYY_OFFSET_8, STRATEGYY_OFFSET_9]

# calculation (logic described in the readme)
STRATEGYY_CALCULATION = []


# ////////////////Supply rate = Ut * (SBt*St + VBt*Vt) * (1 - Rt)

# ////////CASE Ut > Uo
# calcul availableLiq + stable debt
# Step0 = 1, 2, 0

# calcul totalLiq : Step0 + var_debt 
# Step1= 10000, 3, 0

# calcul availableLiq x Precison (10^9)
# Step2 = 1, 1000020000, 2

# calcul Ut(10^9) :  Step2 / Step1       Ut(10^9) step 3
# Step3 = 10002, 10001, 3


# calcul Ut - Uo
# Step4 = 10003, 4, 1

# calcul  1 - Uo
# Step5 = 1000020000, 4, 1            

# calcul (Ut - Uo) x Precision
# Step6 = 10004, 1000020000, 2

# calcul (Ut - Uo)(10^9) / (1 - Uo)
# step7 = 10006, 10005, 3                           (Ut - Uo)(10^9) / (1 - Uo) Step 7


#  average stable rate St= R0 + R1s + (Ut - Uo)/ (1 - Uo)R2s

# calcul R2s * step7 * (10^9)
# Step8 = 10007, 6, 2

# calcul R2s * (Ut - Uo)/ (1 - Uo)
# Step9 = 10008, 1000020000, 3


# calcul R2s * (Ut - Uo)/ (1 - Uo) + R1s
# Step10 = 10009, 5, 0

# calcul R2s * (Ut - Uo)/ (1 - Uo) + R1s + R0
# Step11 = 10010, 9, 0                                            St= R0 + R1s + (Ut - Uo)/ (1 - Uo)R2s   Step 11

# calcul total borrowed : stable debt + var debt
# Step12 = 2, 3, 0                                                total borrowed Step 12

# calcul stable_debt * Precision
# Step13 = 2, 1000020000, 2

# calcul SBt(10^9) =  stable_debt * Precision / total borrowed
# Step14 = 10013, 10012, 3                                                SBt(10^9) step 14

# calcul SBt * St (10^9) =  Step 11 * step 14
# Step15 = 10011, 10014, 2

# calcul SBt * St =  Step 15/ precision
# Step16 = 10015, 1000020000, 3                                       SBt * St  Step 16
    
#  average variable rate Vt= R0 + R1v + (Ut - Uo)/ (1 - Uo)R2v

# calcul R2v * step7 * (10^9)
# Step17 = 10007, 8, 2

# calcul R2v * (Ut - Uo)/ (1 - Uo)
# Step18 = 10017, 1000020000, 3

# calcul R2v * (Ut - Uo)/ (1 - Uo) + R1v
# Step19 = 10018, 7, 0

# calcul R2v * (Ut - Uo)/ (1 - Uo) + R1v + R0
# Step20 = 10019, 9, 0                                            Vt= R0 + R1v + (Ut - Uo)/ (1 - Uo)R2v   Step 20


# calcul variable_debt * Precision
# Step21 = 3, 1000020000, 2

# calcul VBt(10^9) =  variable_debt * Precision / total borrowed
# Ste22 = 10021, 10012, 3                                                VBt(10^9) step 22


# calcul Vt * VBt (10^9) =  Step 20 * step 22
# Step23 = 10020, 10022, 2

# calcul Vt * VBt =  Step23/ precision
# Step24 = 10023, 1000020000, 3                                       VBt * Vt  Step 24
    
# calcul (SBt * St) + (Vt * VBt) =  Step23/ precision
# Step25 = 10016, 10024, 0                                                (SBt * St) + (VBt * Vt) Step 25

# !! Reserve factor /10000 = reserve factor !! 
# calcul (1 - Rt)(10^4)  : 10000 - Rt
# Step26 = 30000, 0, 1     

# calcul  (SBt * St) + (VBt * Vt) * (1 - Rt)(10^4)  : Step 25 *  Step 26
# Step27 = 10025, 10026, 2    

# calcul  (SBt * St) + (VBt * Vt) * (1 - Rt)  : Step 27 / precision
# Step28 = 10027, 30000, 3  

# calcul  (SBt * St) + (VBt * Vt) * (1 - Rt) * Ut(10^9): Step28 * Step3
# Step29 = 10028, 10003, 2    

# calcul  (SBt * St) + (VBt * Vt) * (1 - Rt) * Ut: Step29 / precision(10^9)
# Step30 = 10029, 1000020000, 3                                                   🧪🧪🧪 conditon NOT OK Supply rate STEP 30 🧪🧪🧪 (31 Length )

# [1, 2, 0, 10000, 3, 0, 1, 1000020000, 2, 10002, 10001, 3, 10003, 4, 1, 1000020000, 4, 1, 10004, 1000020000, 2, 10006, 10005, 3, 10007, 6, 2, 10008, 1000020000, 3,
# 10009, 5, 0, 10010, 9, 0, 2, 3, 0, 2, 1000020000, 2, 10013, 10012, 3, 10011, 10014, 2, 10015, 1000020000, 3, 10007, 8, 2, 10017, 1000020000, 3, 10018, 7, 0, 10019, 9, 0,
# 3, 1000020000, 2, 10021, 10012, 3, 10020, 10022, 2, 10023, 1000020000, 3, 10016, 10024, 0, 30000, 0, 1, 10025, 10026, 2, 10027, 30000, 3, 10028, 10003, 2, 10029, 1000020000, 3]


# ////////CASE Ut <= Uo
# calcul availableLiq + stable debt
# Step0 = 1, 2, 0

# calcul totalLiq : Step0 + var_debt 
# Step1= 10000, 3, 0

# calcul availableLiq x Precison (10^9)
# Step2 = 1, 1000020000, 2

# calcul Ut(10^9) :  Step2 / Step1       Ut(10^9) step 3
# Step3 = 10002, 10001, 3

# calcul Ut x Precison (10^9)
# Step4 = 10003, 1000020000, 2

# calcul Ut/Uo
# Step5 = 10004, 4, 3              Ut(10^9)/Uo step 5


#  average stable rate St = R0 + (Ut/Uo)* R1s
# calcul (Ut(10^9)/Uo)* R1s 
# Step6 = 10005, 5, 2

# calcul (Ut/Uo)* R1s
# Step7 = 10006, 1000020000, 3

# calcul St = R0 + (Ut/Uo)* R1s          
# Step8 = 10007, 9, 0                                      St step 8

# calcul stable debt + var debt                            total debt step 9
# Step9 = 2, 3, 0



# calcul stable x Precison (10^9)
# Step10 = 2, 1000020000, 2

# calcul SBt(10^9) : stable_debt(10^9)/ Step9      
# Step11 = 10010, 10009, 3                                  SBt(10^9) step 11

# calcul SBt(10^9) * St : step11 * step8    
# Step12 = 10011, 10009, 2   

# calcul SBt * St : step12 / Precision  
# Step13 = 10012, 1000020000, 3                           SBt * St Step 13   

# average variable rate Vt = R0 + (Ut/Uo)* R1v
# calcul (Ut(10^9)/Uo)* R1v
# Step14 = 10005, 7, 2

# calcul (Ut/Uo)* R1v
# Step15 = 10014, 1000020000, 3

# calcul Vt = R0 + (Ut/Uo)* R1v
# Step16 = 10015, 9, 0                                     Vt STEP 16

# calcul variable_debt x Precison (10^9)
# Step17 = 3, 1000020000, 2

# calcul variable_debt(10^9) / Step 9
# Step18 = 10017, 10009, 3                                VBt(10^9) step 18

# calcul VBt(10^9) * Vt : step16 * Step18   
# Step19 = 10016, 10018, 2   

# calcul VBt * Vt : step19 / Precision   
# Step20 = 10019, 1000020000, 3                           VBt * Vt Step 20 


# calcul (SBt * St) + (VBt * Vt)  : step13 + step20
# Step21 = 10013, 10020, 0                                (SBt * St) + (VBt * Vt) Step 21 


# !! Reserve factor /10000 = reserve factor !! 
# calcul (1 - Rt)(10^4)  : 10000 - Rt
# Step22 = 30000, 0, 1     

# calcul  (SBt * St) + (VBt * Vt) * (1 - Rt)(10^4)  : Step 21 *  Step22
# Step23 = 10021, 10022, 2     

# calcul  (SBt * St) + (VBt * Vt) * (1 - Rt)  : Step 23 / precision(10^4)
# Step24 = 10023, 30000, 3                                                    (SBt * St) + (VBt * Vt) * (1 - Rt) step24

# calcul  (SBt * St) + (VBt * Vt) * (1 - Rt) * Ut(10^9): Step24 * Step3
# Step25 = 10024, 10003, 2    

# calcul  (SBt * St) + (VBt * Vt) * (1 - Rt) * Ut: Step25 / precision(10^9)
# Step26 = 10025, 1000020000, 3                                                   🧪🧪🧪 conditon OK Supply rate STEP 26 🧪🧪🧪 (27 Length )

# [1, 2, 0, 10000, 3, 0, 1, 1000020000, 2, 10002, 10001, 3, 10003, 1000020000, 2, 10004, 4, 3, 10005, 5, 2, 10006, 1000020000, 3, 10007, 9, 0, 2, 3, 0, 2, 1000020000, 2,
# 10010, 10009, 3, 10011, 10009, 2, 10012, 1000020000, 3, 10005, 7, 2, 10014, 1000020000, 3, 10015, 9, 0, 3, 1000020000, 2, 10017, 10009, 3, 10016, 10018, 2, 10019, 1000020000, 3,
# 10013, 10020, 0, 30000, 0, 1, 10021, 10022, 2, 10023, 30000, 3, 10024, 10003, 2, 10025, 1000020000, 3]


# Total Length (31 + 27 = 58) + NOT OK Solution + OK Solution

STRATEGYY_CALCULATION = [58, 1, 2, 0, 10000, 3, 0, 1, 1000020000, 2, 10002, 10001, 3, 10003, 4, 1, 1000020000, 4, 1, 10004, 1000020000, 2, 10006, 10005, 3, 10007, 6, 2, 10008, 1000020000, 3,
10009, 5, 0, 10010, 9, 0, 2, 3, 0, 2, 1000020000, 2, 10013, 10012, 3, 10011, 10014, 2, 10015, 1000020000, 3, 10007, 8, 2, 10017, 1000020000, 3, 10018, 7, 0, 10019, 9, 0,
3, 1000020000, 2, 10021, 10012, 3, 10020, 10022, 2, 10023, 1000020000, 3, 10016, 10024, 0, 30000, 0, 1, 10025, 10026, 2, 10027, 30000, 3, 10028, 10003, 2, 10029, 1000020000, 3, 
1, 2, 0, 10000, 3, 0, 10001, 1000020000, 2, 10002, 10001, 3, 10003, 1000020000, 2, 10004, 4, 3, 10005, 5, 2, 10006, 1000020000, 3, 10007, 9, 0, 2, 3, 0, 2, 1000020000, 2,
10010, 10009, 3, 10011, 10009, 2, 10012, 1000020000, 3, 10005, 7, 2, 10014, 1000020000, 3, 10015, 9, 0, 3, 1000020000, 2, 10017, 10009, 3, 10016, 10018, 2, 10019, 1000020000, 3,
10013, 10020, 0, 30000, 0, 1, 10021, 10022, 2, 10023, 30000, 3, 10024, 10003, 2, 10025, 1000020000, 3]

# Condition : if Ut <= Uo : jump 31
# calcul availableLiq + stable debt
# Step0 = 1, 2, 0

# calcul totalLiq : Step0 + var_debt 
# Step1= 10000, 3, 0

# calcul availableLiq x Precison (10^9)
# Step2 = 1, 1000020000, 2

# calcul Ut(10^9) :  Step2 / Step1       Ut(10^9) step 3
# Step3 = 10002, 10001, 3

# Final: if step3 (Ut) <= stratData 4 (Uo) : go index 31 and 27 length
# FinalStep = 10003, 4, 31, 27

# Total Length (without finalStep): 3 + steps + final step
CALCULATION_CONDITION = [3, 1, 2, 0, 10000, 3, 0, 1, 1000020000, 2, 10003, 4, 31, 27]


def main():
    acct = accounts.load('sa')
    DebtAllocator[0].addStrategy.call(STRATEGY_ADDRESS, MAX_STRATEGY_DEBT_RATIO, STRATEGY_CONTRACTS, STRATEGYY_CHECKDATA, STRATEGYY_OFFSET, STRATEGYY_CALCULATION, CALCULATION_CONDITION,{'from': acct})
