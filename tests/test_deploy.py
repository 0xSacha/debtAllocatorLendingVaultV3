from ape import accounts, project

account = accounts.load("sacha")
contract = project.DebtAllocator.deploy(sender=account)