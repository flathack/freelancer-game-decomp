#!/usr/bin/env python3
"""Record every original file and PE metadata without executing game binaries."""
import hashlib, json, pathlib, datetime
import pefile
ROOT = pathlib.Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / 'original'
OUT = ROOT / 'analysis'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def main():
    OUT.mkdir(exist_ok=True)
    files, modules = [], []
    for p in sorted(ORIGINAL.rglob('*')):
        if not p.is_file(): continue
        record = dict(path=p.relative_to(ROOT).as_posix(), size=p.stat().st_size, sha256=sha(p))
        files.append(record)
        if p.suffix.lower() not in ('.exe', '.dll'): continue
        try:
            pe = pefile.PE(str(p))
            exports = [dict(name=s.name.decode('ascii', 'replace') if s.name else None,
                            ordinal=s.ordinal, rva=s.address,
                            forwarder=s.forwarder.decode('ascii', 'replace') if s.forwarder else None)
                       for s in getattr(getattr(pe, 'DIRECTORY_ENTRY_EXPORT', None), 'symbols', [])]
            imports = [dict(dll=e.dll.decode('ascii', 'replace'), symbols=[
                dict(name=s.name.decode('ascii', 'replace') if s.name else None, ordinal=s.ordinal)
                for s in e.imports]) for e in getattr(pe, 'DIRECTORY_ENTRY_IMPORT', [])]
            versions = [dict(file_version=f'{v.FileVersionMS >> 16}.{v.FileVersionMS & 65535}.{v.FileVersionLS >> 16}.{v.FileVersionLS & 65535}',
                             product_version=f'{v.ProductVersionMS >> 16}.{v.ProductVersionMS & 65535}.{v.ProductVersionLS >> 16}.{v.ProductVersionLS & 65535}')
                        for v in getattr(pe, 'VS_FIXEDFILEINFO', [])]
            metadata = dict(**record, machine=hex(pe.FILE_HEADER.Machine),
                image_base=hex(pe.OPTIONAL_HEADER.ImageBase), entry_rva=hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint),
                linker=f'{pe.OPTIONAL_HEADER.MajorLinkerVersion}.{pe.OPTIONAL_HEADER.MinorLinkerVersion}',
                pe_timestamp=pe.FILE_HEADER.TimeDateStamp, versions=versions,
                sections=[dict(name=s.Name.rstrip(b'\0').decode('ascii','replace'), rva=s.VirtualAddress,
                               virtual_size=s.Misc_VirtualSize, raw_size=s.SizeOfRawData,
                               executable=bool(s.Characteristics & 0x20000000)) for s in pe.sections],
                exports=exports, imports=imports)
            modules.append(metadata)
            pe.close()
        except pefile.PEFormatError as e:
            modules.append(dict(**record, error=str(e)))
    (OUT/'files.json').write_text(json.dumps(files, indent=2)+'\n')
    (OUT/'modules.json').write_text(json.dumps(modules, indent=2)+'\n')
    rows=['# Binary inventory', '', 'Generated from the supplied archive; authenticity and patch status are not independently verified.', '',
          '| Module | Bytes | File version | Linker | Exports |', '|---|---:|---|---|---:|']
    for m in modules:
        rows.append(f"| {m['path'].removeprefix('original/_FL Fresh Install-deutsch/')} | {m['size']} | {', '.join(v['file_version'] for v in m.get('versions', [])) or '—'} | {m.get('linker','—')} | {len(m.get('exports',[]))} |")
    (OUT/'inventory.md').write_text('\n'.join(rows)+'\n')
    print(f'{len(files)} files hashed; {len(modules)} PE candidates; {sum(len(m.get("exports",[])) for m in modules)} export entries (not unique functions).')
if __name__ == '__main__': main()
