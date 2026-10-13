# EquipDescVector append

Original export VA 0x06309a80 first reserves exactly old_size+source_size when
capacity is insufficient. Existing Equipment entries are field-constructed in
new storage, preserving untouched descriptor padding, then the old buffer is
freed. It walks source entries and appends one at a time, re-reading source.end
after every append; reconstruction reuses the verified non-combine add path.
Destination allocator bytes and the distinct source vector stay unchanged.

432 returning comparisons cover destination/source sizes 0..11 and exact/spare
capacity combinations. Entire vector objects, entire 64KiB modeled heap and exact
allocation/free events agree. Three additional nonempty self-append cases reach
2000 instructions in both binaries. Their evolving memory is not compared at
that budget because instruction counts differ; only bounded non-return is checked.
Assembly/source live-bound logic supports the retained self-extension behavior.
This is not a claim of equivalent native faults or arbitrarily long self-append.
The 908 add/merge regression cases also pass after header changes.

Partial storage aliasing, full loader integration, allocation failures, native
CRT/heap and exact instruction matching remain open.
