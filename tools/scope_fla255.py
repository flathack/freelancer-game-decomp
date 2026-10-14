#!/usr/bin/env python3
"""Read-only original-byte/corpus evidence for FLA-255; not game implementation.
Requires the project's pefile environment. No original bytes or corpus contents
are written to public evidence. Private Ghidra indexes are verified against PE.
"""
import argparse
import collections
import csv
import hashlib
import json
import pathlib
import struct
import subprocess

BASE = 'bf555cdc5e177cb3a2485d98e6bca18ffabe5db2'
COMMON_SHA = 'e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
# Entries observed in PE exports, vtables, direct calls and prior fixed evidence.
ANCHORS = [
    0x062701e0, 0x06270330, 0x062704f0, 0x06270600, 0x06270740,
    0x062708c0, 0x062710f0, 0x06271600, 0x06271710,
    0x062f7bd0, 0x062efd00, 0x062efdc0, 0x062fa900,
    0x062eff70, 0x062f0170, 0x062f0230, 0x062f0340, 0x062f0040,
    0x062f3db0, 0x0626d530, 0x0626ddb0, 0x0626ddf0, 0x0626d5e0,
    0x062f5290, 0x0626e000, 0x0626e070, 0x0626e0f0,
    0x062f3e20, 0x062f05e0, 0x062f41e0, 0x062f5330,
    0x062f0890, 0x062f4390, 0x062f5440, 0x062f0a70,
    0x0632e6a0, 0x0632e690, 0x062bd490,
    0x0626d520, 0x0626dff0, 0x06325240,
    0x0627f640, 0x063221d0, 0x0626b770, 0x063015d0,
    0x062f9370, 0x062f11d0, 0x0630f6f0, 0x0630f800,
    0x0630fa40, 0x06310100, 0x06310450, 0x06310200,
    0x06302db0, 0x06333d70,
    # Direct dependencies actually read from the first original-evidence pass:
    # complete inherit subtype assignment set and populated Root container paths.
    0x0626eaf0, 0x0626dbb0, 0x0626e2c0, 0x0626f660,
    0x0626f870, 0x0626fa10, 0x062fb660,
    0x062fc530, 0x062fd350, 0x06319960, 0x062fc150,
    0x06319400, 0x06280e50, 0x062fd090, 0x062fd110,
    0x06342040, 0x063104a0, 0x06310c00,
    0x0630d470, 0x06333d60, 0x06333bd0,
    0x06308d00,  # Actual DataConfig::startup sequential configuration dispatch.
]
HEX = lambda x: f'0x{x:08x}'
SHA = lambda b: hashlib.sha256(b).hexdigest()


def quota():
    p = subprocess.run(['python3', '/opt/data/paperclip-guards/freelancer_quota.py', '--quota-check'], capture_output=True, text=True, check=False)
    print(p.stdout.strip(), flush=True)
    if p.returncode:
        raise SystemExit(p.returncode)


def segments(intervals):
    result = []
    for a, b in sorted(intervals):
        if result and a == result[-1][1]:
            result[-1][1] = b
        else:
            result.append([a, b])
    return result


def read_sections(data):
    """Ordered sections/keys only, TEXT and BINI v1; do not export values."""
    if data.startswith(b'BINI'):
        version, table = struct.unpack_from('<II', data, 4)
        if version != 1 or not 12 <= table <= len(data):
            raise ValueError('unsupported BINI')
        def text(off):
            a = table + off
            end = data.index(b'\0', a)
            return data[a:end].decode('cp1252')
        pos = 12
        sections = []
        while pos < table:
            name, count = struct.unpack_from('<HH', data, pos); pos += 4
            keys = []
            for _ in range(count):
                key, values = struct.unpack_from('<HB', data, pos); pos += 3
                keys.append(text(key))
                pos += values * 5
                if pos > table:
                    raise ValueError('BINI value outside entry area')
            sections.append((text(name), keys))
        if pos != table:
            raise ValueError('BINI section boundary')
        return 'BINI-v1', sections
    text = data.decode('cp1252')
    sections = []
    for line in text.splitlines():
        line = line.split(';', 1)[0].strip()
        if not line:
            continue
        if line.startswith('[') and ']' in line:
            sections.append((line[1:line.index(']')], []))
        elif '=' in line and sections:
            sections[-1][1].append(line.split('=', 1)[0].strip())
    return 'TEXT-cp1252', sections


