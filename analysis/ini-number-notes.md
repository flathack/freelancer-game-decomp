# INI_Reader::is_number

Original export at VA 0x06311110. This is an independent lexical predicate,
not ParseNumber or a successful conversion check. The reader object is unused.

The function consumes an optional sign and optional leading dot. A quoted
alphabetic character immediately returns true even with trailing bytes. If a
quote does not qualify, validation continues at the following character rather
than rejecting the quote. Hexadecimal syntax accepts 0x with no digits, and a
leading dot may precede 0x. Decimal syntax requires an initial digit, allows one
dot anywhere afterward, one exponent marker, and one subsequent sign anywhere
after that exponent (not necessarily immediately after it). It does not require
exponent digits and accepts 1e, 1e+, 1e2+, and 1e.2. Whitespace is not skipped.

10,716 differential calls cover all short combinations of syntax characters,
all nonzero single-byte values in four contexts, 5,000 randomized strings and
explicit legacy edge cases. Exact return bytes and signed tolower argument
sequences agree. Complete reader state remains unchanged. The controlled
ASCII tolower model does not verify native locale behavior. Null/malformed
pointers and exact machine-code matching remain unverified.
