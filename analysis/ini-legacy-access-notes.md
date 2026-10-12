# Remaining legacy INI accessors

Original exports are direct jumps: get_name (0x062632d0) -> get_file_name;
get_value_ptr (0x06263340) -> joined get_value_string;
get_indexed_value (0x06263350) -> indexed get_value_string;
get_bool (0x06263360) -> get_value_bool. Reconstructed forwarding preserves
pointer identities, shared buffers, diagnostics and raw boolean AL bytes.

Legacy bool has 1170 direct differential calls plus 1170 integrated integer
regression calls. Legacy indexed/joined strings have 1577 calls including
buffer reuse, unknown tags, controlled reader-buffer overflow and text lookup.
Legacy filename has 48 direct calls within 144 lifecycle/metadata checks.
Dependencies use the existing CRT/OS models. Native execution and exact
instruction-byte matching remain unverified. These exports add aliases of
existing behavior; their test counts must not be treated as new unique game
logic coverage.
