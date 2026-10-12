# INI_Reader::get_line_ptr

Export at original VA 0x0630fea0. Text mode sprintfs "%s = %s" into
static storage at 0x063fc198. Binary mode with no current entry returns an
empty literal without clearing either line or join buffers. With an entry,
sprintf writes "%s = " into storage at 0x0658d800, the binary parameter
join populates reader offset 0x1464, then a DWORD/tail copy appends that join.
Numeric conversion uses the same shared storage at 0x0658d900 as string getters.

The source reuses reconstructed binary joins and retains separate static line
outputs. The provisional buffers are 2048 text bytes and 256 binary bytes.
Original allocation extents have not been proven. Original binary output is
adjacent to the numeric shared buffer; rebuilt overflow adjacency is not yet
reconstructed. Arbitrarily oversized lines therefore remain unverified, and
these provisional extents must not be mistaken for bounds in original code.

2403 differential calls exercise line output and the integrated string getters,
including every byte boolean value, signed integers, float bit patterns,
unknown tags/shared-buffer reuse, random multi-parameter sequences, empty and
missing entries, and text lines up to 2026 output bytes. The test separately
records line call count. Within the tested buffer ranges, complete output-buffer
write footprints, joined reader state, returned storage categories, formatter
arguments and diagnostics agree. Controlled joined-buffer overflow is exercised
by the underlying getter, not by get_line_ptr. Authentic sprintf spelling/locale,
native Windows runtime and exact instruction matching remain unverified.
