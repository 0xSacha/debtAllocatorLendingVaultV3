export WEB3_INFURA_PROJECT_ID=eebdf8732cd044f0a52f976af7781260      
ape run ops_save_snapshot --network ethereum:goerli:infura 

cairo-compile ../cairoScripts/apy_calculator.cairo  --output=../cairoScripts/apy_calculator_compiled.json

cairo-hash-program --program=../cairoScripts/apy_calculator_compiled.json

cairo-run --program=../cairoScripts/apy_calculator_compiled.json --program_input=../cairoScripts/input/apy_calculator_lender_input.json --print_output --layout=all --cairo_pie_output=../cairoScripts/output/apy_calculator.pie

cairo-sharp submit --cairo_pie ../cairoScripts/output/apy_calculator.pie

echo "Please update the variable PROGRAM_OUTPUT in ops_verify_solution.py script. Then, press enter to continue"
read cont

ape run ops_verify_solution --network ethereum:goerli:infura
