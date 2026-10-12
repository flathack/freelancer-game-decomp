# INI reader destructor

Original export VA 0x062636e0. Destroys both file subobjects regardless of mode,
binary first and text second. Resources and filename storage are released, and
FileMap pointer/length/capacity/position fields cleared. Parser buffers, mode,
line counter and cached binary pointers are not reset. Reconstructed C++ member
destruction uses the verified FileMap destructor for both subobjects.

50 differential calls compare the full object bytes, allocation ownership and
resource/string release ordering with two modes, five COW filename states,
memory/file/mapping ownership and invalid/null handles. CRT helpers are modeled;
external string helper invocation counts are not compared. Original binary string
erase uses the modeled COW split then clear path, while reconstructed FileMap
uses its previously verified detach/assignment path. Resulting heap ownership,
reference counts and release events agree in these cases. Native CRT, exception
unwinding, malformed resource ownership and exact machine-code matching remain
unverified. Synthetic aliased data fields compare release sequences only and do
not establish that such double ownership is safe under a native heap.
