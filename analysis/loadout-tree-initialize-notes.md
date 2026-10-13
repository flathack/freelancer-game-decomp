# Loadout tree initialization

Internal constructor VA 0x06311de0 copies allocator/comparator input bytes into
tree offsets 0/1, sets only multi flag byte at offset 12 to zero, allocates a
44-byte nil node followed by a 44-byte head node, and resets size. Nil has null
left/parent/right, black color and is_nil=1. Head has parent=nil, self left/right,
red color and is_nil=0. Other node payload, tail bytes and tree padding remain
untouched. The constructor returns the tree pointer and cleans two stack args.

65,536 differential constructors test every input-byte pair, rotating through
four object alignments. Complete 64-byte guarded object storage, 128-byte sentinel
allocation region and allocation size/pointer sequence agree. Allocator memory
starts nonzero, so unwritten payload/padding is checked directly. Allocation is
a controlled success model. Input/object aliases, allocation/exception failures,
native heap and startup integration remain unverified. Full Loadout file/list
loading and machine-code matching are still incomplete.
