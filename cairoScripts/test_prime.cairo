// The program produces outputs which require the `output` builtin.
%builtins output

from starkware.cairo.common.serialize import serialize_word

func main{output_ptr: felt*}() {
    alloc_locals;

    local prime_1;
    local prime_2;
    let expected = 15;

    // Read the Prime factors from the input and store them in local variables.
    %{
        ids.prime_1 = program_input["prime_1"]
        ids.prime_2 = program_input["prime_2"]
    %}

    // Compute the potential Prime number.
    let result = prime_1 * prime_2;

    // Throw an error if the Prime factors are invalid.
    assert result = expected;

    // Output Prime factors and Prime number.
    serialize_word(prime_1);
    serialize_word(prime_2);
    serialize_word(expected);

    return ();
}