def corpus(root, label):
    configuration = root / 'EXE/freelancer.ini'
    if not configuration.is_file():
        return {'label': label, 'available': False, 'root': str(root)}
    raw = configuration.read_bytes()
    if raw.startswith(b'BINI'):
        raise ValueError('configuration is BINI; ordered value parser required')
    section = ''
    entries = []
    order = 0
    for line in raw.decode('cp1252').splitlines():
        line = line.split(';', 1)[0].strip()
        if line.startswith('[') and ']' in line:
            section = line[1:line.index(']')].casefold()
        elif section == 'data' and '=' in line:
            key, value = [v.strip() for v in line.split('=', 1)]
            if key.casefold() not in ('goods', 'equipment', 'ships', 'solar'):
                continue
            order += 1
            relative = value.replace('\\', '/')
            path = root / 'DATA' / relative
            if not path.is_file():
                candidates = [p for p in (root / 'DATA').rglob('*.ini') if p.relative_to(root / 'DATA').as_posix().casefold() == relative.casefold()]
                if len(candidates) == 1:
                    path = candidates[0]
            item = {'configuration_order': order, 'kind': key.casefold(), 'relative_path': 'DATA/' + relative, 'exists': path.is_file()}
            if path.is_file():
                contents = path.read_bytes()
                fmt, sections = read_sections(contents)
                item.update({'bytes': len(contents), 'sha256': SHA(contents), 'format': fmt, 'section_count': len(sections), 'header_counts': dict(sorted(collections.Counter(n for n, _ in sections).items())), 'inherit_entry_count': sum(k.casefold() == 'inherit' for _, ks in sections for k in ks)})
            entries.append(item)
    return {'label': label, 'available': True, 'root': str(root), 'configuration': {'relative_path': 'EXE/freelancer.ini', 'sha256': SHA(raw), 'bytes': len(raw)}, 'active_relevant_entries_in_configuration_order': entries, 'file_count': len(entries), 'missing_files': sum(not f['exists'] for f in entries), 'real_loader_cases_executed': 0, 'contents_exported': False}


