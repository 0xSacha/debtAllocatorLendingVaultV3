from starkware.cairo.sharp.client_lib import CairoPie, ClientLib
from starkware.cairo.sharp.fact_checker import FactChecker
from starkware.cairo.bootloaders.generate_fact import get_program_output
from starkware.cairo.sharp.sharp_client import SharpClient
from starkware.cairo.lang.compiler.assembler import Program
from typing import List, Optional
import json
import os


# To Set
BIN_DIR = '/Users/sacha/cairo_venv/bin'



RPC= 'https://mainnet.infura.io/v3/eebdf8732cd044f0a52f976af7781260'
CAIRO_PROGRAM_PATH = './test_sharp.cairo'
CAIRO_PROGRAM_INPUT_PATH = './test_sharp_input.json'



def init_client(bin_dir: str, node_rpc_url: Optional[str] = None) -> SharpClient:
    """
    Initialized a SharpClient instance, with or without node access.
    """
    # Load configuration file.
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
    with open(CONFIG_PATH, "r") as config_file:
        config = json.load(config_file)

    # Get Cairo toolchain executable paths.
    CAIRO_COMPILE_EXE = os.path.join(os.path.join(bin_dir, "cairo-compile"))
    CAIRO_RUN_EXE = os.path.join(os.path.join(bin_dir, "cairo-run"))

    # Initialize the SharpClient.
    client = SharpClient(
        service_client=ClientLib(config["prover_url"]),
        contract_client=FactChecker(
            fact_registry_address=config["verifier_address"],
            node_rpc_url=node_rpc_url if node_rpc_url is not None else "",
        ),
        steps_limit=config["steps_limit"],
        cairo_compiler_path=CAIRO_COMPILE_EXE,
        cairo_run_path=CAIRO_RUN_EXE,
    )

    return client


client = init_client(BIN_DIR, [RPC])
compiled_program = client.compile_cairo(CAIRO_PROGRAM_PATH)
cairo_pie = client.run_program(compiled_program, CAIRO_PROGRAM_INPUT_PATH)
print(f"Program output : {get_program_output(cairo_pie)}")
print(f"Submitting to sharp")
fact = client.get_fact(cairo_pie)
job_key = client.submit_cairo_pie(cairo_pie=cairo_pie)
print(f"Job key: {job_key}")
print(f"Fact: {fact}")

