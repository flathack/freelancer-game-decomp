"""Reusable in-process x86 PE emulator. No host OS execution of loaded images."""
import struct
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_ECX
class X86Harness:
 def __init__(self):
  self.uc=Uc(UC_ARCH_X86,UC_MODE_32)
  self.stack=0x20100000;self.scratch=0x20500000;self.stop=0x20400000
  for addr in [self.stack,self.scratch,self.stop]:self.uc.mem_map(addr,0x10000)
  self.uc.mem_write(self.stop+16,b'\xdb\x3d'+struct.pack('<I',self.scratch+0xff00)+b'\xc3')
 def load(self,path):
  p=pefile.PE(str(path));base=p.OPTIONAL_HEADER.ImageBase
  self.uc.mem_map(base,(p.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);self.uc.mem_write(base,p.get_memory_mapped_image())
  return {s.name.decode():base+s.address for s in p.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
 def write_word(self,address,value):self.uc.mem_write(address,struct.pack('<I',value&0xffffffff))
 def word(self,address):return struct.unpack('<I',self.uc.mem_read(address,4))[0]
 def invoke(self,address,args=(),this=None,float_result=False):
  sp=self.stack+0x8000;self.uc.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),self.stop,*args));self.uc.reg_write(UC_X86_REG_ESP,sp)
  if this is not None:self.uc.reg_write(UC_X86_REG_ECX,this)
  self.uc.emu_start(address,self.stop,count=1000000)
  assert self.uc.reg_read(UC_X86_REG_EIP)==self.stop,'Missing return'
  assert self.uc.reg_read(UC_X86_REG_ESP)==sp+4+(4*len(args) if this is not None else 0),'ABI stack mismatch'
  result=self.uc.reg_read(UC_X86_REG_EAX)
  if float_result:
   self.uc.reg_write(UC_X86_REG_ESP,sp);self.uc.mem_write(sp,struct.pack('<I',self.stop))
   self.uc.emu_start(self.stop+16,self.stop,count=10)
   result=bytes(self.uc.mem_read(self.scratch+0xff00,10))
  return result
 def return_stub(self,value):
  sp=self.uc.reg_read(UC_X86_REG_ESP)
  self.uc.reg_write(UC_X86_REG_EAX,value);self.uc.reg_write(UC_X86_REG_EIP,self.word(sp));self.uc.reg_write(UC_X86_REG_ESP,sp+4)

 def initialize_crt(self,path):
  p=pefile.PE(str(path));count=0
  for section in p.sections:
   if section.Name.rstrip(b'\0')==b'.CRT':
    data=section.get_data()
    for offset in range(0,len(data)-3,4):
     callback=struct.unpack_from('<I',data,offset)[0]
     if callback:
      assert p.OPTIONAL_HEADER.ImageBase<=callback<p.OPTIONAL_HEADER.ImageBase+p.OPTIONAL_HEADER.SizeOfImage
      self.invoke(callback);count+=1
  return count
