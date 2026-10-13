# Goods-driven Cargo combining in the full loader

72 paired Load calls pass across six synthetic text files, both exported bool
values, two consecutive loads per context, and Goods flags 0/1/255. A manually
seeded Goods search node maps archetype 456 to a metadata record. Actual original/
reconstructed GoodList lookup and combination decision execute; the result is not
scripted. Reader, Loadout tree/vector, CreateID and StringAlloc also execute their
respective original/reconstructed implementations.

Cases cover fractional status sums below/above one, old or incoming status equal
to one, internal Cargo, external named hardpoints, and Equipment followed by Cargo.
Final semantic Maps/Equipment snapshots agree. Independent assertions verify that
Goods-enabled internal Cargo merges into one entry, retains the original Equipment
ID, sums count according to fractional rules, and yields exact expected binary32
status bits. External hardpoints or flag zero retain separate entries. Flag 255
works as nonzero without requiring a normalized metadata byte. Repeated loading
replaces entries and resets ID counters as before.

Goods records/tree are manually seeded, not loaded from actual Goods files. Raw
heap layout/padding and allocation trace are not compared. Real Goods database
construction, native runtime, allocation/exception failures, incompatible-first-
Cargo looping and malformed record ordering remain unverified in this suite.
Original mismatch looping is covered separately by vector-add tests. Whole game
reconstruction and instruction matching are still incomplete.
