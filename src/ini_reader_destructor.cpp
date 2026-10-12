#include "ini_reader.hpp"
// Member destruction releases binary_file first, then text_file, regardless of mode.
INI_Reader::~INI_Reader() {}
