# INI reader copy construction and assignment

Original exports VA 0x06263370 and 0x062634d0. FileMap resource handles/data and
BINI parser pointers are copied directly; neither operation creates independent
file data or relocates BINI pointers. Filename storage follows legacy MSVCP60
COW sharing/detach rules. Copy construction copies each allocator first byte;
assignment preserves the destination allocator. Other allocator bytes, binary
value-index padding and final object padding are untouched. All four text buffers
and the 256-byte joined-value buffer are copied. Original constructor buffer
copies operate in DWORD units; assignment copies byte text/join buffers and
16-bit wide-text buffer units.

36 differential cases cover construction, assignment, self-assignment, both modes,
and null/ordinary/shared/saturated/unshareable filename references. Full source
and target bytes, full used modeled heap, ownership map and release events agree.
Shallow data ownership is intentional original behavior; destructor safety after
copying was not established. Arbitrary partially overlapping objects, native CRT,
exception unwinding and helper call counts are not covered. Reconstructed C++
member initialization copies the two FileMaps before parser buffers, whereas
original construction copies text parser buffers between the two filename copies;
these orders agree for tested distinct objects, but alias-heavy inputs need more
work. This is behavioral reconstruction, not exact instruction matching.

INI_Reader is now declared as class with public members, matching original MSVC
class mangling for reference-taking constructor and assignment symbols. Layout
and field offsets remain enforced by the existing static assertions.
