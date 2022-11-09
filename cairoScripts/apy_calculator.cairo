%builtins output range_check bitwise 

from starkware.cairo.common.math import unsigned_div_rem, assert_le_felt
from starkware.cairo.common.math_cmp import is_le
from starkware.cairo.common.serialize import serialize_word, serialize_array
from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.registers import get_label_location
// from keccak import keccak_felts, finalize_keccak
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.memcpy import memcpy
from starkware.cairo.common.uint256 import Uint256
from starkware.cairo.common.keccak import keccak_felts

const SUM = 0;
const SUB = 1;
const MUL = 2;
const DIV = 3; 
// const POW = 4;
// const SQUARE = 5;

func serialize_word_from_pointer{output_ptr: felt*}(word) {
    assert [output_ptr] = [word];
    let output_ptr = output_ptr + 1;
    return ();
}


func perform_calculation{ range_check_ptr }(
        _operand1: felt,
        _operand2: felt,
        _operation: felt
    ) -> (
       result: felt
    ){

    if(_operation == 0){
        return(_operand1 + _operand2,);
    }

    if(_operation == 1){
        return(_operand1 - _operand2,);
    }

    if(_operation == 2){
        return(_operand1 * _operand2,);
    }

    assert _operation = 3;

    if(_operation == 3){
        let (result_,_) = unsigned_div_rem(_operand1, _operand2);
        return(result_,);
    } 
    return(0,);
}


func calcul_score_strategy{ range_check_ptr }(
        _debt_ratio: felt,
        _data_strat_len: felt,
        _data_strat: felt*,
        _calcul_strat_len: felt,
        _calcul_strat: felt*,
        _step_len: felt,
        _step: felt*,
    ) -> (
       score: felt
    ){
    alloc_locals;
    if(_calcul_strat_len == _step_len){
        return(_step[_step_len - 1] * _debt_ratio,);
    }
    let is_operand1_input_ = is_le(_calcul_strat[3*_step_len],9999);
    let is_operand2_input_ = is_le(_calcul_strat[3*_step_len + 1],9999);
    let is_operand1_const_ = is_le(_calcul_strat[3*_step_len],19999);
    let is_operand2_const_ = is_le(_calcul_strat[3*_step_len + 1],19999);

    // _calcul_strat[_step_len].operand2 >= 10000 means we are taking operand from previous step better than strategy input 
    // over 20,000 we take a const operand -> op1: 10,000, op2:20004 operation:0 means we want step 0 (10000 - 10000) + 4 (20004 - 20000) 
    local op1_: felt;
    if(is_operand1_input_ == 1 ){
         assert op1_ = _data_strat[_calcul_strat[3*_step_len]];
    } else {
        if(is_operand1_const_ == 1){
            assert op1_ = _step[_calcul_strat[3*_step_len] - 10000];
        } else {
            assert op1_ = _calcul_strat[3*_step_len] - 20000;
        }
    }
    local op2_: felt;
    if(is_operand2_input_ == 1 ){
        assert op2_ = _data_strat[_calcul_strat[3*_step_len + 1]];
    } else {
        if(is_operand2_const_ == 1){
            assert op2_ = _step[_calcul_strat[3*_step_len + 1] - 10000];
        } else {
            assert op2_ = _calcul_strat[3*_step_len + 1] - 20000;
        }
    }
    let (result_) = perform_calculation(op1_, op2_, _calcul_strat[3 * _step_len + 2]);
    assert _step[_step_len] = result_;
    return calcul_score_strategy(_debt_ratio, _data_strat_len, _data_strat, _calcul_strat_len, _calcul_strat, _step_len + 1, _step);
}

func run_input{ range_check_ptr }(
        _debt_ratio: felt*,
        _data_strat: felt*,
        _calcul_strat: felt*,
        _cumulative_score: felt,
        _cumulative_data_strat_array_len: felt,
        _cumulative_data_strat_array: felt*,
        _cumulative_calculation_strat_array_len: felt,
        _cumulative_calculation_strat_array: felt*,
        _cumulative_debt_: felt,
    ) -> (
       final_score: felt,
       input_hash: Uint256,
    ){
    alloc_locals;
    if(_cumulative_debt_ == 10000){
        memcpy(_cumulative_data_strat_array + _cumulative_data_strat_array_len, _cumulative_calculation_strat_array, _cumulative_calculation_strat_array_len);
        let (input_hash_) = keccak_felts(_cumulative_data_strat_array_len + _cumulative_calculation_strat_array_len, _cumulative_data_strat_array);
        return(_cumulative_score, input_hash_,);
    }

    let (local steps : felt*) = alloc();
    let (score_) = calcul_score_strategy(
        _debt_ratio[0],
        _data_strat[0],
        _data_strat + 1,
        _calcul_strat[0],
        _calcul_strat + 1,
        0,
        steps);
    
    let new_cumulative_score_ = _cumulative_score + score_;

    // memcpy(dst: felt*, src: felt*, len)
    memcpy(_cumulative_data_strat_array + _cumulative_data_strat_array_len, _data_strat + 1,  _data_strat[0]);
    memcpy(_cumulative_calculation_strat_array + _cumulative_calculation_strat_array_len, _calcul_strat + 1,  _calcul_strat[0]*3);

    let new_cumulative_debt_ = _cumulative_debt_ + _debt_ratio[0];
    return run_input(
        _debt_ratio + 1,
        _data_strat + 1 +  _data_strat[0],
        _calcul_strat + 1 + _calcul_strat[0]* 3,
        new_cumulative_score_,
        _cumulative_data_strat_array_len + _data_strat[0],
        _cumulative_data_strat_array,
        _cumulative_calculation_strat_array_len + _calcul_strat[0]*3,
        _cumulative_calculation_strat_array,
        new_cumulative_debt_);
}


func main{output_ptr: felt*, range_check_ptr, bitwise_ptr : BitwiseBuiltin*}() {
    alloc_locals;
    tempvar debt_ratio_len: felt;
    let (local debt_ratio : felt*) = alloc();
    let (local strat_data : felt*) = alloc();
    let (local strat_calculation : felt*) = alloc();

    // Completing tab from input and assert totaldebt ration = 1
    %{  
        sum_debt_ratio = 0 
        for i, val in enumerate(program_input['debt_ratio']):
            sum_debt_ratio = sum_debt_ratio + val
        assert sum_debt_ratio == 10000

        ids.debt_ratio_len = len(program_input['debt_ratio'])
            
        debt_ratio = ids.debt_ratio
        for i, val in enumerate(program_input['debt_ratio']):
             memory[debt_ratio + i] = val


        strat_data_ref = ids.strat_data
        for i, val in enumerate(program_input['strategies_data']):
            memory[strat_data_ref + i] = val

        strat_calculation_ref = ids.strat_calculation
        for i, val in enumerate(program_input['strategies_calculation']):
            memory[strat_calculation_ref + i] = val
    %}


    let (local cumulative_data_strat_array : felt*) = alloc();
    let (local cumulative_calculation_strat_array : felt*) = alloc();
    let (final_score_, input_hash_) = run_input(debt_ratio, strat_data, strat_calculation, 0, 0, cumulative_data_strat_array, 0, cumulative_calculation_strat_array, 0);
    let (vault_apy_,r) = unsigned_div_rem(final_score_, 10000);

    //Return the program input and output
    let (callback) = get_label_location(serialize_word_from_pointer);

    serialize_word(input_hash_.high);
    serialize_word(input_hash_.low);
    serialize_array(debt_ratio, 2, 1, callback);    
    serialize_word(vault_apy_);
    return ();
}
