#!/usr/bin/env python3
"""Compile reconstructions and compare COFF symbol bytes with pinned PE exports."""
import hashlib, json, pathlib, struct, subprocess
import pefile
ROOT = pathlib.Path(__file__).resolve().parents[1]

def coff_symbols(path):
    data = path.read_bytes()
    machine, nsections, _, symptr, nsymbols, optsize, _ = struct.unpack_from('<HHIIIHH', data)
    if machine != 0x14c: raise ValueError('Expected x86 COFF')
    sections = []
    for i in range(nsections):
        off = 20 + optsize + 40*i
        size, ptr = struct.unpack_from('<II', data, off+16)
        sections.append(data[ptr:ptr+size])
    strings = symptr + nsymbols*18
    symbols = {}
    i = 0
    while i < nsymbols:
        off = symptr + i*18
        namebytes = data[off:off+8]
        if namebytes[:4] == b'\0'*4:
            nameoff = strings + struct.unpack_from('<I', namebytes, 4)[0]
            name = data[nameoff:data.index(b'\0', nameoff)].decode()
        else: name = namebytes.rstrip(b'\0').decode()
        value, section, _, storage, aux = struct.unpack_from('<IhHBB', data, off+8)
        if section > 0 and storage == 2:
            symbols[name] = sections[section-1][value:]
        i += 1 + aux
    return symbols

def main():
    targets = json.loads((ROOT/'analysis/targets.json').read_text())
    compiled = {}; commands = []
    for source in sorted({t.get('source','src/csimple.cpp') for t in targets}):
        out = ROOT/'build'/(pathlib.Path(source).stem+'-match.obj')
        out.parent.mkdir(exist_ok=True)
        cmd = ['clang++', '--target=i686-pc-windows-msvc', '-O2', '-c', str(ROOT/source), '-o', str(out)]
        subprocess.run(cmd, check=True)
        compiled.update(coff_symbols(out));commands.append(cmd)
    results = []
    for t in targets:
        path = ROOT/t['module']
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != t['sha256']: raise ValueError('Original binary changed: '+str(path))
        pe = pefile.PE(str(path))
        export = next(s for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name.decode() == t['symbol'])
        if export.address != t['rva']: raise ValueError('Export address changed')
        expected = pe.get_data(t['rva'], t['code_size'])
        actual = compiled[t['symbol']][:t['code_size']]
        match = actual == expected
        results.append(dict(**t, original_hex=expected.hex(), compiled_hex=actual.hex(), matched=match))
        print(('MATCH' if match else 'FAIL')+' '+t['symbol']+' '+actual.hex())
        pe.close()
    report = dict(compiler=subprocess.check_output(['clang++','--version'],text=True).splitlines()[0],
        commands=commands, results=results, matched_functions=sum(r['matched'] for r in results),
        verified_code_bytes=sum(r['code_size'] for r in results if r['matched']),
        scope='Only listed function bodies; excludes alignment, linking, complete class layout, and runtime behavior.')
    (ROOT/'analysis/matches.json').write_text(json.dumps(report,indent=2)+'\n')
    if not all(r['matched'] for r in results): raise SystemExit(1)
if __name__ == '__main__': main()
