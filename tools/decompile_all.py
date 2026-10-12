#!/usr/bin/env python3
"""Resume raw Ghidra decompilation of installation PE modules with executable code.
This produces analysis artifacts, not verified/buildable C++ reconstructions.
"""
import argparse, datetime, fcntl, hashlib, json, pathlib, subprocess, os
ROOT=pathlib.Path(__file__).resolve().parents[1]
ANALYSIS=ROOT/'analysis'
GHIDRA=ROOT/'.tools/ghidra_12.1.4_PUBLIC/support/analyzeHeadless'

def save(path,value):
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,indent=2)+'\n')
    temp.replace(path)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--skip',action='append',default=[],help='Module basename to skip this run')
    args=ap.parse_args()
    lock=(ANALYSIS/'decompile.lock').open('w')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    modules=json.loads((ANALYSIS/'modules.json').read_text())
    scope=[]
    for m in modules:
        p=pathlib.Path(m['path'])
        gameplay=('EXE' in p.parts or ('DLLS' in p.parts and 'BIN' in p.parts))
        code=any(s['executable'] and s['raw_size'] for s in m.get('sections',[]))
        scope.append(dict(module=m['path'],sha256=m['sha256'],
                         category='code_module' if gameplay and code else 'resource_or_installer',
                         included=bool(gameplay and code)))
    save(ANALYSIS/'decompilation-scope.json',scope)
    state=dict(pid=os.getpid(),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               goal='Full verified Freelancer reconstruction; raw output is an intermediate step',modules=[])
    selected=[m for m in scope if m['included']]
    priority={'Freelancer.exe':0,'common.dll':1,'server.dll':2,'content.dll':3,'flserver.exe':4}
    selected.sort(key=lambda m:(priority.get(pathlib.Path(m['module']).name,10),m['module']))
    script_hash=hashlib.sha256((ROOT/'tools/ghidra/ExportDecompilation.java').read_bytes()).hexdigest()
    for m in selected:
        name=pathlib.Path(m['module']).name
        if name in args.skip: continue
        row=dict(**m,status='pending')
        state['modules'].append(row)
        out=ANALYSIS/'raw'/name
        provenance=out/'provenance.json'
        if (out/'summary.json').exists() and provenance.exists():
            cached=json.loads(provenance.read_text())
            if cached.get('sha256')==m['sha256'] and cached.get('script_sha256')==script_hash:
                row['status']='raw_exported_cached'
                save(ANALYSIS/'decompile-run.json',state)
                continue
        actual_hash=hashlib.sha256((ROOT/m['module']).read_bytes()).hexdigest()
        if actual_hash!=m['sha256']: raise ValueError('Changed baseline: '+m['module'])
        project='module_'+hashlib.sha256(m['module'].encode()).hexdigest()[:12]
        project_dir=ANALYSIS/'ghidra-project'
        project_dir.mkdir(exist_ok=True)
        logs=ANALYSIS/'ghidra-logs'
        logs.mkdir(exist_ok=True)
        cmd=[str(GHIDRA),str(project_dir),project]
        if (project_dir/(project+'.gpr')).exists(): cmd += ['-process',name]
        else: cmd += ['-import',str(ROOT/m['module'])]
        cmd += ['-scriptPath',str(ROOT/'tools/ghidra'),'-postScript','ExportDecompilation.java',
                str(ANALYSIS/'raw'),'-max-cpu','4','-log',str(logs/(name+'.log'))]
        row['status']='running'
        save(ANALYSIS/'decompile-run.json',state)
        print('START '+name,flush=True)
        # A stale summary cannot establish success for the current invocation.
        if (out/'summary.json').exists(): (out/'summary.json').unlink()
        with (logs/(name+'-console.log')).open('w') as log:
            process=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            row['process_pid']=process.pid
            save(ANALYSIS/'decompile-run.json',state)
            result=process.wait()
        row['exit_code']=result
        if result==0 and (out/'summary.json').exists():
            row['status']='raw_exported'
            row['summary']=json.loads((out/'summary.json').read_text())
            save(provenance,dict(module=m['module'],sha256=m['sha256'],script_sha256=script_hash,
                                 ghidra_version='12.1.4',command=cmd))
        else: row['status']='failed'
        save(ANALYSIS/'decompile-run.json',state)
        print(row['status'].upper()+' '+name,flush=True)
    state['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    save(ANALYSIS/'decompile-run.json',state)
    if any(m['status']=='failed' for m in state['modules']): raise SystemExit(1)
if __name__=='__main__': main()
