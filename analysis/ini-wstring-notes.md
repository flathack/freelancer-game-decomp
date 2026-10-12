# INI_Reader::get_value_wstring

Original common.dll export VA 0x06310db0. Text mode passes text_value (offset
0x828) to mbstowcs with destination offset 0xc28 and limit 1024 wide characters.
Binary mode joins parameters in offset 0x1464, then passes the joined text to
mbstowcs with shared destination VA 0x063fbf98 and limit 256 wide characters.
The reconstructed source reuses the already reconstructed binary parameter join.
The result of mbstowcs is ignored in both modes. Neither destination is cleared;
short writes leave old tails, conversion errors retain partial results, and a
conversion reaching its limit need not append a terminator.

840 differential wide calls and 1577 integrated string getter calls pass against
original instructions. Numeric/bool/float/string/unknown tags, randomized joins,
missing entries, text lengths through 1023, BINI lengths around 256, high bytes,
and modeled conversion failures are covered. Full reader state, wide output
including tails, shared numeric buffer, returned pointer category, and exact
conversion input/count agree. The fixture uses a deterministic single-byte
conversion model with a controlled invalid byte. This proves call/dataflow
fidelity under that dependency model, not authentic MSVCRT locale/multibyte
behavior. Native Windows execution, arbitrary oversized buffer adjacency and
exact instruction matching remain unverified.
