# Loadout node insertion

Internal helper VA 0x06312480 allocates a 44-byte node, initializes parent/children,
red color and is_nil=0, then copies the key and Map payload. Map copy allocates
its Equipment list and preserves original field-construction padding behavior.
Insertion selects the left edge for head, a non-nil marker, or a smaller key;
otherwise it takes the right edge. Head root/min/max and size are updated. Standard
mirrored red-black recoloring and rotations restore a black root. The output
iterator receives the newly allocated node, not the rotated final cursor.

5687 insertions over 150 empty-to-growing trees compare original and reconstructed
instructions. Inputs include ascending/descending/random insertion, unsigned ID
boundaries, nil/non-nil left markers and Map lists of 0..3 entries. Full 64KiB heap,
tree prefix, output pointer and exact allocation events agree after every insert.
Allocator storage retains random bytes; all untouched/padding bytes are compared.
Rotations are now shared with erase. Regression checks pass: 3600 erases, 300 bulk
Free calls, 180 inconsistent-size recovery calls.

This helper accepts an already selected parent/marker; top-level duplicate/hint
selection is not yet reconstructed. Native allocation, failure/exception paths,
full Loadout file loading and instruction matching remain incomplete.
