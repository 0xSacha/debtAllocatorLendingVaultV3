import json
from json import load

from starkware.cairo.bootloaders.hash_program import compute_program_hash_chain
from starkware.cairo.lang.compiler.program import Program
from web3 import Web3


def main():
    # Compile with cairo-compile ./prime_15.cairo --output
    # ./prime_15_compiled.json
    with open("./prime_15_compiled.json", "r") as f:
        program = Program.Schema().load(json.load(f))
        program_hash = compute_program_hash_chain(program)
        print("ProgramHash: " + hex(program_hash))

        # get the output with:
        # cairo-run --program ./prime_15_compiled.json --program_input ./prime_15-input.json --print_output --layout=small
        program_output = [3, 5, 15]

        fact = Web3.solidityKeccak(
            ["uint256", "bytes32"],
            [program_hash, Web3.solidityKeccak(["uint256[]"], [program_output])],
        )

        print("Fact: " + fact.hex())


if __name__ == "__main__":
    main()
