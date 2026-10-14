#!/usr/bin/env python3
"""FLA-263 N09/N10: real original/rebuilt CommReferrable callback.

Expectations were frozen from 0x0632e6a0..0x0632e71a before implementation.
The modeled leaves are INI is_value and whole_string only; the callback and
three-slot table are compiled implementations. No native Windows/CRT claim.
"""
import argparse
import hashlib
import json
import pathlib
import random
import struct
import subprocess
import sys

from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_INVALID, UcError
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_ECX,
    UC_X86_REG_EIP, UC_X86_REG_ESP, UC_X86_REG_EBX, UC_X86_REG_ESI,
    UC_X86_REG_EDI, UC_X86_REG_EBP)
from x86_harness import X86Harness

ROOT = pathlib.Path(__file__).resolve().parents[1]
COMMON_HASH = 'e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
ORIGINAL = ROOT / 'original/_FL Fresh Install-deutsch/EXE/common.dll'
CALLBACK = 0x0632e6a0
SPAN = (CALLBACK, 0x0632e71a)
REGS = [UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP]
VALUES = [0x12345678, 0x23456789, 0x3456789a, 0x456789ab]
U = lambda n: struct.pack('<I', n & 0xffffffff)


def build(source, label):
    dest = ROOT / 'build/fla263-comm'
    dest.mkdir(parents=True, exist_ok=True)
    obj = dest / (label + '.obj')
    dll = dest / (label + '.dll')
    runtime = dest / (label + '-runtime.obj')
    commands = [
        ['clang++', '--target=i686-pc-windows-msvc', '-O2', '-fno-builtin',
         '-fno-exceptions', '-fno-rtti', '-Wall', '-Wextra', '-Werror',
         '-c', str(ROOT / 'tests/fixtures/good_info_comm_runtime.cpp'), '-o', str(runtime)],
        ['clang++', '--target=i686-pc-windows-msvc', '-O2', '-fno-builtin',
         '-fno-exceptions', '-fno-rtti', '-Wall', '-Wextra', '-Werror',
         '-I' + str(ROOT / 'src'), '-c', str(source), '-o', str(obj)],
        ['lld-link', '/dll', '/noentry', '/nodefaultlib', '/base:0x15000000',
         '/out:' + str(dll), str(obj), str(runtime),
         '/export:good_info_read_comm', '/export:good_info_has_voice',
         '/export:good_info_prefix_ref', '/export:good_info_comm_slots,DATA']]
    for command in commands:
        subprocess.run(command, check=True)
    return dll, [{'argv': c, 'exit_code': 0} for c in commands]


class Machine:
    def __init__(self, dll, rebuilt):
        self.h = X86Harness()
        self.u = self.h.uc
        self.h.load(ORIGINAL)
        self.new = self.h.load(dll)
        self.rebuilt = rebuilt
        self.obj = self.h.scratch + 0x1000
        self.reader = self.h.scratch + 0x3000
        self.source = self.h.scratch + 0x4000
        self.trace = []
        self.fault = None
        self.known = True
        self.pointer = 0
        self.u.mem_write(self.h.stop + 0x100, b'\x8b\x01\xff\x60\x08')
        self.u.hook_add(UC_HOOK_CODE, self.hook)
        self.u.hook_add(UC_HOOK_MEM_INVALID, self.invalid)

    def ret(self, value, pop):
        sp = self.u.reg_read(UC_X86_REG_ESP)
        self.u.reg_write(UC_X86_REG_EAX, value)
        self.u.reg_write(UC_X86_REG_EIP, self.h.word(sp))
        self.u.reg_write(UC_X86_REG_ESP, sp + 4 + pop)

    def invalid(self, uc, access, address, size, value, user):
        self.fault = (access, address, size)
        return False

    def hook(self, uc, address, size, user):
        if self.rebuilt and SPAN[0] <= address < SPAN[1]:
            raise AssertionError('FORBIDDEN ORIGINAL CALLBACK FALLBACK')
        sp = uc.reg_read(UC_X86_REG_ESP)
        ecx = uc.reg_read(UC_X86_REG_ECX)
        if address == 0x063104a0:
            assert ecx == self.reader
            ptr = self.h.word(sp + 4)
            key = bytearray()
            while self.u.mem_read(ptr + len(key), 1)[0]:
                key += self.u.mem_read(ptr + len(key), 1)
            assert key == b'msg_id_prefix'
            self.trace.append(('is_value', key.decode()))
            self.ret(0x80 if self.known else 0, 4)
        elif address == 0x06310c00:
            assert ecx == self.reader
            self.trace.append(('whole_string', self.pointer))
            self.ret(self.pointer, 0)

    def run(self, seed, value, known=True, virtual=False, alignment=0, fault=False):
        self.trace = []
        self.fault = None
        self.known = known
        obj = self.obj + alignment
        self.u.mem_write(obj - 16, seed)
        self.h.write_word(obj, self.new['good_info_comm_slots'] if self.rebuilt else 0x063993e8)
        if fault:
            self.u.mem_map(0x24000000, 0x1000)
            self.u.mem_write(0x24000000, b'Q' * 0x1000)
            self.pointer = 0x24000fa0
        else:
            self.pointer = self.source if value is not None else 0
            if value is not None:
                self.u.mem_write(self.pointer, value + b'\0')
        before = bytes(self.u.mem_read(obj - 16, len(seed)))
        for reg, val in zip(REGS, VALUES):
            self.u.reg_write(reg, val)
        entry = (self.h.stop + 0x100 if virtual else
                 self.new['good_info_read_comm'] if self.rebuilt else CALLBACK)
        returned = False
        result = None
        try:
            result = self.h.invoke(entry, (self.reader,), obj) & 255
            returned = True
        except UcError:
            if self.fault is None:
                raise
        after = bytes(self.u.mem_read(obj - 16, len(seed)))
        if returned:
            assert all(self.u.reg_read(r) == v for r, v in zip(REGS, VALUES)), 'nonvolatile registers'
        if fault:
            self.u.mem_unmap(0x24000000, 0x1000)
        return dict(before=before, after=after, al=result, returned=returned,
                    fault=self.fault, trace=self.trace)


