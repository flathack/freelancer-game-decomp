# Goods index insertion

Original emplace helper VA 0x063221d0; unique insertion helper VA 0x06272c50. Reconstructed with 24-byte nodes: links at 0/4/8, unsigned key at 12, GoodInfo pointer at 16, color at 20, nil flag at 21. Shared 16-byte link/key and 20-byte tree-prefix storage declarations are reused from Loadout; color access is specific to Goods nodes.

Emplace walks by unsigned key. Unique mode returns an existing node on duplicate, preserving result padding; multi mode inserts equal keys on the right. New nodes receive the key/pointer pair, nil children and red color. Insertion maintains head extrema and balances by recoloring and rotations. Both helpers return the supplied result storage pointer.

8,000 original/reconstructed emplace comparisons across 100 complete GoodInfoList initialization sequences exercise both indexes, unique mode and noncanonical nonzero multi flags, repeated small keys and full-width keys including zero, 0x80000000 and 0xffffffff. Each insertion compares returned pointer, the complete guarded database/result/input storage, seeded 16 KiB heap and cumulative allocation sequence. The test uses the actual reconstructed constructor rather than hand-built trees.

Allocation failures, overlapping tree/input/result storage, native heap/CRT and instruction matching remain unverified. GoodInfo pointers are test payload addresses; this establishes index mechanics, not Goods file parsing or complete database loading.
