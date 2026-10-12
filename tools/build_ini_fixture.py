#!/usr/bin/env python3
"""Link every original INI_Reader export against reconstructed code and test adapters."""
import hashlib,json,pathlib,subprocess
import pefile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert digest(original)=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 exports=[]
 for s in pefile.PE(str(original)).DIRECTORY_ENTRY_EXPORT.symbols:
  if not s.name:continue
  n=s.name.decode();owner=n.split('@@')[0]
  if owner.endswith('@INI_Reader') or owner in ['??0INI_Reader','??1INI_Reader','??4INI_Reader']:exports.append(n)
 sources=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'src').glob('ini*.cpp'))
 sources+=['src/file_map.cpp','src/string_index.cpp','src/text_file.cpp','src/parse_number.cpp','src/parse_number_x87.cpp']
 sources+=['tests/fixtures/'+p for p in ['file_map_x86_runtime.cpp','ini_text_runtime.cpp','ini_values_x86_runtime.cpp','ini_float_x86_runtime.cpp','ini_strings_x86_runtime.cpp','ini_lifetime_runtime.cpp','ini_number_runtime.cpp','ini_open_runtime.cpp','ini_wstring_runtime.cpp','parse_number_runtime.cpp']]
 build=ROOT/'build/ini-fixture';build.mkdir(parents=True,exist_ok=True);objects=[];commands=[]
 for source in sources:
  obj=build/(pathlib.Path(source).stem+'.obj');objects.append(str(obj))
  cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-mno-sse','-mno-sse2','-c',str(ROOT/source),'-o',str(obj)];subprocess.run(cmd,check=True);commands.append(cmd)
 dll=build/'freelancer-ini-fixture.dll';cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x19000000',f'/out:{dll}']+objects+['/export:'+n for n in exports];subprocess.run(cmd,check=True);commands.append(cmd)
 pe=pefile.PE(str(dll));actual=sorted(s.name.decode() for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name)
 assert actual==sorted(exports)
 from verify_matches import coff_symbols
 symbol='?log_link@INI_Reader@@QBEXPBD@Z';code=coff_symbols(build/'ini_reader_log.obj')[symbol][:3];expected=pefile.PE(str(original)).get_data(0xec430,3);assert code==expected==b'\xc2\x04\x00'
 import sys
 sys.path.insert(0,str(ROOT/'tests'))
 from x86_harness import X86Harness
 h=X86Harness();original_exports=h.load(original);fixture_exports=h.load(dll)
 for obj in [0,1,0xffffffff,h.scratch]:
  for text in [0,1,0xffffffff,h.scratch+0x100]:
   h.invoke(original_exports[symbol],(text,),obj)
   h.invoke(fixture_exports[symbol],(text,),obj)
 report=dict(status='all_ini_reader_exports_linked',export_count=len(exports),exports=actual,source_hashes={p:digest(ROOT/p) for p in sources+['src/ini_reader.hpp','tools/build_ini_fixture.py']},dll_sha256=digest(dll),commands=commands,log_link_abi_cases=16,log_link_code_match=dict(original_va='0x0634c430',bytes_hex=code.hex()),runtime_binding='test adapters use original image addresses; not standalone Windows runtime',complete_reader_runtime_verified=False,complete_game_verified=False)
 (ROOT/'analysis/ini-fixture-build.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: all {len(exports)} original INI_Reader exports linked; log_link matches 3 original bytes')
if __name__=='__main__':main()
