cairo-compile apy_calculator.cairo  --output=apy_calculator_compiled.json
cairo-run --program=apy_calculator_compiled.json --program_input=input_test_Aave_V2.json --print_output --layout=all --cairo_pie_output=apy_calculator.pie
# cairo-sharp submit --cairo_pie apy_calculator.pie