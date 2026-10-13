# EquipDescVector add / Cargo merging

Original export VA 0x06309f50. Non-combine appends an Equipment field copy;
full capacity grows by max(current_size,1), constructs existing entries and new
entry, then frees the old buffer. With spare capacity only the newly appended
entry fields are written; Equipment padding remains untouched.

Combine first finds the first matching archetype. Temporary raw byte, owner and
case-insensitive hardpoint must match. A mismatch restarts from begin in original
assembly (0x06309fa9/0x06309fb1/0x06309fc2 branch to 0x06309f70), not from the next
entry. This creates a stable nonreturning path for fixed incompatible inputs;
that behavior is preserved, not silently repaired. No matching archetype appends.

Matching entries add count words modulo 32 bits. Old status below 1 and incoming
status not below 1 adds count without changing old status. When both are below 1,
their sum is compared before binary32 rounding: sums >=1 subtract 1 and keep the
summed count, otherwise count is reduced by one. Old status not below 1 replaces
status with incoming status through x87-compatible narrowing (including signaling
NaN quieting). The existing double intermediate retains exact sums of tested
binary32 inputs; native FPU/rounding-mode variants remain unverified.

908 differential cases pass: vector growth/reuse, append and combine, count
wraparound, signed zeros, fractions around 1, NaNs/infinities and three fixed
mismatch paths reaching 50,000 instructions in both binaries. Complete vector
bytes, complete 64KiB modeled heap and allocation/free events agree. Nonreturning
classification is supported by assembly restart logic and bounded emulation;
it is not native process execution. Input/vector storage aliasing, full loader
integration, native CRT/heap and byte matching remain open.
