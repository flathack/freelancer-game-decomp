# INI legacy numeric and Vector access

Original value_num at VA 0x06263330 is a direct jump to get_value_float despite
its double declaration; it does not narrow ST0. Reconstructed forwarding retains
the already verified x87 return path. Original get_vector at VA 0x062632e0 accepts
a hidden output pointer as its stack argument, returns that pointer in EAX, and
reads indices 0, 1, 2, each rounded to binary32 before the next call. All three
output stores occur after the three conversions. The explicit ABI entry and
volatile local floats preserve that behavior without inventing Vector class
methods or unrelated layout.

1,178 value_num cases compare complete 80-bit return values and diagnostics.
1,153 Vector cases compare all 12 output bytes plus untouched guards, hidden
return pointer, diagnostic sequences, every bool byte, integer/float edge bits,
string conversions, unknown tags, missing parameters and text parsing. Four
injected extended atof returns straddle binary32 rounding boundaries. External
atof/formatters/diagnostics remain controlled models. Native CRT/FPU execution,
partially aliased output/reader inputs and exact instruction matching remain
unverified.
