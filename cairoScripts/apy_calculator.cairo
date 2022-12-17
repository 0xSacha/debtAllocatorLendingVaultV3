%builtins output range_check bitwise 

from starkware.cairo.common.math import unsigned_div_rem
from starkware.cairo.common.math_cmp import is_le
from starkware.cairo.common.serialize import serialize_word, serialize_array
from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.registers import get_label_location
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin
from starkware.cairo.common.memcpy import memcpy
from starkware.cairo.common.uint256 import Uint256
from starkware.cairo.common.keccak import keccak_felts

const SUM = 0;
const SUB = 1;
const MUL = 2;
const DIV = 3; 
const POW = 4;
const ALLOCATION_CHANGE = 5;

func serialize_word_from_pointer{output_ptr: felt*}(word) {
    assert [output_ptr] = [word];
    let output_ptr = output_ptr + 1;
    return ();
}

func perform_calculation{ range_check_ptr }(
        _operand1: felt,
        _operand2: felt,
        _operation: felt,
        _current_allocation: felt,
        _new_allocation: felt,
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

    if(_operation == 3){
        let (result_,_) = unsigned_div_rem(_operand1, _operand2);
        return(result_,);
    } 

    if(_operation == 4){
        let (result_) =  pow(_operand1, _operand2);
        return(result_,);
    } 

    assert _operation = 5;

    if(_operation == 5){
        let is_le_ = is_le(_current_allocation, _new_allocation);
        if(is_le_ == 1){
            let diff_ = _new_allocation - _current_allocation;
            return(_operand1 + diff_,);
        } else {
            let diff_ = _current_allocation - _new_allocation;
            return(_operand1 - diff_,);
        }
    } 

    return(0,);
}


func pow{ range_check_ptr }(base : felt, exp : felt) -> (res: felt){
    if(exp == 0){
        return (1,);
    }
    let (res_) = pow(base=base, exp=exp - 1);
    return (res_ * base,);
}

func is_eq{ range_check_ptr }(op1 : felt, op2 : felt) -> (res: felt){
    if(op1 == op2){
        return(1,);
    } else {
        return(0,);
    }
}

