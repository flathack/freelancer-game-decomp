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
        rows.append(row)
    matches=json.loads((A/'matches.json').read_text())
    current_source=(A/'createid-behavior.json').exists()
    behavior=json.loads((A/'createid-behavior.json').read_text()) if current_source else {}
    current_source=current_source and behavior.get('source_sha256')==hashlib.sha256((ROOT/'src/create_id.cpp').read_bytes()).hexdigest()
    report=dict(code_modules=len(rows),raw_exported_modules=sum(r['status']=='raw_exported' for r in rows),
                raw_decompiled_functions=sum(r.get('raw_decompiled',0) for r in rows),
                raw_failed_functions=sum(r.get('failed',0) for r in rows),
                last_machine_code_check=dict(functions=matches['matched_functions'],bytes=matches['verified_code_bytes']),
                createid_behavior=dict(source_current=current_source,cases=behavior.get('cases',0),domain=behavior.get('domain')),
                complete_game_verified=False,modules=rows)
    (A/'progress.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Decompilation progress','',
           f"Raw exports: {report['raw_exported_modules']} of {len(rows)} code-bearing installation modules.",
           f"Raw function outputs: {report['raw_decompiled_functions']}; failed decompilations: {report['raw_failed_functions']}.",
           f"Last exact machine-code check: {matches['matched_functions']} functions / {matches['verified_code_bytes']} bytes.",
           f"CreateID: {behavior.get('cases',0)} differential cases; source current: {current_source}.",'',
           'The full game is not reconstructed or verified. Raw outputs are not buildable source; function discovery may be incomplete.',
           '', '| Module | Raw export status | Raw functions | Failed |','|---|---|---:|---:|']
    for row in rows: lines.append(f"| {pathlib.Path(row['module']).name} | {row['status']} | {row.get('raw_decompiled','—')} | {row.get('failed','—')} |")
    (A/'progress.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines[:8]))
if __name__=='__main__': main()
