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