def collect(root, out):
    import pefile
    quota()
    original = root / 'original/_FL Fresh Install-deutsch/EXE/common.dll'
    data = original.read_bytes()
    assert SHA(data) == COMMON_SHA, 'Wrong original binary'
    pe = pefile.PE(data=data)
    image = pe.OPTIONAL_HEADER.ImageBase
    assert image == 0x06260000 and pe.FILE_HEADER.Machine == 0x14c
    rawroot = root / 'analysis/raw/common.dll'
    functions = {}
    with (rawroot / 'functions.tsv').open() as f:
        for row in csv.DictReader(f, delimiter='\t'):
            functions[int(row['address'], 16)] = row
    exports = collections.defaultdict(list)
    for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        if symbol.name:
            exports[image + symbol.address].append(symbol.name.decode('ascii'))
    selected = set(ANCHORS)
    # Follow the actual direct-call index for the proposed copy/lifetime kernel.
    # Shared already-reconstructed services and CRT entrypoints are explicit leaves.
    roots = {0x062eff70,0x062f0170,0x062f0230,0x062f0340,
             0x062f3db0,0x0626d530,0x0626ddb0,0x0626ddf0,
             0x0626d5e0,0x062f5290,0x0626e000,0x0626e070,
             0x0626e0f0,0x062f3e20,0x0632e6a0}
    leaves = {0x0630d470,0x06333bd0,0x06333d60,0x06333d70,
              0x063104a0,0x06310c00}
    call_index = collections.defaultdict(set)
    with (rawroot / 'calls.tsv').open() as f:
        for row in csv.DictReader(f, delimiter='\t'):
            if row['callee'].startswith('EXTERNAL:'):
                continue  # PE imports are inventoried as separate runtime leaves.
            call_index[int(row['caller'],16)].add(int(row['callee'],16))
    closure = set(roots)
    frontier = list(roots)
    while frontier:
        caller = frontier.pop()
        for target in call_index[caller]:
            if target in closure or target >= 0x06390000 or target not in functions:
                continue
            closure.add(target)
            if target not in leaves:
                frontier.append(target)
    selected.update(closure)
    ordered_anchors = list(ANCHORS) + sorted(selected-set(ANCHORS))
    instructions = collections.defaultdict(list)
    verified = 0
    with (rawroot / 'instructions.tsv').open() as f:
        for row in csv.DictReader(f, delimiter='\t'):
            if not row['function']:
                continue  # Decoded executable orphan, not an assigned function body.
            function = int(row['function'], 16)
            if function not in selected:
                continue
            address = int(row['address'], 16)
            code = bytes.fromhex(row['bytes'])
            assert pe.get_data(address-image, len(code)) == code, HEX(address)
            instructions[function].append((address, code, row['instruction']))
            verified += 1
    result = []
    for address in ordered_anchors:
        rows = instructions[address]
        assert rows, HEX(address)
        spans = segments([(a, a + len(b)) for a, b, _ in rows])
        spans_out = [{'start_va': HEX(a), 'end_va_exclusive': HEX(b), 'bytes': b-a, 'sha256': SHA(pe.get_data(a-image, b-a))} for a, b in spans]
        concat = b''.join(pe.get_data(a-image, b-a) for a, b in spans)
        assert len(concat) == int(functions[address]['body_bytes']), HEX(address)
        edges = []
        returns = []
        for a, b, ins in rows:
            if b[0] in (0xe8, 0xe9) and len(b) == 5:
                target = a + 5 + struct.unpack('<i', b[1:])[0]
                internal = any(lo <= target < hi for lo, hi in spans)
                kind = 'call' if b[0] == 0xe8 else ('intra_function_jump' if internal else 'tail_jump')
                edges.append({'callsite_va': HEX(a), 'kind': kind, 'target_va': HEX(target), 'exports': exports[target]})
            elif ins.startswith('CALL'):
                edges.append({'callsite_va': HEX(a), 'kind': 'indirect_call', 'operand': ins[4:].strip()})
            if ins.startswith('RET'):
                returns.append({'va': HEX(a), 'instruction': ins})
        result.append({'entry_va': HEX(address), 'index_name_not_semantic_proof': functions[address]['name'], 'exports': exports[address], 'instruction_count': len(rows), 'body_bytes': len(concat), 'sha256_address_order_instruction_spans': SHA(concat), 'half_open_spans': spans_out, 'direct_and_indirect_edges': edges, 'returns': returns})
    tables = []
    for name, address, words in [('GoodInfo_CommReferrable',0x063993e8,3), ('Root',0x063a11c0,6), ('Equipment',0x06399860,10), ('AttachedEquipment',0x06399af4,10), ('inherit_class_dispatch_table',0x062f4170,26)]:
        contents = pe.get_data(address-image, words*4)
        values = struct.unpack('<'+'I'*words, contents)
        tables.append({'name':name, 'start_va':HEX(address), 'end_va_exclusive':HEX(address+len(contents)), 'sha256':SHA(contents), 'slots':[{'offset':HEX(i*4), 'value_va':HEX(v), 'exports':exports[v]} for i,v in enumerate(values)]})
    helper_inputs = []
    for p in [rawroot/'functions.tsv', rawroot/'instructions.tsv', rawroot/'calls.tsv', root/'tools/disassemble_export.py']:
        helper_inputs.append({'relative_path':str(p.relative_to(root)), 'bytes':p.stat().st_size, 'sha256':SHA(p.read_bytes()), 'published_contents':False})
    modules = []
    siblings = {p.name.casefold():p for p in original.parent.iterdir() if p.is_file()}
    for descriptor in pe.DIRECTORY_ENTRY_IMPORT:
        name = descriptor.dll.decode('ascii')
        path = siblings.get(name.casefold())
        item = {'imported_name':name, 'available_in_original_exe_directory':path is not None, 'imported_symbol_count':len(descriptor.imports)}
        if path is not None:
            contents = path.read_bytes()
            item.update({'relative_path':str(path.relative_to(root)), 'bytes':len(contents), 'sha256':SHA(contents)})
        else:
            item['limit'] = 'Native Windows/CRT dependency; no hash or execution evidence available in this directory.'
        modules.append(item)
    doc = {'schema':1, 'base_commit':BASE, 'original_module':{'relative_path':str(original.relative_to(root)), 'sha256':COMMON_SHA, 'bytes':len(data), 'image_base':HEX(image), 'machine':'PE32-i386'}, 'method':'Instruction indexes are private hints; every selected instruction byte was compared to the pinned original PE. Discontiguous instruction bodies are represented as separate half-open spans; table data is hashed separately, not miscounted as code.', 'verified_original_instructions':verified, 'functions':result, 'tables':tables, 'input_hashes':helper_inputs, 'imported_modules':modules, 'proposed_kernel_direct_dependency_closure':{'roots':sorted(HEX(x) for x in roots), 'body_entries':sorted(HEX(x) for x in closure), 'shared_service_leaves':sorted(HEX(x) for x in leaves), 'native_crt_cutoff_va':HEX(0x06390000), 'limit':'Only indexed direct calls are followed. Indirect client/runtime/CRT dispatch is explicitly not an implemented body or proof of complete dynamic closure.'}, 'real_original_or_reconstructed_loader_cases_executed':0}
    inventories = [corpus(root/'original/_FL Fresh Install-deutsch', 'German original reference; pinned common.dll'), corpus(pathlib.Path('/opt/data/projects/Freelancer/Installations/Freelancer-HD'), 'HD mod corpus; distinct, not automatically the pinned original binary oracle')]
    out.mkdir(parents=True,exist_ok=True)
    (out/'original-evidence.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
    (out/'corpus-inventory.json').write_text(json.dumps({'schema':1,'corpora':inventories,'contents_uploaded':False},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'functions':len(result),'verified_instructions':verified,'tables':len(tables),'corpora':[{'label':c['label'],'available':c['available'],'file_count':c.get('file_count'),'missing_files':c.get('missing_files')} for c in inventories],'real_loader_cases_executed':0},ensure_ascii=False,indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', type=pathlib.Path, required=True)
    p.add_argument('--output', type=pathlib.Path, required=True)
    a = p.parse_args()
    collect(a.project_root, a.output)


if __name__ == '__main__':
    main()
