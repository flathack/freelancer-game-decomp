# GoodInfoList lookup on populated indexes

Reconstructed `find_by_id` (VA 0x06271470) and `find_by_archetype` (VA 0x062714d0) read the database object's indexes at offsets 12 and 32. Both perform unsigned lower_bound and return the stored GoodInfo pointer only for an exact key match. This differs in scope from existing global GoodList wrappers: these exports work with a supplied GoodInfoList object.

Validation: 96,000 differential lookups during 8,000 original/reconstructed index insertions across 100 actual constructor sequences. Both indexes are queried after every insertion for the inserted key, its neighbors and boundary keys 0/0x80000000/0xffffffff. Tests compare returns, full guarded database/input/result storage, 16 KiB heap and allocation events. An independent first-insertion mapping verifies expected results in unique and multi mode, including null for absent keys and the earliest duplicate after balancing.

The test payload pointers are addresses rather than loaded goods. Full file parsing, archetype resolution, native heap/CRT, aliased/malformed trees and exact instruction matching remain unverified.
