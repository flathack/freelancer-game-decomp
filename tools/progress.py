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
    bini=json.loads((A/'bini-reader-x86-behavior.json').read_text()) if (A/'bini-reader-x86-behavior.json').exists() else {}
    bini_current=bool(bini) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in bini.get('source_hashes',{}).items())
    values=json.loads((A/'ini-bool-int-x86-behavior.json').read_text()) if (A/'ini-bool-int-x86-behavior.json').exists() else {}
    values_current=bool(values) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in values.get('source_hashes',{}).items())
    floats=json.loads((A/'ini-float-x86-behavior.json').read_text()) if (A/'ini-float-x86-behavior.json').exists() else {}
    floats_current=bool(floats) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in floats.get('source_hashes',{}).items())
    strings=json.loads((A/'ini-strings-x86-behavior.json').read_text()) if (A/'ini-strings-x86-behavior.json').exists() else {}
    strings_current=bool(strings) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in strings.get('source_hashes',{}).items())
    index=json.loads((A/'string-index-x86-behavior.json').read_text()) if (A/'string-index-x86-behavior.json').exists() else {}
    index_current=bool(index) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in index.get('source_hashes',{}).items())
    lines=json.loads((A/'text-file-x86-behavior.json').read_text()) if (A/'text-file-x86-behavior.json').exists() else {}
    headers=json.loads((A/'ini-text-header-x86-behavior.json').read_text()) if (A/'ini-text-header-x86-behavior.json').exists() else {}
    lines_current=bool(lines) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in lines.get('source_hashes',{}).items())
    headers_current=bool(headers) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in headers.get('source_hashes',{}).items())
    textvalues=json.loads((A/'ini-text-value-x86-behavior.json').read_text()) if (A/'ini-text-value-x86-behavior.json').exists() else {}
    textvalues_current=bool(textvalues) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in textvalues.get('source_hashes',{}).items())
    numbers=json.loads((A/'parse-number-x86-behavior.json').read_text()) if (A/'parse-number-x86-behavior.json').exists() else {}
    numbers_current=bool(numbers) and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in numbers.get('source_hashes',{}).items())
    reader_lifetime=json.loads((A/'ini-lifetime-x86-behavior.json').read_text())
    reader_memory=json.loads((A/'ini-open-memory-x86-behavior.json').read_text())
    reader_lifetime_current=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in reader_lifetime['source_hashes'].items())
    reader_memory_current=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in reader_memory['source_hashes'].items())
    reader_line=json.loads((A/'ini-line-x86-behavior.json').read_text())
    reader_line_current=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in reader_line['source_hashes'].items())
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
                bini_navigation_x86_behavior=dict(source_current=bini_current,calls=bini.get('differential_calls',0),methods=len(bini.get('covered_original_methods',[])),tested_real_files=bini.get('selected_real_files'),supplied_bini_files=bini.get('total_real_bini_files'),typed_getters_verified=False,text_iteration_verified=False),
                ini_bool_int_x86_behavior=dict(source_current=values_current,calls=values.get('differential_calls',0),parameter_cases=values.get('parameter_cases',0),external_runtime_modeled=True,text_index_cases=values.get('text_index_cases',0)),
                ini_float_x86_behavior=dict(source_current=floats_current,calls=floats.get('differential_calls',0),parameter_cases=floats.get('parameter_cases',0),full_80bit_returns_compared=True,assembly_in_getter=False,text_lookup_cases=floats.get('text_calls',0),external_atof_modeled=True),
                ini_strings_x86_behavior=dict(source_current=strings_current,calls=strings.get('differential_calls',0),indexed_cases=strings.get('indexed_parameter_cases',0),formatter_modeled=True,text_index_cases=strings.get('text_index_cases',0)),
                string_index_x86_behavior=dict(source_current=index_current,calls=index.get('differential_calls',0),inputs=index.get('input_cases',0),max_input_bytes=index.get('maximum_input_length',0)),
                text_line_x86_behavior=dict(source_current=lines_current,calls=lines.get('differential_calls',0),inputs=lines.get('input_cases',0)),
                text_header_x86_behavior=dict(source_current=headers_current,calls=headers.get('differential_calls',0),inputs=headers.get('input_cases',0)),
                text_value_x86_behavior=dict(source_current=textvalues_current,calls=textvalues.get('differential_calls',0),integration_calls=textvalues.get('integration_calls',0),real_files=len(textvalues.get('real_text_files',[])),sections=textvalues.get('real_sections',0),entries=textvalues.get('real_entries',0)),
                parse_number_x86_behavior=dict(source_current=numbers_current,calls=numbers.get('differential_calls',0),temporary_x87_arithmetic_boundary=True,external_crt_modeled=True),
                ini_reader_lifetime=dict(source_current=reader_lifetime_current,calls=reader_lifetime['differential_calls']),
                ini_reader_open_memory=dict(source_current=reader_memory_current,calls=reader_memory['differential_calls'],external_crt_modeled=True),
                ini_reader_line=dict(source_current=reader_line_current,calls=reader_line['line_calls'],integrated_calls=reader_line['differential_calls'],overflow_cases=reader_line['controlled_line_overflow_cases']),
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
           f"FileMap lifetime: {lifetime.get('lifetime_calls',0)} modeled-import cases; Windows component: {windows.get('export_count',0)} exports, {sum(len(v) for v in windows.get('imports',{}).values())} imports; native runtime unverified.",
           f"BINI navigation: {bini.get('differential_calls',0)} calls / {len(bini.get('covered_original_methods',[]))} methods; real corpus {bini.get('selected_real_files','sample')}/{bini.get('total_real_bini_files','unknown')}; typed getters/text iteration separately scoped.",
           f"Binary bool/int: {values.get('differential_calls',0)} calls / {values.get('parameter_cases',0)} cases; real CRT/full text iteration unverified.",
           f"Binary float: {floats.get('differential_calls',0)} full-x87 comparisons; C++ double ABI view; real CRT remains unverified.",
           f"String getters: {strings.get('differential_calls',0)} comparisons; shared/joined buffers; authentic CRT/full text iteration unverified.",
           f"StringIndex: {index.get('differential_calls',0)} comparisons / {index.get('input_cases',0)} inputs; reconstructed helper integrated.",
           f"Text lines/headers: {lines.get('differential_calls',0)} / {headers.get('differential_calls',0)} comparisons; text lifecycle remains open.",
           f"Text entries: {textvalues.get('differential_calls',0)} direct + {textvalues.get('integration_calls',0)} integrated calls; native runtime/lifecycle remain open.",
           f"ParseNumber: {numbers.get('differential_calls',0)} full-x87 comparisons; temporary arithmetic assembly boundary.",'',
           f"Reader close/metadata: {reader_lifetime['differential_calls']} calls; memory open: {reader_memory['differential_calls']} calls; native CRT/file open remains unverified.",
           f"Reader line formatting: {reader_line['line_calls']} direct calls / {reader_line['differential_calls']} integrated comparisons; {reader_line['controlled_line_overflow_cases']} static-buffer overflow sequences.",
           'The full game is not reconstructed or verified. Raw outputs are not buildable source; function discovery may be incomplete.',
           '', '| Module | Raw export status | Raw functions | Failed |','|---|---|---:|---:|']
    for row in rows: lines.append(f"| {pathlib.Path(row['module']).name} | {row['status']} | {row.get('raw_decompiled','—')} | {row.get('failed','—')} |")
    (A/'progress.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines[:8]))
if __name__=='__main__': main()
