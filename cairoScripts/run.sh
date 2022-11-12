cairo-compile apy_calculator.cairo  --output=apy_calculator_compiled.json
cairo-run --program=apy_calculator_compiled.json --program_input=apy_calculator_input.json --print_output --layout=all --cairo_pie_output=apy_calculator.pie
cairo-sharp submit --cairo_pie apy_calculator.pie