def expected(result, value, known, fault=False):
    want = bytearray(result['before'])
    if fault:
        assert not result['returned'] and result['fault'] is not None
        assert result['fault'][1:] == (0x24001000, 1)
    else:
        assert result['returned'] and result['fault'] is None
        assert result['al'] == int(known)
        if known:
            prefix = (value or b'')[:63]
            want[24:24 + len(prefix)] = prefix
            want[24 + len(prefix)] = 0
            want[20:24] = U(len(prefix))
    assert result['after'] == want, 'independent exact guarded write set'
    assert [x[0] for x in result['trace']] == (['is_value', 'whole_string'] if known else ['is_value'])


def paired(dll):
    original, rebuilt = Machine(dll, False), Machine(dll, True)
    normal = faults = 0
    values = [None, b''] + [b'P' * n for n in (1, 62, 63, 64, 255, 8191)]
    for seed_number in (17, 91, 451):
        rng = random.Random(seed_number)
        for alignment in range(4):
            for virtual in (False, True):
                for known in (False, True):
                    for value in values:
                        seed = rng.randbytes(192 + 32)
                        results = [m.run(seed, value, known, virtual, alignment) for m in (original, rebuilt)]
                        for r in results:
                            expected(r, value, known)
                        # Only image-relative table pointer is normalized, never payload/guards.
                        assert results[0]['after'][:16] + results[0]['after'][20:] == results[1]['after'][:16] + results[1]['after'][20:]
                        assert results[0]['trace'] == results[1]['trace']
                        normal += 1
                seed = rng.randbytes(224)
                results = [m.run(seed, None, True, virtual, alignment, fault=True) for m in (original, rebuilt)]
                for r in results:
                    expected(r, None, True, fault=True)
                assert results[0]['fault'] == results[1]['fault']
                faults += 1
    return normal, faults


def mutations(source):
    text = source.read_text()
    variants = {
        'bounded_scan': ('while (scan[length])', 'while (length < 63 && scan[length])'),
        'wrong_limit': ('length > 63 ? 63 : length', 'length > 62 ? 62 : length'),
        'wrong_length_offset': ('word(self, 4) = length;', 'word(self, 12) = length;'),
        'unknown_true': ('return 0; // unknown key', 'return 1; // unknown key'),
    }
    rejected = []
    for label, (old, new) in variants.items():
        assert text.count(old) == 1, label
        file = ROOT / 'build/fla263-comm' / (label + '.cpp')
        file.write_text(text.replace(old, new))
        dll, _ = build(file, label)
        try:
            paired(dll)
        except AssertionError as exc:
            rejected.append({'name': label, 'compiled': True, 'rejected': True, 'discriminator': str(exc)})
        else:
            raise AssertionError('SURVIVING COMPILED MUTATION: ' + label)
    return rejected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', default='analysis/fla263/comm-verification.json')
    args = parser.parse_args()
    assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == COMMON_HASH
    source = ROOT / 'src/good_info_comm.cpp'
    dll, commands = build(source, 'good_info_comm')
    normal, faults = paired(dll)
    defects = mutations(source)
    report = {'issue': 'FLA-263', 'scope_commit': 'c93583dcdca63e257d9a18dd9d51aa62905f5042',
              'original_sha256': COMMON_HASH, 'callback_span': [hex(x) for x in SPAN],
              'normal_pairs': normal, 'normal_thiscall_ret4_pairs': normal,
              'fault_pairs': faults, 'faults_counted_as_returns': 0,
              'modeled_services': ['INI_Reader::is_value', 'INI_Reader::get_value_string'],
              'compiled_defects': defects, 'commands': commands,
              'native_runs': 0, 'milestone_complete': False,
              'limits': ['Only N09/N10 callback probes; other N01-N15 gates not closed by this report.',
                         'No real file reader/DB or native CRT/Windows execution.',
                         'Unmasked native x87 and aliasing source/destination are not claimed.'],
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'test_sha256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
    dest = ROOT / args.report
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
