#!/usr/bin/env python3
"""Disassemble a bounded window at an export; window is NOT a function boundary."""
import argparse, pathlib, subprocess
import pefile
ROOT = pathlib.Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('module', help='Path relative to project root')
p.add_argument('symbol', help='Exact decorated export name')
p.add_argument('--bytes', type=int, default=128)
p.add_argument('--output', help='Save assembly relative to project root')
a = p.parse_args()
if not 1 <= a.bytes <= 65536: p.error('--bytes must be between 1 and 65536')
path = ROOT/a.module
pe = pefile.PE(str(path))
symbols = getattr(getattr(pe,'DIRECTORY_ENTRY_EXPORT',None),'symbols',[])
s = next((s for s in symbols if s.name and s.name.decode('ascii','replace') == a.symbol),None)
if s is None: p.error('Export not found')
if s.forwarder: p.error('Forwarded export: '+s.forwarder.decode())
start = pe.OPTIONAL_HEADER.ImageBase+s.address
cmd = ['objdump','-d','-Mintel',f'--start-address={start}',f'--stop-address={start+a.bytes}',str(path)]
assembly = '; Bounded analysis window, not a proven function extent.\n'+subprocess.check_output(cmd,text=True)
if a.output:
    output=ROOT/a.output
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(assembly)
else: print(assembly)
