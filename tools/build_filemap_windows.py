#!/usr/bin/env python3
"""Build reconstructed FileMap with actual named CRT/Win32 imports (no fixed VAs)."""
import hashlib,json,pathlib,subprocess
import pefile
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 original_path=ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
 assert hashlib.sha256(original_path.read_bytes()).hexdigest()=='e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
 original=pefile.PE(str(original_path))
 names=[s.name.decode() for s in original.DIRECTORY_ENTRY_EXPORT.symbols if s.name and b'FileMap@@' in s.name]
 required={0x6399328,0x639932c,0x63991d4,0x63991bc,0x63991b8,0x63991a4,0x63991d0,0x63990d4,0x6399144,0x639913c,0x6399138,0x6399130,0x6399140}
 libraries={}
 for e in original.DIRECTORY_ENTRY_IMPORT:
  for s in e.imports:
   if s.address in required:libraries.setdefault(e.dll.decode(),[]).append((s.name.decode(),s.address==0x63991d0))
 out=ROOT/'build/filemap-windows';out.mkdir(parents=True,exist_ok=True);commands=[]
 def run(cmd):commands.append(cmd);subprocess.run(cmd,check=True)
 libs=[]
 for dll,exports in libraries.items():
  definition=out/(dll+'.def');library=out/(dll+'.lib')
  definition.write_text('LIBRARY '+dll+'\nEXPORTS\n'+''.join('  "'+n+'"'+(' DATA' if data else '')+'\n' for n,data in exports))
  run(['llvm-dlltool','-m','i386','-d',str(definition),'-l',str(library)]);libs.append(str(library))
 for source,name in [('src/file_map.cpp','file_map.obj'),('src/runtime/file_map_windows.cpp','runtime.obj')]:
  run(['clang++','--target=i686-pc-windows-msvc','-O2','-fno-exceptions','-fno-rtti','-fno-builtin','-c',str(ROOT/source),'-o',str(out/name)])
 dll=out/'freelancer-filemap.dll'
 run(['lld-link','/dll','/noentry','/nodefaultlib','/base:0x15000000',f'/out:{dll}',str(out/'file_map.obj'),str(out/'runtime.obj')]+libs+['/export:'+n for n in names])
 built=pefile.PE(str(dll));imports={e.dll.decode():sorted(s.name.decode() for s in e.imports) for e in built.DIRECTORY_ENTRY_IMPORT}
 expected={dll:sorted(n for n,data in exports) for dll,exports in libraries.items()}
 assert imports==expected,(imports,expected)
 assert sorted(s.name.decode() for s in built.DIRECTORY_ENTRY_EXPORT.symbols)==sorted(names)
 report=dict(status='linked_and_imports_verified',dll=str(dll.relative_to(ROOT)),dll_sha256=hashlib.sha256(dll.read_bytes()).hexdigest(),
             export_count=len(names),imports=imports,commands=commands,
             source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/file_map.cpp','src/file_map.hpp','src/runtime/file_map_windows.cpp']},
             runtime_execution_verified=False,scope='FileMap component DLL; not common.dll or the complete game. Requires matching external CRT/Windows DLLs.')
 (ROOT/'analysis/filemap-windows-build.json').write_text(json.dumps(report,indent=2)+'\n');print(f'Linked {len(names)} FileMap exports with {sum(len(v) for v in imports.values())} checked named imports, no fixed original-image addresses.')
if __name__=='__main__':main()
