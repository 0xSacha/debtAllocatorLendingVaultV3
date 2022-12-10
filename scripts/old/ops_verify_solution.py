import click 
from ape import accounts, project
import json
from starkware.cairo.lang.vm.cairo_pie import CairoPie
from starkware.cairo.lang.vm.relocatable import MaybeRelocatable, RelocatableValue

def get_program_output(cairo_pie):
    """
    Returns the program output.
    """
    assert "output" in cairo_pie.metadata.builtin_segments, "The output builtin must be used."
    output = cairo_pie.metadata.builtin_segments["output"]

    def verify_int(x: MaybeRelocatable) -> int:
        assert isinstance(
            x, int
        ), f"Expected program output to contain absolute values, found: {x}."
        return x

    return [
        verify_int(cairo_pie.memory[RelocatableValue(segment_index=output.index, offset=i)])
        for i in range(output.size)
    ]

def main():
    f = open("./scripts/config.json", "r")
    config_dict = json.load(f)
    f.close()
    account = accounts.load(config_dict["account"])
    contract = project.DebtAllocator.at(config_dict["debt_allocator_address"])

    pie = CairoPie.from_file("./cairoScripts/output/apy_calculator.pie")
    program_output = get_program_output(pie)

    tx = contract.verifySolution(program_output, sender=account)
    logs = list(tx.decode_logs(contract.NewSolution))
    print(logs)
