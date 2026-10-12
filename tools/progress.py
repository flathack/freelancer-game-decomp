#!/usr/bin/env python3
"""Report raw analysis and verification independently; never infer total-game matching."""
import json, pathlib, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
A=ROOT/'analysis'

def main():
    scope=json.loads((A/'decompilation-scope.json').read_text())
    rows=[]
    for module in scope:
        if not module['included']: continue
        name=pathlib.Path(module['module']).name
        out=A/'raw'/name
        row=dict(module=module['module'],status='pending')
        if (out/'summary.json').exists() and (out/'provenance.json').exists():
            provenance=json.loads((out/'provenance.json').read_text())
            if provenance['sha256']==module['sha256']:
                row.update(json.loads((out/'summary.json').read_text()))
                row['status']='raw_exported'
            else: row['status']='stale'
        if (out/'coverage-audit.json').exists():
            audit=json.loads((out/'coverage-audit.json').read_text())
            if audit['original_sha256']==module['sha256']:
                row['coverage_audit']={k:v for k,v in audit.items() if k not in ['gaps','orphan_run_starts']}
        rows.append(row)
    matches=json.loads((A/'matches.json').read_text())
    current_source=(A/'createid-behavior.json').exists()
    behavior=json.loads((A/'createid-behavior.json').read_text()) if current_source else {}
    current_source=current_source and behavior.get('source_sha256')==hashlib.sha256((ROOT/'src/create_id.cpp').read_bytes()).hexdigest()
    if current_source and behavior.get('header_sha256'):
        current_source=behavior['header_sha256']==hashlib.sha256((ROOT/'src/cfl_id_maker.hpp').read_bytes()).hexdigest()
    x86=json.loads((A/'flid-x86-behavior.json').read_text()) if (A/'flid-x86-behavior.json').exists() else {}
    x86_current=bool(x86) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in x86.get('source_hashes',{}).items())
    equip=json.loads((A/'equipdesc-x86-behavior.json').read_text()) if (A/'equipdesc-x86-behavior.json').exists() else {}
    equip_current=bool(equip) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in equip.get('source_hashes',{}).items())
    cache=json.loads((A/'stringcache-x86-behavior.json').read_text()) if (A/'stringcache-x86-behavior.json').exists() else {}
    cache_current=bool(cache) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in cache.get('source_hashes',{}).items())
    fm=json.loads((A/'filemap-x86-behavior.json').read_text()) if (A/'filemap-x86-behavior.json').exists() else {}
    fm_current=bool(fm) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in fm.get('source_hashes',{}).items())
    lifetime=json.loads((A/'filemap-lifetime-x86-behavior.json').read_text()) if (A/'filemap-lifetime-x86-behavior.json').exists() else {}
    lifetime_current=bool(lifetime) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in lifetime.get('source_hashes',{}).items())
    windows=json.loads((A/'filemap-windows-build.json').read_text()) if (A/'filemap-windows-build.json').exists() else {}
    windows_current=bool(windows) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in windows.get('source_hashes',{}).items())
    report=dict(code_modules=len(rows),raw_exported_modules=sum(r['status']=='raw_exported' for r in rows),
                raw_decompiled_functions=sum(r.get('raw_decompiled',0) for r in rows),
                raw_failed_functions=sum(r.get('failed',0) for r in rows),
                last_machine_code_check=dict(functions=matches['matched_functions'],bytes=matches['verified_code_bytes']),
                createid_behavior=dict(source_current=current_source,cases=behavior.get('cases',0),domain=behavior.get('domain')),
                flid_x86_behavior=dict(source_current=x86_current,hash_state_cases=x86.get('hash_and_full_crc_state_cases',0),counter_cases=x86.get('object_counter_cases',0),byte_update_cases=x86.get('byte_update_cases',0)),
                equipdesc_x86_behavior=dict(source_current=equip_current,passing_calls=equip.get('passing_calls',0),method_count=len(equip.get('covered_method_symbols',[])),cargo_cases=equip.get('cargo_cases',0),cargo_precision_differences=equip.get('cargo_extended_precision_differences'),temporary_x87_assembly_shim=True),
                stringcache_x86_behavior=dict(source_current=cache_current,sequence_cases=cache.get('sequence_cases',0),capacity_cases=cache.get('capacity_boundary_cases',0),tree_shape_checks=cache.get('tree_shape_checks',0),shutdown_checks=cache.get('shutdown_checks',[])),
                filemap_memory_x86_behavior=dict(source_current=fm_current,calls=fm.get('differential_calls',0),methods=len(fm.get('methods',[]))),
                filemap_lifetime_x86_behavior=dict(source_current=lifetime_current,calls=lifetime.get('lifetime_calls',0),compiled_exports=lifetime.get('compiled_exported_methods',0),external_imports_modeled=True),
                filemap_windows_build=dict(source_current=windows_current,exports=windows.get('export_count',0),named_imports=sum(len(v) for v in windows.get('imports',{}).values()),native_execution_verified=False),
                complete_game_verified=False,modules=rows)
    (A/'coverage-summary.json').write_text(json.dumps({r['module']:r['coverage_audit'] for r in rows if 'coverage_audit' in r},indent=2)+'\n')
    (A/'progress.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Decompilation progress','',
           f"Raw exports: {report['raw_exported_modules']} of {len(rows)} code-bearing installation modules.",
           f"Raw function outputs: {report['raw_decompiled_functions']}; failed decompilations: {report['raw_failed_functions']}.",
           f"Last exact machine-code check: {matches['matched_functions']} functions / {matches['verified_code_bytes']} bytes.",
           f"CreateID: {behavior.get('cases',0)} differential cases; source current: {current_source}.",
           f"Compiled x86 CFLIDMaker: {x86.get('hash_and_full_crc_state_cases',0)} hash/state, {x86.get('object_counter_cases',0)} counter and {x86.get('byte_update_cases',0)} update cases; source current: {x86_current}.",
           f"EquipDesc: {equip.get('passing_calls',0)} ABI/state cases and {equip.get('cargo_cases',0)} full-x87 cargo cases; temporary assembly ABI shim; source current: {equip_current}.",
           f"String cache: {cache.get('sequence_cases',0)} requests/tree shape checks and {cache.get('capacity_boundary_cases',0)} capacity cases; source current: {cache_current}.",
           f"FileMap memory/BINI subset: {fm.get('differential_calls',0)} calls across {len(fm.get('methods',[]))} methods; source current: {fm_current}.",
           f"FileMap lifetime: {lifetime.get('lifetime_calls',0)} modeled-import cases; Windows component: {windows.get('export_count',0)} exports, {sum(len(v) for v in windows.get('imports',{}).values())} imports; native runtime unverified.",'',
           'The full game is not reconstructed or verified. Raw outputs are not buildable source; function discovery may be incomplete.',
           '', '| Module | Raw export status | Raw functions | Failed |','|---|---|---:|---:|']
    for row in rows: lines.append(f"| {pathlib.Path(row['module']).name} | {row['status']} | {row.get('raw_decompiled','—')} | {row.get('failed','—')} |")
    (A/'progress.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines[:8]))
if __name__=='__main__': main()
