# INI_Reader default constructor

Original export at VA 0x0630f6f0. Reconstructed source invokes the two FileMap
constructors, initializes the text line counter/header first byte, clears binary
header/string-table/block/value pointers, and selects text mode. Original opaque
allocator first bytes at offsets 0 and 0x1428 come from the high byte of ECX (the
object address); the remaining allocator bytes are untouched. value_index,
parameters, remaining text buffers and unknown regions are not initialized.

72 differential calls compare full 0x1568-byte object footprints and constructor
return ABI at four address regions, six alignments/offsets, and zero/pattern/random
prior storage. These include high-address and intentionally unaligned objects.
The imported text string _Tidy(false) is modeled as clearing its three string
fields, matching the observed dependency. Native MSVCP60 and exception unwinding
are not verified, nor is instruction-byte matching.
