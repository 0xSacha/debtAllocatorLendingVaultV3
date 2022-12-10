cairo-compile apy_calculator.cairo  --output=apy_calculator_compiled.json
cairo-hash-program --program=apy_calculator_compiled.json
cairo-run --program=apy_calculator_compiled.json --program_input=input/apy_calculator_lender_input.json --print_output --layout=all --cairo_pie_output=output/apy_calculator.pie
cairo-sharp submit --cairo_pie output/apy_calculator.pie
