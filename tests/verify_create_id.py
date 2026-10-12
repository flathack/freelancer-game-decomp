#!/usr/bin/env python3
"""Differential check: reconstructed native C++ versus original x86 CreateID.
Only allocator and ASCII _strlwr are mocked; all hashing instructions are original.
"""
import ctypes, hashlib, json, pathlib, random, struct, subprocess
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ESP, UC_X86_REG_EIP
ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT/'original/_FL Fresh Install-deutsch/EXE/common.dll'
HASH = 'e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'

def main():
    if hashlib.sha256(MODULE.read_bytes()).hexdigest() != HASH:
        raise ValueError('Wrong original binary')
    pe = pefile.PE(str(MODULE))
    base = pe.OPTIONAL_HEADER.ImageBase
    export = next(s for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name == b'?CreateID@@YAIPBD@Z')
    assert export.address == 0xad470
    assert next(s.name for e in pe.DIRECTORY_ENTRY_IMPORT for s in e.imports if s.address == 0x6399350) == b'_strlwr'
    uc = Uc(UC_ARCH_X86, UC_MODE_32)
    uc.mem_map(base, (pe.OPTIONAL_HEADER.SizeOfImage+4095) & ~4095)
    uc.mem_write(base, pe.get_memory_mapped_image())
    stack, input_addr, heap, stop, lower_stub = 0x20100000, 0x20200000, 0x20300000, 0x20400000, 0x20400010
    for addr in (stack,input_addr,heap,stop): uc.mem_map(addr,0x10000)
    uc.mem_write(0x6399350,struct.pack('<I',lower_stub))
    allocations=[]
    heap_cursor=heap
    def word(addr): return struct.unpack('<I',uc.mem_read(addr,4))[0]
    def return_value(value):
        esp=uc.reg_read(UC_X86_REG_ESP)
        uc.reg_write(UC_X86_REG_EAX,value)
        uc.reg_write(UC_X86_REG_ESP,esp+4)
        uc.reg_write(UC_X86_REG_EIP,word(esp))
    def hook(uc,addr,size,user):
        nonlocal heap_cursor
        esp=uc.reg_read(UC_X86_REG_ESP)
        if addr == 0x6391abc:
            size=word(esp+4)
            assert size in (8,0x41c), f'Unexpected allocation {size}'
            allocated=heap_cursor
            heap_cursor+=(size+15)&~15
            allocations.append(size)
            return_value(allocated)
        elif addr == lower_stub:
            ptr=word(esp+4)
            for i in range(256):
                byte=uc.mem_read(ptr+i,1)[0]
                if not byte: break
                assert byte < 128, 'Non-ASCII input outside test domain'
                if 65 <= byte <= 90: uc.mem_write(ptr+i,bytes([byte+32]))
            else: raise ValueError('Unterminated test input')
            return_value(ptr)
    uc.hook_add(UC_HOOK_CODE,hook)
    def original(value):
        if value is not None:
            assert len(value) <= 255 and b'\0' not in value
            uc.mem_write(input_addr,value+b'\0')
        esp=stack+0x8000
        uc.mem_write(esp,struct.pack('<II',stop,input_addr if value is not None else 0))
        uc.reg_write(UC_X86_REG_ESP,esp)
        uc.emu_start(base+export.address,stop,count=1000000)
        assert uc.reg_read(UC_X86_REG_EIP)==stop, 'Original did not finish'
        assert uc.reg_read(UC_X86_REG_ESP)==esp+4, 'Incorrect cdecl return stack'
        return uc.reg_read(UC_X86_REG_EAX)
    libpath=ROOT/'build/create_id.so'
    libpath.parent.mkdir(exist_ok=True)
    subprocess.run(['clang++','-O2','-shared','-fPIC',str(ROOT/'src/create_id.cpp'),'-o',str(libpath)],check=True)
    lib=ctypes.CDLL(str(libpath))
    reconstructed=lib.create_id_reconstructed
    reconstructed.argtypes=[ctypes.c_char_p]
    reconstructed.restype=ctypes.c_uint32
    rng=random.Random(2003)
    vectors=[None,b'',b'li01',b'LI01',b'Li01',b'ge_fighter',b'li01_01_base',b'A'*255,b'z'*255]
    vectors += [bytes([i]) for i in range(1,128)]
    vectors += [bytes(rng.randrange(1,128) for _ in range(rng.randrange(256))) for _ in range(500)]
    rows=[]
    for value in vectors:
        expected=original(value)
        actual=reconstructed(value)
        if expected != actual: raise AssertionError((value,hex(expected),hex(actual)))
        rows.append(dict(input_hex=value.hex() if value is not None else None,result=hex(actual)))
    assert allocations==[8,0x41c],allocations
    report=dict(status='passed',cases=len(rows),original_sha256=HASH,
                source_sha256=hashlib.sha256((ROOT/'src/create_id.cpp').read_bytes()).hexdigest(),
                domain='Null or zero-terminated ASCII strings of length 0..255; successful allocations.',
                mocks=['malloc at VA 0x06391abc','ASCII _strlwr via IAT VA 0x06399350'],
                not_verified=['Machine-code matching','CRT non-ASCII/locale behavior','Allocation failure/logging'],
                vectors=rows)
    (ROOT/'analysis/createid-behavior.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(rows)} cases against original x86 instructions, allocation sizes {allocations}')
if __name__=='__main__': main()