func calcul_score_strategy{ range_check_ptr }(
        _data_strat_len: felt,
        _data_strat: felt*,
        _calcul_strat_len: felt,
        _calcul_strat: felt*,
        _step_len: felt,
        _step: felt*,
        _current_allocation: felt,
        _new_allocation: felt,
    ) -> (
       apy: felt
    ){
    alloc_locals;
    if(_calcul_strat_len  == _step_len){
        return(_step[_step_len - 1],);
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

    let (result_) = perform_calculation(op1_, op2_, _calcul_strat[3 * _step_len + 2], _current_allocation, _new_allocation);
    %{
        print(ids.result_)
    %}
    assert _step[_step_len] = result_;
    return calcul_score_strategy(_data_strat_len, _data_strat, _calcul_strat_len, _calcul_strat, _step_len + 1, _step, _current_allocation, _new_allocation);
}



func prepare_calcul{ range_check_ptr }(
        _data_strat_len: felt,
        _data_strat: felt*,
        _conditions_strat_len: felt,
        _conditions_strat: felt*,
        _step_len: felt,
        _step: felt*,
        _current_allocation: felt,
        _new_allocation: felt,
        _calcul_strat_len: felt,
        _calcul_strat: felt*,
        _to_prepare: felt*,
    ) -> (
       len: felt
    ){
    alloc_locals;
    if(_conditions_strat_len  == 0){
            memcpy(_to_prepare, _calcul_strat, _calcul_strat_len*3);
            return(_calcul_strat_len,);
    }
    
    let is_operand1_input_ = is_le(_conditions_strat[3*_step_len],9999);
    let is_operand2_input_ = is_le(_conditions_strat[3*_step_len + 1],9999);
    let is_operand1_const_ = is_le(_conditions_strat[3*_step_len],19999);
    let is_operand2_const_ = is_le(_conditions_strat[3*_step_len + 1],19999);

    // _conditions_strat[_step_len].operand2 >= 10000 means we are taking operand from previous step better than strategy input 
    // over 20,000 we take a const operand -> op1: 10,000, op2:20004 operation:0 means we want step 0 (10000 - 10000) + 4 (20004 - 20000) 
    local op1_: felt;
    if(is_operand1_input_ == 1 ){
         assert op1_ = _data_strat[_conditions_strat[3*_step_len]];
    } else {
        if(is_operand1_const_ == 1){
            assert op1_ = _step[_conditions_strat[3*_step_len] - 10000];
        } else {
            assert op1_ = _conditions_strat[3*_step_len] - 20000;
        }
    }

    local op2_: felt;
    if(is_operand2_input_ == 1 ){
         assert op2_ = _data_strat[_conditions_strat[3*_step_len + 1]];
    } else {
        if(is_operand2_const_ == 1){
            assert op2_ = _step[_conditions_strat[3*_step_len + 1] - 10000];
        } else {
            assert op2_ = _conditions_strat[3*_step_len + 1] - 20000;
        }
    }
    

    if(_conditions_strat_len == _step_len){
        let is_le_ = is_le(op1_, op2_);
        if(is_le_ == 1){
            memcpy(_to_prepare, _calcul_strat + 3*_conditions_strat[_conditions_strat_len*3 + 2], 3*_conditions_strat[_conditions_strat_len*3 + 3]);
            return(_conditions_strat[_conditions_strat_len*3 + 3],);
        } else {
            memcpy(_to_prepare, _calcul_strat, (_calcul_strat_len - _conditions_strat[_conditions_strat_len*3 + 3])*3 );
            return(_calcul_strat_len - _conditions_strat[_conditions_strat_len*3 + 3],);
        }
    }

    let (result_) = perform_calculation(op1_, op2_, _conditions_strat[3 * _step_len + 2], _current_allocation, _new_allocation);
    assert _step[_step_len] = result_;

    return prepare_calcul(_data_strat_len, _data_strat, _conditions_strat_len, _conditions_strat, _step_len + 1, _step, _current_allocation, _new_allocation, _calcul_strat_len, _calcul_strat, _to_prepare);
}


func run_input{ range_check_ptr }(
        _current_allocation: felt*,
        _new_allocation: felt*,
        _data_strat: felt*,
        _calcul_strat: felt*,
        _condtions_strat: felt*,
        _cumulative_current_score: felt,
        _cumulative_new_score: felt,
        _cumulative_data_strat_array_len: felt,
        _cumulative_data_strat_array: felt*,
        _cumulative_strat_condtions_array_len: felt,
        _cumulative_strat_condtions_array: felt*,
        _cumulative_calculation_strat_array_len: felt,
        _cumulative_calculation_strat_array: felt*,
        tab_len_: felt,
        _strat_amount: felt
    ) -> (
       current_score: felt,
       new_score: felt,
       input_hash: Uint256,
    ){
    alloc_locals;
    if(tab_len_ == _strat_amount){
        memcpy(_cumulative_data_strat_array + _cumulative_data_strat_array_len, _cumulative_calculation_strat_array, _cumulative_calculation_strat_array_len);
        memcpy(_cumulative_data_strat_array + _cumulative_data_strat_array_len + _cumulative_calculation_strat_array_len, _cumulative_strat_condtions_array, _cumulative_strat_condtions_array_len);
        let (input_hash_) = keccak_felts(_cumulative_data_strat_array_len + _cumulative_calculation_strat_array_len + _cumulative_strat_condtions_array_len, _cumulative_data_strat_array);
        return(_cumulative_current_score, _cumulative_new_score, input_hash_);
    }

    let (local calcul_strat_after_condition_: felt*) = alloc();
    let (local condition_step : felt*) = alloc();
    let (calcul_strat_after_condition_len_: felt) = prepare_calcul(
        _data_strat[0],
        _data_strat + 1,
        _condtions_strat[0],
        _condtions_strat + 1,
        0,
        condition_step,
        _current_allocation[0],
        _new_allocation[0],
        _calcul_strat[0],
        _calcul_strat + 1,
        calcul_strat_after_condition_);

    let (local steps : felt*) = alloc();
    let (strategy_apy_) = calcul_score_strategy(
        _data_strat[0],
        _data_strat + 1,
        calcul_strat_after_condition_len_,
        calcul_strat_after_condition_,
        0,
        steps,
        _current_allocation[0],
        _new_allocation[0],);
    
    let current_score_ = strategy_apy_ *  _current_allocation[0];
    let new_score_ = strategy_apy_ *  _new_allocation[0];

    memcpy(_cumulative_data_strat_array + _cumulative_data_strat_array_len, _data_strat + 1,  _data_strat[0]);
    memcpy(_cumulative_calculation_strat_array + _cumulative_calculation_strat_array_len, _calcul_strat + 1,  _calcul_strat[0]*3);
    memcpy(_cumulative_strat_condtions_array + _cumulative_strat_condtions_array_len, _condtions_strat + 1, _condtions_strat[0]*3 + 4);

    return run_input(
        _current_allocation + 1,
        _new_allocation + 1,

        _data_strat + 1 +  _data_strat[0],
        _calcul_strat + 1 + _calcul_strat[0]* 3,
        _condtions_strat + 1 + _condtions_strat[0]*3 + 4,

        _cumulative_current_score + current_score_,
        _cumulative_new_score + new_score_,

        _cumulative_data_strat_array_len + _data_strat[0],
        _cumulative_data_strat_array,
        _cumulative_strat_condtions_array_len + _condtions_strat[0]*3 + 4,
        _cumulative_strat_condtions_array,
        _cumulative_calculation_strat_array_len + _calcul_strat[0]*3,
        _cumulative_calculation_strat_array,
        tab_len_,
        _strat_amount + 1);
}


func main{output_ptr: felt*, range_check_ptr, bitwise_ptr : BitwiseBuiltin*}() {
    alloc_locals;
    let (local current_allocation : felt*) = alloc();
    let (local new_allocation : felt*) = alloc();
    let (local strat_data : felt*) = alloc();
    let (local strat_calculation : felt*) = alloc();
    let (local strat_calculation_conditions : felt*) = alloc();
    tempvar tab_len_;

    %{  
        strategy_amount = len(program_input['current_allocation'])
        ids.tab_len_ = strategy_amount
        current_allocation = ids.current_allocation
        for i, val in enumerate(program_input['current_allocation']):
             memory[current_allocation + i] = val

        new_allocation = ids.new_allocation
        for i, val in enumerate(program_input['new_allocation']):
             memory[new_allocation + i] = val


        strat_data_ref = ids.strat_data
        for i, val in enumerate(program_input['strategies_data']):
            memory[strat_data_ref + i] = val

        strat_calculation_ref = ids.strat_calculation
        for i, val in enumerate(program_input['strategies_calculation']):
            memory[strat_calculation_ref + i] = val

        strat_calculation_conditions_ref = ids.strat_calculation_conditions
        for i, val in enumerate(program_input['strategies_calculation_conditions']):
            memory[strat_calculation_conditions_ref + i] = val

    %}

    let tab_len_ = tab_len_;
    let (vault_total_value_) = sum_array(tab_len_, current_allocation);
    let (local cumulative_data_strat_array : felt*) = alloc();
    let (local cumulative_calculation_strat_array : felt*) = alloc();
    let (local cumulative_condition_strat_array : felt*) = alloc();
    let (current_score_, new_score_, input_hash_) = run_input(current_allocation, new_allocation, strat_data, strat_calculation, strat_calculation_conditions,0, 0, 0, cumulative_data_strat_array, 0, cumulative_calculation_strat_array, 0, cumulative_condition_strat_array, tab_len_, 0);
    let (vault_current_apy_,r) = unsigned_div_rem(current_score_, vault_total_value_);
    let (vault_new_apy_,r) = unsigned_div_rem(new_score_, vault_total_value_);

    //Return the program input and output
    let (callback) = get_label_location(serialize_word_from_pointer);

    serialize_word(input_hash_.high);
    serialize_word(input_hash_.low);
    serialize_array(current_allocation, tab_len_, 1, callback);    
    serialize_array(new_allocation, tab_len_, 1, callback);    
    serialize_word(vault_current_apy_);
    serialize_word(vault_new_apy_);
    return ();
}


func sum_array{ range_check_ptr }(array_len : felt, array: felt*) -> (res: felt){
    if(array_len == 0){
        return (0,);
    }
    let (previous_result_) = sum_array(array_len - 1, array + 1);
    let new_result = array[0] + previous_result_;
    return (new_result,);
}