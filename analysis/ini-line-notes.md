# INI_Reader::get_line_ptr

Export at original VA 0x0630fea0. Text mode sprintfs "%s = %s" into
static storage at 0x063fc198. Binary mode with no current entry returns an
empty literal without clearing either line or join buffers. With an entry,
sprintf writes "%s = " into storage at 0x0658d800, the binary parameter
join populates reader offset 0x1464, then a DWORD/tail copy appends that join.
Numeric conversion uses the same shared storage at 0x0658d900 as string getters.

The source reuses reconstructed binary joins. BINI output now occupies the first
256 bytes of a contiguous 512-byte region, with numeric conversion at +256.
COFF symbol aliases preserve both original exported/global identities and this
observed address relationship. Overflow from line output into numeric output is
therefore reproduced, including subsequent unknown-tag reuse of overwritten
numeric contents. The text destination remains a provisional 2048-byte buffer.
Original allocation extents beyond these reconstructed ranges have not been
proven; these extents must not be mistaken for bounds in original code.

2445 differential calls exercise line output and the integrated string getters,
including every byte boolean value, signed integers, float bit patterns,
unknown tags/shared-buffer reuse, random multi-parameter sequences, empty and
missing entries, and text lines up to 2026 output bytes. The test separately
records line call count. Within the tested buffer ranges, complete output-buffer
write footprints, joined reader state, returned storage categories, formatter
arguments and diagnostics agree. 21 additional sequences exercise line/numeric adjacency: long names, numeric
parameters that overwrite an existing line prefix, long string parameters, and
subsequent unknown-tag retrieval. All 512 static bytes agree. Controlled
joined-buffer overflow is also exercised by the underlying getter. Authentic sprintf spelling/locale,
native Windows runtime and exact instruction matching remain unverified.

## Additional text-storage evidence

The next raw common.dll functions (0x06311240, 0x06311250, 0x06311260)
write globals at 0x063fc2a0, 0x063fc29c, and 0x063fc298. The last address is
exactly +0x100 from the text line destination at 0x063fc198. Thus the current
2048-byte text array does not yet reconstruct the original neighboring global
storage, despite passing output-buffer comparisons. Future integration must
recover these neighboring globals and preserve their alias/overflow effects;
long-line comparisons alone cannot establish fidelity for those consumers.
