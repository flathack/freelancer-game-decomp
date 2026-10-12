# INI_Reader::open

Original export VA 0x0630fa40. RefreshLoadingProgress is called before acquisition.
A temporary FileMap acquires file/mapping/view. A complete 12-byte header with
BINI magic and string-table offset less than file length selects binary handling;
version is not checked. Binary_file receives the temporary state and ownership,
then the reconstructed initialization helper re-reads its header. Otherwise the
temporary cursor returns to zero and text_file receives ownership; line_number
and text_header[0] reset. Previously owned reader resources are overwritten
without release, preserving original behavior. Failed acquisition leaves reader
state unchanged. With fatal=true it invokes FatalErrorFn(200, filename), returning
false if that handler returns. Cleanup releases temporary resources and filename.

768 differential calls cover eight synthetic inputs and 40 supplied INI files,
both prior reader modes, successful acquisition and three failure stages, and
both fatal settings. Complete reader bytes, modeled heap, allocation ownership,
resource release order and callback arguments agree. File APIs, MSVCP60, progress
and fatal callbacks are controlled models; no native OS execution is implied.
Reader filename inputs in this test start empty; shared pre-existing destination
names remain covered only by underlying FileMap tests. Allocation/exception
failures, a non-returning fatal handler and exact machine-code matching remain
unverified.
