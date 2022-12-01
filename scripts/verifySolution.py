import click 
from ape import accounts, project

PROGRAM_OUTPUT= [69877331423220707281243982024735471462, 198902898170385006158168479911819002343, 2, 0, 0, 2, 5000, 5000, 0, 1510489860937415003303867]

def main():
    account = accounts.load("sach")
    contract = project.DebtAllocator.at("0xDcAA40F17cEce7c7aB9c37E6e54754aA6985DEe1")
    tx = contract.verifySolution(PROGRAM_OUTPUT, sender=account)
    logs = list(tx.decode_logs(contract.NewSolution))
    print(logs)
    
