# SubObjectID counter classes

Reconstructed EquipIdMaker, CollGroupIdMaker and ShieldIdMaker each contain a
single unsigned 16-bit counter. Constructors and Reset initialize it to 0x21,
3 and 0xfff0 respectively. CreateEquipID/CreateGroupID/CreateShieldID preincrement
and return the low word, including wraparound to zero; there are no bounds checks.
Assignment copies only that word and returns the target object. Original exports
share some implementation addresses; twelve export names are not twelve unique
algorithm bodies.

66,414 differential calls compare original instructions against compiled C++.
Equipment increment covers all 65,536 starting values; both other classes cover
boundary and randomized inputs. Constructor/reset writes, returned AX/pointer,
complete 64-byte guarded storage, self-assignment, unaligned sources and partial
word overlap agree. Constructor return registers and void-function return registers
are not compared. No external dependency models are used. Native execution,
world/Loadout Map integration and exact instruction matching remain unverified.
