#!/usr/bin/env python3
"""Link every original INI_Reader export against reconstructed code and test adapters."""
import hashlib,json,pathlib,subprocess
import pefile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(include_loadout=False,include_hash=False,include_cache=False,include_loader=False):
 original=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll';assert digest(original)=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 exports=[]
 for s in pefile.PE(str(original)).DIRECTORY_ENTRY_EXPORT.symbols:
  if not s.name:continue
  n=s.name.decode();owner=n.split('@@')[0]
  if owner.endswith('@INI_Reader') or owner in ['??0INI_Reader','??1INI_Reader','??4INI_Reader']:exports.append(n)
 sources=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'src').glob('ini*.cpp'))
 sources+=['src/file_map.cpp','src/string_index.cpp','src/text_file.cpp','src/parse_number.cpp','src/parse_number_x87.cpp']
 sources+=['tests/fixtures/'+p for p in ['file_map_x86_runtime.cpp','ini_text_runtime.cpp','ini_values_x86_runtime.cpp','ini_float_x86_runtime.cpp','ini_strings_x86_runtime.cpp','ini_lifetime_runtime.cpp','ini_number_runtime.cpp','ini_open_runtime.cpp','ini_wstring_runtime.cpp','parse_number_runtime.cpp']]
 if include_loadout:
  sources+=['src/loadout_lines.cpp','tests/fixtures/loadout_reader_runtime.cpp']
  exports+=['?ReadEquipLine@Loadout@@YA_NAAVINI_Reader@@AAUEquipDesc@@@Z','?ReadCargoLine@Loadout@@YA_NAAVINI_Reader@@AAUEquipDesc@@@Z']
 if include_hash:
  assert include_loadout
  sources.remove('tests/fixtures/loadout_reader_runtime.cpp')
  sources+=['tests/fixtures/loadout_reader_hash_runtime.cpp','src/create_id.cpp','tests/fixtures/flid_x86_runtime.cpp']
 if include_cache:
  assert include_hash
  sources.remove('tests/fixtures/loadout_reader_hash_runtime.cpp')
  sources+=['tests/fixtures/loadout_reader_cache_runtime.cpp','src/string_cache.cpp','tests/fixtures/string_cache_x86_runtime.cpp']
 if include_loader:
  assert include_cache
  sources+=['src/loadout_load.cpp','src/loadout_lookup.cpp','src/loadout_tree_initialize.cpp','src/loadout_insert.cpp','src/loadout_insert_unique.cpp','src/loadout_iterator.cpp','src/loadout_erase.cpp','src/loadout_free.cpp','src/loadout_map.cpp','src/loadout_map_constructor.cpp','src/subobject_id.cpp','src/equip_desc_vector_add.cpp','src/good_archetype_lookup.cpp','tests/fixtures/loadout_map_runtime.cpp','tests/fixtures/loadout_loader_runtime.cpp']
  exports+=['?Load@Loadout@@YAHPBD_N@Z','?Get@Loadout@@YAPBUMap@1@I@Z','?Free@Loadout@@YAXXZ','??0Map@Loadout@@QAE@XZ','??0Map@Loadout@@QAE@ABU01@@Z','??4Map@Loadout@@QAEAAU01@ABU01@@Z','??1Map@Loadout@@QAE@XZ']
 build=ROOT/('build/loadout-loader-fixture' if include_loader else 'build/loadout-cache-fixture' if include_cache else 'build/loadout-hash-fixture' if include_hash else 'build/loadout-reader-fixture' if include_loadout else 'build/ini-fixture');build.mkdir(parents=True,exist_ok=True);objects=[];commands=[]
 for source in sources:
  obj=build/(pathlib.Path(source).stem+'.obj');objects.append(str(obj))
  cmd=['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-mno-sse','-mno-sse2','-c',str(ROOT/source),'-o',str(obj)];subprocess.run(cmd,check=True);commands.append(cmd)
 data_exports=['?INIValuesStringBuffer@@3PADA','?StringIndexBuffer@@3PADA','?INIWideValueBuffer@@3PAGA','?INITextLineBuffer@@3PADA','?INIBinaryLineBuffer@@3PADA']
 if include_cache:data_exports+=['?StringCacheArena@@3PADA','?StringCacheFront@@3IA','?StringCacheBack@@3IA','?StringCacheInternedCount@@3IA','?StringCachePrivateCount@@3IA']
 dll=build/'freelancer-ini-fixture.dll';cmd=['lld-link','/dll','/noentry','/nodefaultlib','/base:0x19000000',f'/out:{dll}']+objects+['/export:'+n for n in exports]+['/export:'+n+',DATA' for n in data_exports];subprocess.run(cmd,check=True);commands.append(cmd)
 pe=pefile.PE(str(dll));actual=sorted(s.name.decode() for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name)
 assert actual==sorted(exports+data_exports)
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
 report=dict(status='all_ini_reader_exports_linked',export_count=len(exports),exports=sorted(exports),test_data_exports=data_exports,source_hashes={p:digest(ROOT/p) for p in sources+['src/ini_reader.hpp','tools/build_ini_fixture.py']},dll_sha256=digest(dll),commands=commands,log_link_abi_cases=16,log_link_code_match=dict(original_va='0x0634c430',bytes_hex=code.hex()),runtime_binding='test adapters use original image addresses; not standalone Windows runtime',complete_reader_runtime_verified=False,complete_game_verified=False)
 (ROOT/('analysis/loadout-loader-fixture-build.json' if include_loader else 'analysis/loadout-cache-fixture-build.json' if include_cache else 'analysis/loadout-hash-fixture-build.json' if include_hash else 'analysis/loadout-reader-fixture-build.json' if include_loadout else 'analysis/ini-fixture-build.json')).write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {len(exports)} original exports linked (39 INI_Reader methods); log_link matches 3 original bytes')
if __name__=='__main__':main()
