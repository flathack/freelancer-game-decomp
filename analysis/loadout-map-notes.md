# Loadout::Map ownership

Observed x86 Map extent: 24 bytes. ID word at 0, vector allocator bytes at 4,
begin/end/capacity at 8/12/16, EquipIdMaker word at 20, final padding at 22.
Reconstructed exports: copy constructor (0x0626c510), assignment (0x0626c5c0),
destructor (0x06273100). Default construction remains open because the original
writes an indeterminate vector allocator byte from stack storage.

Copy construction allocates exactly size*32, including a zero-size allocation,
and field-copies EquipDesc without its padding bytes. Assignment retains the
destination allocator, reuses existing capacity when possible, copies existing
entries as all 32 bytes, and field-constructs only newly grown entries. Insufficient
capacity frees the previous buffer before allocating exactly the new size.
Self-assignment preserves the list. Equipment counter is copied as a word.
Destructor frees begin even when null and clears all three vector pointers.
Volatile pointer stores retain those observable post-destruction writes, which
Clang otherwise removes as dead stores at optimization level O2.

512 differential cases cover lengths 0..7, varying target size/capacity, growth,
shrink, reuse/reallocation, copy construction, self-assignment and destruction.
Object bytes, entire guarded modeled heap, allocation/free events and constructor/
assignment return pointers agree. No descriptor padding is normalized or excluded.
Native heap, allocator failure, exception unwinding, partial object overlap,
default construction, complete Loadout tree integration and exact matching remain
unverified. This change does not reconstruct complete Loadout list loading.
