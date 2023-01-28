from .sharp.client_lib import ClientLib
from .sharp.sharp_client import SharpClient
import os, json, time
from dotenv import load_dotenv
from starkware.cairo.bootloaders.generate_fact import get_program_output
from typing import Optional
from starkware.cairo.sharp.fact_checker import FactChecker

from ape import accounts, project

def _load_config(config_file):
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), config_file)
    with open(CONFIG_PATH, "r") as file:
        config = json.load(file)
    return config


def main():
    load_dotenv()
    config = _load_config("config_mainnet.json")

    #### START CLIENT ####
    client = init_client(os.environ["BIN_PATH"], [os.environ["NODE_RPC_URL"]])

    #### RUN THE CAIRO PROGRAM ####
    compiled_program = client.compile_cairo(config["cairo_program_path"])
    cairo_pie = client.run_program(compiled_program, config["cairo_program_input_path"])
    cairo_pie.to_file(config["cairo_program_output_path"])
    program_output = get_program_output(cairo_pie)

    #### SUBMIT FOR VERIFICATION ####
    print("PROGRAM OUTPUT")
    print(program_output)
    print(program_output[-1] / 1e16, "% vs.", program_output[-2] / 1e16, "%")

    job_key = client.submit_cairo_pie(cairo_pie=cairo_pie)
    fact = client.get_fact(cairo_pie)

    print("Job Key:", job_key)
    print("Fact:", fact)

    mins = 0
    print("Waiting for Job to be processed. This can take several minutes (> 15 min)")
    debt_allocator = project.DebtAllocator.at(config["debt_allocator_address"])
    verifier = project.MockVerifier.at(debt_allocator.cairoVerifier())
    while True:
        if verifier.isValid(fact):
            print("Job has been processed!")
            break
        print(mins, "minutes passed")
        mins += 1
        time.sleep(60)
        print("Job is still pending... sleeping for 60 secs")


def init_client(bin_dir: str, node_rpc_url: Optional[str] = None) -> SharpClient:
    """
    Initialized a SharpClient instance, with or without node access.
    """
    # Load configuration file.
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_mainnet.json")
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
