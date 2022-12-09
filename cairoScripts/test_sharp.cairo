%builtins output range_check bitwise 
from starkware.cairo.common.serialize import serialize_word
// from keccak import keccak_felts, finalize_keccak
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin


func check_sum{ range_check_ptr }(_op1: felt, _op2: felt) -> (state: felt){
    alloc_locals;
    let sum_ = _op1 + _op2;
    if(sum_ == 5){
        return(1,);
    } else {
        return(0,);
    }
}


func main{output_ptr: felt*, range_check_ptr, bitwise_ptr : BitwiseBuiltin*}() {
    alloc_locals;
    local operand1:felt;
    local operand2:felt;
    %{  
        ids.operand1 = program_input['operand1']
        ids.operand2 = program_input['operand2']
    %}
    let (result_) = check_sum(operand1, operand2);
    serialize_word(operand1);
    serialize_word(operand2);
    serialize_word(result_);
    return ();
}
