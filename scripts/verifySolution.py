import click 
from ape import accounts, project

PROGRAM_OUTPUT= [273822300930268542190909985240014354946, 289686421479239889190470738038045525506, 2, 0, 0, 2, 5000, 5000, 0, 5149393346585344287115867]

def main():
    account = accounts.load("sach")
    contract = project.DebtAllocator.at("0x8aD42486109e5Ec080eFe015830d2c9B806631d0")
    tx = contract.verifySolution(PROGRAM_OUTPUT, sender=account)
    logs = list(tx.decode_logs(contract.NewSolution))
    print(logs)
    
