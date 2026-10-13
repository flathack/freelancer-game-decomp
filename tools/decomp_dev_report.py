#!/usr/bin/env python3
"""Publish conservative objdiff v2 measures from pinned inventory and rebuilt matches."""
import argparse
import json
import pathlib
import subprocess
import tempfile
from verify_matches import coff_symbols

ROOT = pathlib.Path(__file__).resolve().parents[1]


def measures(total, matched, functions=0, matched_functions=0, units=1):
    percent = 100 * matched / total if total else 0
    return dict(total_code=str(total), matched_code=str(matched),
                matched_code_percent=percent, fuzzy_match_percent=percent,
                total_functions=functions, matched_functions=matched_functions,
                matched_functions_percent=100 * matched_functions / functions if functions else 0,
                total_units=units)


def generate():
    scope = {m['module']: m for m in json.loads((ROOT/'analysis/decompilation-scope.json').read_text()) if m['included']}
    inventory = json.loads((ROOT/'analysis/modules.json').read_text())
    evidence = json.loads((ROOT/'analysis/matches.json').read_text())['results']
    discovery = {pathlib.Path(m['module']).name: m.get('raw_decompiled', 0) for m in json.loads((ROOT/'analysis/progress.json').read_text())['modules']}
    with tempfile.TemporaryDirectory() as directory:
        obj = pathlib.Path(directory)/'csimple.obj'
        subprocess.run(['clang++', '--target=i686-pc-windows-msvc', '-O2', '-c',
                        str(ROOT/'src/csimple.cpp'), '-o', str(obj)], check=True)
        compiled = coff_symbols(obj)
    units, categories = [], []
    for module in inventory:
        path = module['path']
        if path not in scope:
            continue
        if module['sha256'] != scope[path]['sha256']:
            raise ValueError('Inventory hash mismatch: '+path)
        sections = [s for s in module['sections'] if s['executable']]
        total = sum(s['virtual_size'] for s in sections)
        functions = []
        seen = set()
        for match in evidence:
            if match['module'] != path:
                continue
            key = match['rva']
            if key in seen:
                raise ValueError('Duplicate match address')
            seen.add(key)
            expected = bytes.fromhex(match['original_hex'])
            if len(expected) != match['code_size'] or match['sha256'] != module['sha256']:
                raise ValueError('Invalid pinned match evidence')
            if not any(s['rva'] <= key and key+len(expected) <= s['rva']+s['virtual_size'] for s in sections):
                raise ValueError('Match outside executable sections')
            # Only this reconstruction has byte-match evidence so far.
            if match['symbol'] not in compiled:
                raise ValueError('No compiled symbol for pinned evidence')
            if compiled[match['symbol']][:len(expected)] == expected:
                functions.append(dict(name=match['symbol'], size=str(len(expected)),
                                      fuzzy_match_percent=100, address=str(key)))
        matched = sum(int(f['size']) for f in functions)
        count = discovery.get(pathlib.Path(path).name, 0)
        if count < len(functions) or matched > total:
            raise ValueError('Invalid progress totals')
        name = pathlib.Path(path).name
        category = name.replace('.', '_')
        m = measures(total, matched, count, len(functions))
        units.append(dict(name=name, measures=m, functions=functions,
                          metadata=dict(module_name=name, progress_categories=[category], complete=False)))
        categories.append(dict(id=category, name=name, measures=m))
    if len(units) != len(scope):
        raise ValueError('Missing scoped module inventory')
    aggregate = measures(sum(int(u['measures']['total_code']) for u in units),
                         sum(int(u['measures']['matched_code']) for u in units),
                         sum(u['measures']['total_functions'] for u in units),
                         sum(u['measures']['matched_functions'] for u in units), len(units))
    return dict(version=2, measures=aggregate, units=units, categories=categories)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=pathlib.Path, default=ROOT/'build/report.json')
    args = parser.parse_args()
    report = generate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report['measures'], indent=2))
