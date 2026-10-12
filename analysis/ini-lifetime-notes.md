# INI reader close and metadata

Reconstructed common.dll exports at 0x0630f800 (close), 0x0630fa00
(get_line_num), and 0x063100d0 (get_file_name). The active mode selects the
FileMap subobject; close does not reset binary_mode, cached BINI pointers,
text buffers, or line_number. Resource ownership behavior is inherited from
FileMap, including freeing memory-backed data and invalid-handle edge cases.

Binary get_line_num emits the original FDUMP warning (severity 0x100002,
Ini.cpp line 0x1f6) and returns zero. Text mode returns the signed 32-bit line
counter. Null filenames use the imported MSVCP60 empty string.

144 differential calls cover both modes, null/non-null filename and data,
invalid/null/non-null file handle, and absent/present mapping handle. The test
compares the complete 0x1568-byte object, filename memory, returned metadata,
resource release order/arguments, and diagnostic content. String growth and
memmove are controlled dependency models; their invocation counts are not
compared. Reader-specific shared COW name paths and native CRT/Win32 execution
remain unverified. No byte-identical matching claim is made.

## Memory open

The export at 0x0630fce0 is reconstructed as well. A temporary FileMap copies
input bytes, then its data ownership transfers into the text FileMap. Successful
calls always switch to text mode, reset line_number and text_header[0], and
preserve all other parser fields, including the binary FileMap. Previously owned
text handles/data are overwritten without release, as in the original. Null input
or zero length returns false without modifying the reader. An allocation failure
fault/exception remains outside the successful-path comparison.

320 differential calls cover both prior modes, five COW filename states, sixteen
payloads (including BINI, embedded NULs, every byte, word-copy boundaries and
4097 bytes), and null input. Full object bytes, copied payload, filenames,
allocation ownership, reference-count mutations, and release events agree under
the controlled CRT models. This does not establish native CRT fidelity or byte
matching.
