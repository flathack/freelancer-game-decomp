#!/usr/bin/env python3
"""Goods pricing handlers versus original complete block execution (scoped).

Reader traversal/int values are controlled dependencies. The original complete
read_Good_block executes; reconstructed side executes ONLY pricing handlers.
No claim of a reconstructed full reader, database, or original-file coverage.
"""
import hashlib
import itertools
import json
import os
import pathlib
import random
import struct
import subprocess

from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EIP, UC_X86_REG_ESP
from x86_harness import X86Harness

ROOT = pathlib.Path(__file__).resolve().parents[1]
ORIGINAL_HASH = 'e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
BLOCK = '?read_Good_block@GoodInfoList@@AAEXPAVINI_Reader@@PAUGoodInfo@@@Z'
FIELDS = {'good_buy_price': 0x5c, 'bad_buy_price': 0x60,
          'good_sell_price': 0x64, 'bad_sell_price': 0x68}
FILES = ['src/good_info_price.cpp', 'src/good_info_price.hpp',
         'tests/fixtures/good_info_price_runtime.cpp', 'tests/verify_good_info_price_x86.py']


def binary80(value):
    """Exact promotion of binary64 fixture numbers to x87 memory format."""
    bits = struct.unpack('<Q', struct.pack('<d', value))[0]
    sign = bits >> 63
    exponent = (bits >> 52) & 0x7ff
    fraction = bits & ((1 << 52) - 1)
    if exponent == 0x7ff:
        return struct.pack('<QH', (1 << 63) | (fraction << 11), (sign << 15) | 0x7fff)
    if exponent:
        return struct.pack('<QH', (1 << 63) | (fraction << 11),
                           (sign << 15) | (exponent - 1023 + 16383))
    if not fraction:
        return struct.pack('<QH', 0, sign << 15)
    shift = 63 - (fraction.bit_length() - 1)
    return struct.pack('<QH', fraction << shift,
                       (sign << 15) | (16383 - 1074 + fraction.bit_length() - 1))


def build(source, name, base):
    objects = []
    for path in [source, ROOT / FILES[2]]:
        obj = ROOT / 'build' / (path.stem + '-' + name + '.obj')
        subprocess.run(['clang++', '--target=i686-pc-windows-msvc', '-O2',
                        '-fno-exceptions', '-fno-rtti', '-fno-builtin',
                        '-I' + str(ROOT / 'src'), '-c', str(path), '-o', str(obj)], check=True)
        objects.append(str(obj))
    dll = ROOT / 'build' / (name + '.dll')
    subprocess.run(['lld-link', '/dll', '/noentry', '/nodefaultlib',
                    '/base:' + hex(base), '/out:' + str(dll)] + objects +
                   ['/export:' + n for n in ['good_info_set_price',
                    'good_info_read_price_multiplier', 'good_price_check_abi']], check=True)
    return dll


