cairo-compile test_sharp.cairo  --output=test_sharp_compiled.json
cairo-run --program=test_sharp_compiled.json --program_input=test_sharp_input.json --print_output --layout=all --cairo_pie_output=test_sharp.pie
# cairo-sharp submit --cairo_pie apy_calculator.pie