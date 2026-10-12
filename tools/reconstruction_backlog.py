#!/usr/bin/env python3
"""Index decompiler warning/failure functions for targeted source reconstruction."""
import collections,csv,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1];A=ROOT/'analysis'
def main():
 issues=[];modules=[]
 for directory in sorted((A/'raw').iterdir()):
  if not (directory/'summary.json').exists():continue
  funcs={r['address']:r for r in csv.DictReader((directory/'functions.tsv').open(),delimiter='\t')}
  # Count distinct callers, not repeated edges.
  callers=collections.defaultdict(set)
  for r in csv.DictReader((directory/'calls.tsv').open(),delimiter='\t'):callers[r['callee']].add(r['caller'])
  warnings=collections.defaultdict(set)
  source=(directory/'raw.c').read_text()
  chunks=re.split(r'/\* Address: ([0-9a-fA-F]+); name: .*? \*/',source)
  for i in range(1,len(chunks),2):
   addr=chunks[i].lower();code=chunks[i+1]
   for warning in re.findall(r'/\* WARNING:.*?\*/',code,re.S):warnings[addr].add(' '.join(warning.split()))
  for addr,f in funcs.items():
   if f['status']=='failed' or warnings[addr]:
    issues.append(dict(module=directory.name,address=addr,name=f['name'],body_bytes=int(f['body_bytes']),
                       distinct_callers=len(callers[addr]),is_thunk=f['thunk']=='true',status=f['status'],error=f['error'],warnings=sorted(warnings[addr])))
  modules.append(dict(module=directory.name,functions=len(funcs),warnings_functions=sum(bool(warnings[a]) for a in funcs)))
 issues.sort(key=lambda r:(r['status']!='failed',r['is_thunk'],-r['distinct_callers'],-len(r['warnings']),r['module'],r['address']))
 report=dict(scope='Decompiler warnings/errors are review signals, not an exhaustive correctness audit.',
             modules=modules,issue_functions=len(issues),issues=issues)
 (A/'reconstruction-backlog.json').write_text(json.dumps(report,indent=2)+'\n')
 lines=['# Reconstruction review backlog','',report['scope'],'',f'{len(issues)} functions have failed output or explicit decompiler warnings.','',
        '| Module | Address | Function | Distinct callers | Warnings |','|---|---|---|---:|---:|']
 for r in issues[:150]:lines.append(f"| {r['module']} | {r['address']} | {r['name'].replace('|','/')} | {r['distinct_callers']} | {len(r['warnings'])} |")
 (A/'reconstruction-backlog.md').write_text('\n'.join(lines)+'\n')
 print(f'{len(modules)} modules indexed; {len(issues)} warning/error functions; ranked by failure status, substantive functions before thunks, and caller count.')
if __name__=='__main__':main()