def main():
    original = ROOT / 'original/_FL Fresh Install-deutsch/EXE/common.dll'
    assert hashlib.sha256(original.read_bytes()).hexdigest() == ORIGINAL_HASH
    rebuilt = build(ROOT / FILES[0], 'good_info_price', 0x1d000000)
    # Deliberately incorrect negative control: rounding FILD to binary32 before
    # multiplying defaults. The suite must reject this common reconstruction bug.
    scratch = pathlib.Path(os.environ['TMPDIR']) / 'fla124-price-negative'
    scratch.mkdir(exist_ok=True)
    text = (ROOT / FILES[0]).read_text()
    before = 'fst dword ptr [ecx+58h]'
    assert text.count(before) == 1
    mutation = scratch / 'good_info_price_rounded.cpp'
    mutation.write_text(text.replace(before, 'fstp dword ptr [ecx+58h]\n        fld dword ptr [ecx+58h]'))
    bad = build(mutation, 'good_info_price_negative', 0x1c000000)
    # A second mutation inserts a binary64 spill between the getter and FMUL.
    # Inputs just either side of a binary32 halfway tie make the lost low bits
    # observable, rather than relying on ordinary binary64 fixture values.
    spill_marker = 'call good_price_value_float\n        fmul'
    assert text.count(spill_marker) == 1
    spill = scratch / 'good_info_price_spill.cpp'
    spill.write_text(text.replace(spill_marker,
        'call good_price_value_float\n        sub esp, 8\n        fstp qword ptr [esp]\n'
        '        fld qword ptr [esp]\n        add esp, 8\n        fmul'))
    bad_spill = build(spill, 'good_info_price_spill_negative', 0x1b000000)
    h = X86Harness()
    orig = h.load(original)
    new = h.load(rebuilt)
    wrong = h.load(bad)
    wrong_spill = h.load(bad_spill)
    uc = h.uc
    reader = h.scratch + 0x2000
    fp = h.scratch + 0x3000
    control = fp + 0x20
    state = fp + 0x40
    literal = fp + 0x100
    uc.mem_write(literal, b'shop\0')
    rng = random.Random(2003)
    # FLD tbyte / RET 4: dependency returns full ST0 without C++ double spill.
    uc.mem_write(h.stop + 0x100, b'\xdb\x2d' + struct.pack('<I', fp) + b'\xc2\x04\x00')
    uc.mem_write(h.stop + 0x120, b'\xdb\xe3\xd9\x2d' + struct.pack('<I', control) + b'\xc3')
    uc.mem_write(h.stop + 0x140, b'\xdd\x35' + struct.pack('<I', state) + b'\xc3')
    uc.mem_write(h.stop + 0x160, b'\xdb\x2d' + struct.pack('<I', fp + 0x200) +
                 b'\xdb\x2d' + struct.pack('<I', fp + 0x210) + b'\xc3')
    uc.mem_write(fp + 0x200, binary80(1.25))
    uc.mem_write(fp + 0x210, binary80(-3.5))
    operations = []
    position = -1
    trace = []

    def ret(value, cleanup=0):
        sp = uc.reg_read(UC_X86_REG_ESP)
        uc.reg_write(UC_X86_REG_EAX, value & 0xffffffff)
        uc.reg_write(UC_X86_REG_EIP, h.word(sp))
        uc.reg_write(UC_X86_REG_ESP, sp + 4 + cleanup)

    def cstring(ptr):
        result = bytearray()
        while uc.mem_read(ptr, 1)[0]:
            result += uc.mem_read(ptr, 1)
            ptr += 1
        return result.decode('ascii')

    def hook(uc, address, size, user):
        nonlocal position
        sp = uc.reg_read(UC_X86_REG_ESP)
        if address == 0x6310200:
            assert uc.reg_read(UC_X86_REG_ECX) == reader
            position += 1
            ret(position < len(operations))
        elif address == 0x63104a0:
            assert uc.reg_read(UC_X86_REG_ECX) == reader
            ret(cstring(h.word(sp + 4)) == operations[position][0], 4)
        elif address == 0x6310850:
            assert uc.reg_read(UC_X86_REG_ECX) == reader and h.word(sp + 4) == 0
            assert operations[position][0] == 'price'
            trace.append(('int', operations[position][1]))
            ret(operations[position][1], 4)
        elif address == 0x6310980:
            assert uc.reg_read(UC_X86_REG_ECX) == reader and h.word(sp + 4) == 0
            assert operations[position][0] in FIELDS
            trace.append(('float80', operations[position][1].hex()))
            uc.mem_write(fp, operations[position][1])
            uc.reg_write(UC_X86_REG_EIP, h.stop + 0x100)

    uc.hook_add(UC_HOOK_CODE, hook)

    def fp_snapshot():
        h.invoke(h.stop + 0x140)
        data = bytes(uc.mem_read(state, 108))
        cw, sw, tag = [struct.unpack_from('<H', data, offset)[0] for offset in [0, 4, 8]]
        top = (sw >> 11) & 7
        live = tuple((i, data[28 + 10*i:38 + 10*i]) for i in range(8)
                     if ((tag >> (2*((top+i) & 7))) & 3) != 3)
        # Instruction/data pointers and empty register residuals are not ABI
        # results and differ between images. CW/SW/tags/live 80-bit values are.
        return cw, sw, tag, live

    abi_counts = {'reconstruction': 0, 'early_binary32': 0, 'getter_binary64_spill': 0}

    def run(exports, seed, alignment, cw, older_values):
        nonlocal position
        obj = h.scratch + 64 + alignment
        uc.mem_write(h.scratch, seed)
        uc.mem_write(control, struct.pack('<H', cw))
        h.invoke(h.stop + 0x120)
        if older_values:
            h.invoke(h.stop + 0x160)
        trace.clear()
        position = -1
        if exports is orig:
            h.invoke(orig[BLOCK], (reader, obj), h.scratch + 0x1000)
            assert position == len(operations)
            assert trace == [('int', v) if key == 'price' else ('float80', v.hex())
                             for key, v in operations]
        else:
            for position, (key, value) in enumerate(operations):
                if key == 'price':
                    args = (exports['good_info_set_price'], obj, value & 0xffffffff, 0)
                else:
                    args = (exports['good_info_read_price_multiplier'], obj, reader, FIELDS[key])
                assert h.invoke(exports['good_price_check_abi'], args) == 1, 'nonvolatile ABI mismatch'
                variant = ('early_binary32' if exports is wrong else
                           'getter_binary64_spill' if exports is wrong_spill else 'reconstruction')
                abi_counts[variant] += 1
            assert trace == [('float80', v.hex()) for key, v in operations if key != 'price']
        guarded = bytes(uc.mem_read(h.scratch, len(seed)))
        return guarded, fp_snapshot()

    cases = []
    prices = [-(1 << 31), -(1 << 31)+1, -16777219, -16777217, -65537,
              -1, 0, 1, 3, 50, 65537, 16777215, 16777216, 16777217,
              16777218, 16777219, 0x7ffffffe, 0x7fffffff]
    patterns = [0x00000000, 0x80000000, 0x3f800000, 0xbf800000,
                0x00000001, 0x80000001, 0x7f800000, 0xff800000,
                0x7fc01234, 0x7f801234]
    # All default/retain masks, plus negative zero, denormals, infinities, q/sNaN.
    for price, mask in itertools.product(prices, range(16)):
        initial = [0 if mask & (1 << j) else 0x3f800000 for j in range(4)]
        cases.append(('default-mask', [('price', price)], initial))
    for price, pattern in itertools.product(prices, patterns):
        cases.append(('special-existing', [('price', price)], [pattern]*4))
    floats = [binary80(v) for v in [0., -0., 1., -1., 0.95, 1.05,
              1e-300, 1e300, float('inf'), -float('inf'), float('nan')]]
    floats += [struct.pack('<QH', mantissa, exponent) for mantissa, exponent in [
        (0x8000000000000001, 0x3fff), (0x8000000000000401, 0x3fff),
        (0xffffffffffffffff, 0x3ffe), (0x8000000000000000, 0x0001),
        (0x0000000000000001, 0x0000), (0xa000000000000123, 0x7fff)]]
    tie_values = [struct.pack('<QH', mantissa, 0x3fff) for mantissa in
                  [0x8000008000000001, 0x8000007fffffffff]]
    floats += tie_values
    for key, value, price in itertools.product(FIELDS, floats, [0, 1, 16777217, 0x7fffffff]):
        cases.append(('multiplier80', [('price', price), (key, value)], [0]*4))
    # Order, repeated price, factor before price, zero override and mixed fields.
    for i in range(120):
        ops = [(rng.choice(['price'] + list(FIELDS)), None) for _ in range(rng.randrange(2, 9))]
        ops = [(key, rng.choice(prices) if key == 'price' else rng.choice(floats)) for key, _ in ops]
        cases.append(('sequence', ops, [rng.choice(patterns) for _ in range(4)]))
    controls = [(0x007f | pc | rc) for pc in [0, 0x0200, 0x0300]
                for rc in [0, 0x0400, 0x0800, 0x0c00]]
    counts = {}
    negative_mismatches = 0
    negative_storage_mismatches = 0
    negative_x87_mismatches = 0
    spill_storage_mismatches = 0
    spill_x87_mismatches = 0
    spill_cases = 0
    independent_checks = 0
    total = 0
    for cw in controls:
        for index, (kind, operations, initial) in enumerate(cases):
            alignment = [0, 1, 3][index % 3]
            obj_offset = 64 + alignment
            seed = bytearray(rng.randbytes(320))
            # Valid non-pricing context: ShipHull category bypasses Archetype
            # fallback; archetype=0 and nonempty shop avoid unrelated writes.
            for offset, value in [(0x4c, 2), (0x50, 0), (0x74, literal)]:
                struct.pack_into('<I', seed, obj_offset + offset, value)
            for j, value in enumerate(initial):
                struct.pack_into('<I', seed, obj_offset + 0x5c + 4*j, value)
            older_values = index % 2 == 0
            a = run(orig, bytes(seed), alignment, cw, older_values)
            b = run(new, bytes(seed), alignment, cw, older_values)
            assert a == b, (kind, index, hex(cw), operations, a, b)
            # Independent write-set assertion: neither side may touch anything
            # outside five pricing words, including guards and random padding.
            start = obj_offset + 0x58
            assert a[0][:start] == seed[:start] and a[0][start+20:] == seed[start+20:]
            assert a[1][0] == cw
            assert len(a[1][3]) == (2 if older_values else 0)
            if kind == 'default-mask' and operations[0][1] == 50 and cw == 0x037f:
                # Binary64 exactly represents these small integer * binary32
                # products. Round independently with struct.pack, NOT with the
                # pricing handler/original oracle and NOT decimal double 1.05.
                low = struct.unpack('<f', struct.pack('<I', 0x3f733333))[0]
                high = struct.unpack('<f', struct.pack('<I', 0x3f866666))[0]
                expected = [50., 50.*low, 50.*high, 50.*high, 50.*low]
                for j, prior in enumerate(initial):
                    if prior:
                        expected[j+1] = 1.
                assert a[0][start:start+20] == struct.pack('<5f', *expected), (
                    initial, a[0][start:start+20].hex(), struct.unpack('<5f', a[0][start:start+20]), expected)
                independent_checks += 1
            if kind == 'special-existing' and initial[0] not in [0, 0x80000000]:
                assert a[0][start+4:start+20] == struct.pack('<4I', *initial)
                independent_checks += 1
            if kind == 'default-mask' and operations[0][1] in [16777217, 16777219, 0x7fffffff]:
                mutated = run(wrong, bytes(seed), alignment, cw, older_values)
                if mutated != a:
                    negative_mismatches += 1
                if mutated[0] != a[0]:
                    negative_storage_mismatches += 1
                if mutated[1] != a[1]:
                    negative_x87_mismatches += 1
            if (kind == 'multiplier80' and operations[0][1] == 1
                    and operations[1][1] in tie_values):
                mutated = run(wrong_spill, bytes(seed), alignment, cw, older_values)
                spill_cases += 1
                if mutated[0] != a[0]:
                    spill_storage_mismatches += 1
                if mutated[1] != a[1]:
                    spill_x87_mismatches += 1
            total += 1
            counts[kind] = counts.get(kind, 0) + 1
    assert negative_mismatches > 0, 'negative control was not rejected'
    assert negative_storage_mismatches > 0, 'negative control did not change stored prices'
    assert spill_storage_mismatches > 0, 'binary64 getter spill was not rejected by stored prices'
    report = dict(status='passed', original_sha256=ORIGINAL_HASH,
                  original_entry=hex(orig[BLOCK]), differential_blocks=total,
                  cases_per_control=len(cases), x87_controls=[hex(v) for v in controls],
                  case_kinds=counts, reconstruction_handler_abi_calls=abi_counts['reconstruction'],
                  negative_control_handler_abi_calls={k: v for k, v in abi_counts.items()
                                                     if k != 'reconstruction'},
                  negative_control_mismatches=negative_mismatches,
                  negative_control_storage_mismatches=negative_storage_mismatches,
                  negative_control_x87_mismatches=negative_x87_mismatches,
                  binary64_spill_negative_control=dict(cases=spill_cases,
                      storage_mismatches=spill_storage_mismatches,
                      x87_mismatches=spill_x87_mismatches),
                  independent_expected_value_checks=independent_checks,
                  full_guarded_object_compared=True, x87_control_status_tags_live80_compared=True,
                  source_hashes={f: hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in FILES},
                  not_verified=['Complete Goods block/file reader', 'Original Goods file corpus',
                                'Archetype database and metadata fallback', 'Native Windows/CRT',
                                'Unmasked x87 exceptions or stack exhaustion', 'Exact instruction matching'])
    (ROOT/'analysis/good-info-price-x86-behavior.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f'PASS: {total} Goods pricing block comparisons; '
          f"{abi_counts['reconstruction']} reconstruction handler ABI checks; "
          f'{negative_storage_mismatches} rejected binary32-rounding and '
          f'{spill_storage_mismatches} rejected binary64-spill storage controls')


if __name__ == '__main__':
    main()
