# Loadout insert selection and duplicates

Internal helper VA 0x06311e50 searches the BST with unsigned keys. Tree flags[0]
selects multi mode: equal keys are inserted to the right-search position. Unique
mode checks the selected parent or its predecessor; existing equal keys return
the existing node with inserted=false and perform no allocation/copy. A smaller
than minimum key inserts immediately. Actual insertion uses the already verified
node construction/rebalancing helper, returning node plus one-byte success flag.
Output padding remains untouched.

11,482 calls across 150 sequences, alternating unique/multi modes, pass against
original code. Ascending, descending and shuffled inputs include duplicates,
unsigned boundaries and Map payload lists of 0..3 Equipment entries. Complete
64KiB modeled heap, all tree-prefix bytes, all eight result bytes (including
padding), allocation pointer/size events and cursor progression agree. Duplicate
values in unique mode do not overwrite the stored Map. No search-result model is
used. Hinted insertion, output/value aliasing, native heap, failure/exception paths,
complete Loadout loading and machine-code matching remain unverified.
