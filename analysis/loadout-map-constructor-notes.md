# Loadout Map default construction

Original export VA 0x0626c4b0 clears the ID, copies an indeterminate allocator
byte from entry ESP-17 into object+4, clears begin/end/capacity, and resets the
Equipment ID maker to 0x21. Other allocator and tail padding bytes remain intact.
The source now declares the default constructor and supplies its decorated ABI
entry, with C++ initialization plus an explicit temporary naked boundary for the
physical stack byte. This avoids inventing a zero allocator value or relying on
undefined uninitialized C++ local reads. ID clearing precedes the stack-byte read,
as in original code; the C++ initializer clears the ID again harmlessly.

1024 differential calls cover all 256 byte values at four aligned/unaligned object
positions. Complete 64-byte guarded object storage and constructor return pointer
agree. The existing 512 copy/assignment/destructor cases pass after the declaration
change. This is still a temporary ABI reconstruction, not exact instruction
matching. Stack/object aliasing, exception unwinding, native execution, native
heap and full Loadout tree/list loading remain unverified.
