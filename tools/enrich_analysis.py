#!/usr/bin/env python3
"""Recover referenced orphan functions and export context for completed modules."""
import fcntl,hashlib,json,pathlib,subprocess
from decompile_all import ROOT,ANALYSIS,GHIDRA,save

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    lock=(ANALYSIS/'enrich.lock').open('w'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    scripts=['RecoverOrphanFunctions.java','ExportContext.java','ExportDecompilation.java']
    hashes={s:digest(ROOT/'tools/ghidra'/s) for s in scripts}
    scope=json.loads((ANALYSIS/'decompilation-scope.json').read_text())
    failed=[]
    for m in scope:
        if not m['included']: continue
        name=pathlib.Path(m['module']).name; out=ANALYSIS/'raw'/name
        if not (out/'provenance.json').exists() or not (out/'summary.json').exists(): continue
        prov=json.loads((out/'provenance.json').read_text())
        if prov['sha256']!=m['sha256'] or digest(ROOT/m['module'])!=m['sha256']: raise ValueError('Baseline mismatch')
        marker=out/'enrichment-provenance.json'
        if marker.exists():
            cached=json.loads(marker.read_text())
            if cached.get('script_hashes')==hashes and cached.get('raw_c_sha256')==digest(out/'raw.c'): continue
        project=prov['command'][2] if 'command' in prov else pathlib.Path(prov['project']).name
        cmd=[str(GHIDRA),str(ANALYSIS/'ghidra-project'),project,'-process',name,'-noanalysis',
             '-scriptPath',str(ROOT/'tools/ghidra')]
        for script in scripts[:1]+scripts[2:]+scripts[1:2]:
            cmd+=['-postScript',script,str(ANALYSIS/'raw')]
        cmd+=['-max-cpu','4']
        print('ENRICH '+name,flush=True)
        # Marker from this invocation is required; an old context summary is insufficient.
        summary=out/'context-summary.json'
        if summary.exists(): summary.unlink()
        with (ANALYSIS/'ghidra-logs'/(name+'-enrich.log')).open('w') as log:
            result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        if result.returncode or not summary.exists(): failed.append(name); print('FAILED '+name,flush=True); continue
        save(marker,dict(module=m['module'],sha256=m['sha256'],script_hashes=hashes,
                         raw_c_sha256=digest(out/'raw.c'),command=cmd))
        subprocess.run(['python3',str(ROOT/'tools/audit_context.py'),name],check=True)
    if failed: raise SystemExit('Failed modules: '+', '.join(failed))
if __name__=='__main__': main()
