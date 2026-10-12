#!/usr/bin/env python3
"""Run existing differential suites against one complete reader fixture DLL."""
import hashlib,json,pathlib,runpy,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'));sys.path.insert(0,str(ROOT/'tools'))
from x86_harness import X86Harness
from build_ini_fixture import main as build_fixture

def main():
 build_fixture();fixture=ROOT/'build/ini-fixture/freelancer-ini-fixture.dll'
 fixture_hash=hashlib.sha256(fixture.read_bytes()).hexdigest()
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
 suites=['verify_ini_constructor_x86.py','verify_ini_destructor_x86.py','verify_ini_copy_x86.py','verify_ini_open_memory_x86.py','verify_ini_open_x86.py','verify_ini_lifetime_x86.py','verify_ini_text_value_x86.py','verify_ini_float_x86.py','verify_ini_vector_x86.py','verify_ini_number_x86.py','verify_ini_bool_int_x86.py','verify_ini_strings_x86.py','verify_ini_wstring_x86.py','verify_ini_line_x86.py','verify_ini_legacy_bool_x86.py','verify_ini_legacy_strings_x86.py','verify_ini_legacy_name_x86.py']
 report_dir=ROOT/'analysis/ini-integrated';report_dir.mkdir(exist_ok=True);results=[]
 real_load=X86Harness.load;real_write=pathlib.Path.write_text;current=None
 def load(h,path):
  return real_load(h,original if pathlib.Path(path).resolve()==original else fixture)
 def write(path,data,*args,**kwargs):
  if path.parent==ROOT/'analysis' and path.name.endswith('-behavior.json'):
   report=json.loads(data)
   if 'compiled_dll_sha256' in report:report['compiled_dll_sha256']=fixture_hash
   report['integration_fixture_sha256']=fixture_hash
   report['integration_fixture']='build/ini-fixture/freelancer-ini-fixture.dll'
   report['suite']=current
   results.append(dict(suite=current,report=str((report_dir/path.name).relative_to(ROOT)),calls=report.get('differential_calls',0),integration_calls=report.get('integration_calls',0),vector_calls=report.get('vector_calls',0),wide_calls=report.get('wide_calls',0)))
   return real_write(report_dir/path.name,json.dumps(report,indent=2)+'\n',*args,**kwargs)
  return real_write(path,data,*args,**kwargs)
 X86Harness.load=load;pathlib.Path.write_text=write
 try:
  for suite in suites:
   current=suite;print('INTEGRATED:',suite,flush=True)
   runpy.run_path(str(ROOT/'tests'/suite),run_name='__main__')
 finally:X86Harness.load=real_load;pathlib.Path.write_text=real_write
 assert len(results)==len(suites)
 report=dict(status='passed',fixture_sha256=fixture_hash,fixture_build_report_sha256=hashlib.sha256((ROOT/'analysis/ini-fixture-build.json').read_bytes()).hexdigest(),suites=results,all_tests_use_same_reader_dll=True,native_runtime_verified=False,complete_game_verified=False)
 (ROOT/'analysis/ini-integrated.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {len(suites)} differential suites against one 39-export reader DLL')
if __name__=='__main__':main()
