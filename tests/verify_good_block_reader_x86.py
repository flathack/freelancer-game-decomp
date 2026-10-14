#!/usr/bin/env python3
"""P1 complete block control flow vs original; services explicitly controlled.

Not a file/corpus, real Archetype database or native CRT verification. Rebuilt
blockreader must never execute original blockreader bytes. Guarded objects,
seeded node padding, dependency call order, raw AL, faults, ABI and live x87 are
compared. Existing pricing code is linked unchanged, not reimplemented.
"""
import argparse
import collections
import hashlib
import itertools
import json
import os
import pathlib
import random
import struct
import subprocess
import zlib

import pefile
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_INVALID, UcError
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EIP, UC_X86_REG_ESP
from x86_harness import X86Harness
from verify_good_info_price_x86 import binary80

ROOT = pathlib.Path(__file__).resolve().parents[1]
ORIGINAL_HASH = 'e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
START, END = 0x062708c0, 0x062710ed
DESTROY = '??1GoodInfo@@QAE@XZ'
FILES = ['src/good_block_reader.cpp', 'src/good_block_reader.hpp',
         'tests/fixtures/good_block_reader_runtime.cpp', 'tests/verify_good_block_reader_x86.py',
         'src/good_info_price.cpp', 'src/good_info_price.hpp', 'src/good_info_destroy.cpp',
         'tests/verify_good_info_price_x86.py', 'tests/x86_harness.py']


def build(source, name, base):
    objects = []
    for f in [source, ROOT / 'src/good_info_price.cpp', ROOT / 'src/good_info_destroy.cpp', ROOT / FILES[2]]:
        obj = ROOT / 'build' / (f.stem + '-' + name + '.obj')
        subprocess.run(['clang++', '--target=i686-pc-windows-msvc', '-O2', '-fno-exceptions',
                        '-fno-rtti', '-fno-builtin', '-Wall', '-Wextra', '-Werror',
                        '-I' + str(ROOT / 'src'), '-c', str(f), '-o', str(obj)], check=True)
        objects.append(str(obj))
    dll = ROOT / 'build' / (name + '.dll')
    subprocess.run(['lld-link', '/dll', '/noentry', '/nodefaultlib', '/base:' + hex(base),
                    '/out:' + str(dll)] + objects + ['/export:' + s for s in
                    ['good_info_read_block', 'good_block_check_abi', 'good_block_find_good',
                     'good_block_find_hull', 'good_block_unknown_category', DESTROY]], check=True)
    return dll


def ident(text):
    # A controlled dependency ID, deliberately NOT advertised as CreateID.
    return zlib.crc32((text or '').lower().encode('ascii')) | 0x80000000


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='debug subset; does not write accepted report')
    args = parser.parse_args()
    original = ROOT / 'original/_FL Fresh Install-deutsch/EXE/common.dll'
    assert hashlib.sha256(original.read_bytes()).hexdigest() == ORIGINAL_HASH
    (ROOT / 'build').mkdir(exist_ok=True)
    dll = build(ROOT / FILES[0], 'good_block_reader', 0x1a000000)
    h = X86Harness()
    orig, new = h.load(original), h.load(dll)
    uc = h.uc
    heap = 0x23000000
    uc.mem_map(heap, 0x10000)
    reader, listing, equipment_obj, lookup_good = [h.scratch + o for o in (0x2000, 0x2200, 0x2400, 0x2800)]
    strings = h.scratch + 0x4000
    fp, control, state = [h.scratch + o for o in (0x3000, 0x3020, 0x3040)]
    # Original indirect imports and virtual calls bind controlled fixtures.
    strcmp, dump, unknown, has_attach = [h.stop + o for o in (0x800, 0x820, 0x840, 0x860)]
    h.write_word(0x0639902c, strcmp)
    h.write_word(0x06399028, h.stop + 0x900)
    h.write_word(h.stop + 0x900, dump)
    h.write_word(h.stop + 0x2008, unknown)
    h.write_word(h.stop + 0x2124, has_attach)
    uc.mem_write(h.stop + 0x100, b'\xdb\x2d' + struct.pack('<I', fp) + b'\xc2\x04\x00')
    uc.mem_write(h.stop + 0x120, b'\xdb\xe3\xd9\x2d' + struct.pack('<I', control) + b'\xc3')
    uc.mem_write(h.stop + 0x140, b'\xdd\x35' + struct.pack('<I', state) + b'\xc3')
    uc.mem_write(h.stop + 0x160, b'\xdb\x2d' + struct.pack('<I', fp + 0x200) +
                 b'\xdb\x2d' + struct.pack('<I', fp + 0x210) + b'\xc3')
    uc.mem_write(fp + 0x200, binary80(1.25))
    uc.mem_write(fp + 0x210, binary80(-3.5))
    rng = random.Random(1242003)
    table = {}
    text_cursor = strings
    operations = []
    spec = {}
    position = -1
    events = []
    allocator = heap + 0x100
    obj = h.scratch + 64
    rebuilt_side = False
    covered = set()
    fault = None
    abi_calls = ownership_calls = 0

    def text_ptr(text):
        nonlocal text_cursor
        if text is None:
            return 0
        if text not in table:
            data = text.encode('ascii') + b'\0'
            assert text_cursor + len(data) < h.scratch + 0xf000
            table[text] = text_cursor
            uc.mem_write(text_cursor, data)
            text_cursor += len(data)
        return table[text]

    def cstring(ptr):
        if not ptr:
            return None
        data = bytearray()
        for i in range(512):
            b = uc.mem_read(ptr + i, 1)[0]
            if not b:
                return data.decode('ascii')
            data.append(b)
        raise AssertionError('Fixture string exceeded limit')

    def ret(value=0, cleanup=0):
        sp = uc.reg_read(UC_X86_REG_ESP)
        uc.reg_write(UC_X86_REG_EAX, value & 0xffffffff)
        uc.reg_write(UC_X86_REG_EIP, h.word(sp))
        uc.reg_write(UC_X86_REG_ESP, sp + 4 + cleanup)

    def resolve_id(value):
        return 0 if value == ident('missing') else value ^ 0x10203040

    def hook(uc, address, size, user):
        nonlocal position, allocator
        if START <= address < END:
            assert not rebuilt_side, 'Reconstruction executed original blockreader!'
            covered.add(address)
        sp = uc.reg_read(UC_X86_REG_ESP)
        ecx = uc.reg_read(UC_X86_REG_ECX)
        if address == 0x06310200:
            assert ecx == reader
            position += 1
            events.append(('read', position))
            ret(0x80 if position < len(operations) else 0)
        elif address == 0x063104a0:
            assert ecx == reader and 0 <= position < len(operations)
            key = cstring(h.word(sp + 4))
            events.append(('is', key))
            ret(0x80 if key.lower() == operations[position][0].lower() else 0, 4)
        elif address in (0x06310c00, 0x06310ac0):
            assert ecx == reader
            index = 0 if address == 0x06310c00 else h.word(sp + 4)
            value = operations[position][1][index]
            assert value is None or isinstance(value, str), (operations[position], index)
            events.append(('whole' if address == 0x06310c00 else 'string', index, value))
            result = text_ptr(value)
            if spec.get('unterminated_level') and address == 0x06310ac0 and index == 3:
                result = h.scratch + 0x10000 - 64
                uc.mem_write(result, b'x' * 64) # no NUL before unmapped page
            ret(result, 0 if address == 0x06310c00 else 4)
        elif address in (0x06310850, 0x06310640):
            assert ecx == reader
            index = h.word(sp + 4)
            value = operations[position][1][index]
            events.append(('int' if address == 0x06310850 else 'bool', index, value))
            ret(value, 4)
        elif address == 0x063105f0:
            assert ecx == reader
            index = h.word(sp + 4)
            value = operations[position][1][index]
            empty = value is None or value == ''
            if spec.get('null_nonempty') and value is None:
                empty = False
            events.append(('empty', index, empty))
            ret(0x80 if empty else 0, 4)
        elif address == 0x06310980:
            assert ecx == reader and h.word(sp + 4) == 0
            value = operations[position][1][0]
            assert isinstance(value, bytes) and len(value) == 10
            events.append(('float80', value.hex()))
            uc.mem_write(fp, value)
            uc.reg_write(UC_X86_REG_EIP, h.stop + 0x100)
        elif address == 0x0630d470:
            text = cstring(h.word(sp + 4))
            events.append(('hash', text))
            ret(ident(text))
        elif address == 0x062f11d0:
            value = h.word(h.word(sp + 4))
            events.append(('resolve', value))
            ret(resolve_id(value))
        elif address == 0x063015d0:
            output, value = h.word(sp + 4), h.word(h.word(sp + 8))
            global_lookup = ecx == 0x063fab80
            assert global_lookup or ecx == listing + 0x0c
            events.append(('find_hull' if global_lookup else 'find_good', value))
            found = not spec.get('hull_missing') if global_lookup else value in spec.get('duplicates', set())
            h.write_word(output, heap + 0xe00 if found else heap + 0xe40)
            ret(output, 8)
        elif address == new['good_block_find_good']:
            assert h.word(sp + 4) == listing
            value = h.word(sp + 8)
            events.append(('find_good', value))
            ret(lookup_good if value in spec.get('duplicates', set()) else 0)
        elif address == new['good_block_find_hull']:
            value = h.word(sp + 4)
            events.append(('find_hull', value))
            ret(0 if spec.get('hull_missing') else lookup_good)
        elif address == 0x062f9370:
            value = h.word(sp + 4)
            events.append(('get_equipment', value))
            ret(0 if spec.get('equipment_missing') else equipment_obj)
        elif address == 0x06333d60:
            events.append(('cache_clear',))
            h.write_word(ecx, text_ptr(''))
            ret()
        elif address == 0x06333bd0:
            text, lower = cstring(h.word(sp + 4)), h.word(sp + 8) & 0xff
            assert lower in (0, 1)
            events.append(('string_alloc', text, lower))
            ret(text_ptr(text.lower() if lower else text))
        elif address == strcmp:
            a, b = cstring(h.word(sp + 4)), cstring(h.word(sp + 8))
            assert a is not None and b is not None
            events.append(('stricmp', a, b))
            ret(0 if a.lower() == b.lower() else 1)
        elif address == dump:
            assert h.word(sp + 4) == 0x100001 and h.word(sp + 16) == 0xab
            events.append(('unknown_category', cstring(h.word(sp + 20))))
            ret()
        elif address == new['good_block_unknown_category']:
            events.append(('unknown_category', cstring(h.word(sp + 4))))
            ret()
        elif address == unknown:
            assert ecx == obj and h.word(sp + 4) == reader
            events.append(('unknown_key', operations[position][0]))
            h.write_word(obj + 4, h.word(obj + 4) + 1)
            ret(0, 4)
        elif address == has_attach:
            assert ecx == equipment_obj
            events.append(('has_attachment', spec.get('attachment', 1)))
            ret(spec.get('attachment', 1))
        elif address == 0x06391abc:
            length = h.word(sp + 4)
            assert length == 40 and allocator + 48 < heap + 0xd00
            events.append(('allocate', allocator, length, bytes(uc.mem_read(h.scratch, 320)).hex(),
                           bytes(uc.mem_read(heap, 4096)).hex()))
            result = allocator
            allocator += 48
            ret(result)
        elif address == 0x06391a7a:
            pointer = h.word(sp + 4)
            events.append(('free', pointer, bytes(uc.mem_read(h.scratch, 320)).hex(),
                           bytes(uc.mem_read(heap, 4096)).hex()))
            ret()

    def invalid_memory(uc, access, address, size, value, user):
        nonlocal fault
        fault = (access, address, size)
        return False

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.hook_add(UC_HOOK_MEM_INVALID, invalid_memory)

    def fpu_snapshot():
        h.invoke(h.stop + 0x140)
        data = bytes(uc.mem_read(state, 108))
        cw, sw, tag = [struct.unpack_from('<H', data, o)[0] for o in (0, 4, 8)]
        top = (sw >> 11) & 7
        live = tuple((i, data[28 + 10*i:38 + 10*i].hex()) for i in range(8)
                     if ((tag >> (2*((top+i) & 7))) & 3) != 3)
        return cw, sw, tag, live

    def seed_case(alignment):
        nonlocal obj, table, text_cursor
        obj = h.scratch + 64 + alignment
        table, text_cursor = {}, strings
        uc.mem_write(strings, b'\0' * 0x9000)
        seed = bytearray(rng.randbytes(320))
        start = 64 + alignment
        words = {0: h.stop + 0x2000, 4: 0, 0x48: 0, 0x4c: spec.get('category', 2),
                 0x50: 0xdeadbeef, 0x54: 0, 0x58: 0, 0x5c: 0, 0x60: 0, 0x64: 0,
                 0x68: 0, 0x6c: 50, 0x88: spec.get('name', 0), 0x8c: spec.get('info', 0),
                 0x90: 0, 0xb8: 0, 0xbc: 0}
        for offset in (0x74, 0x78, 0x7c, 0x80, 0x84):
            words[offset] = text_ptr(spec.get('initial_strings', {}).get(offset, ''))
        uc.mem_write(heap, rng.randbytes(4096))
        for head_offset, n in ((0x98, 0), (0xa4, 1), (0xb0, 2)):
            head = heap + n * 48
            words[head_offset] = head
            words[head_offset + 4] = spec.get('initial_count', 0)
            h.write_word(head, head)
            h.write_word(head + 4, head)
        for off, val in words.items():
            struct.pack_into('<I', seed, start + off, val & 0xffffffff)
        seed[start + 0x70] = 0
        for off, val in spec.get('initial_words', {}).items():
            struct.pack_into('<I', seed, start + off, val & 0xffffffff)
        uc.mem_write(h.scratch, bytes(seed))
        uc.mem_write(equipment_obj, rng.randbytes(192))
        h.write_word(equipment_obj, h.stop + 0x2100)
        h.write_word(equipment_obj + 0x14, spec.get('meta_name', 12345))
        h.write_word(equipment_obj + 0x18, spec.get('meta_info', 54321))
        h.write_word(equipment_obj + 0x0c, text_ptr(spec.get('meta_attach', 'meta_attach')))
        h.write_word(equipment_obj + 0x80, text_ptr(spec.get('meta_child', 'HpMeta')))
        h.write_word(listing + 0x10, heap + 0xe40)
        h.write_word(0x063fab84, heap + 0xe40)
        h.write_word(heap + 0xe00 + 0x10, lookup_good)
        h.write_word(lookup_good + 0x48, 0x81234567)
        h.write_word(0x063fbf0c, text_ptr('BAY'))
        uc.mem_write(0x063a4a74, struct.pack('<H', 0xfffe))
        # Preallocate ALL input and normalized cache texts before paired runs.
        for _, values in operations:
            for value in values:
                if isinstance(value, str):
                    text_ptr(value)
                    text_ptr(value.lower())
        return bytes(seed), bytes(uc.mem_read(heap, 4096))

    def run(exports, seed, heap_seed, cw, older):
        nonlocal position, allocator, rebuilt_side, fault, abi_calls, ownership_calls
        uc.mem_write(h.scratch, seed)
        uc.mem_write(heap, heap_seed)
        uc.mem_write(control, struct.pack('<H', cw))
        h.invoke(h.stop + 0x120)
        if older:
            h.invoke(h.stop + 0x160)
        position, allocator, fault = -1, heap + 0x100, None
        events.clear()
        rebuilt_side = exports is not orig
        entry = START if exports is orig else exports['good_info_read_block']
        try:
            assert h.invoke(new['good_block_check_abi'], (entry, listing, reader, obj)) == 1, 'nonvolatile ABI'
            abi_calls += 1
        except UcError:
            assert fault is not None, 'Unexpected emulator error without memory fault'
        storage, heap_after, trace = bytes(uc.mem_read(h.scratch, 320)), bytes(uc.mem_read(heap, 4096)), tuple(events)
        fp_state = fpu_snapshot()
        teardown = None
        if fault is None:
            events.clear()
            # Original destructor uses FS:[0] SEH bookkeeping. Map a controlled
            # TEB only for teardown; leave it UNMAPPED during block calls so the
            # original unchecked missing hull/equipment faults remain observable.
            uc.mem_map(0, 4096)
            try:
                h.invoke(exports[DESTROY], (), obj)
            except UcError:
                raise AssertionError(('Destructor fault', 'original' if exports is orig else 'rebuilt', fault,
                                      hex(uc.reg_read(UC_X86_REG_EIP)), tuple(events)))
            finally:
                uc.mem_unmap(0, 4096)
            ownership_calls += 1
            teardown = (bytes(uc.mem_read(h.scratch, 320)), bytes(uc.mem_read(heap, 4096)), tuple(events))
        return storage, heap_after, trace, fp_state, fault, position, teardown

    def independent(result, seed, heap_seed, alignment):
        storage, memory, trace, _, fault_result, consumed, teardown = result
        start = 64 + alignment
        def w(offset): return struct.unpack_from('<I', storage, start + offset)[0]
        def initial(offset): return struct.unpack_from('<I', seed, start + offset)[0]
        # Named field writes only; random padding/guards are never an oracle hole.
        writable = {4, 0x48, 0x4c, 0x50, 0x54, 0x58, 0x5c, 0x60, 0x64, 0x68,
                    0x6c, 0x74, 0x78, 0x7c, 0x80, 0x84, 0x88, 0x8c, 0x90,
                    0x9c, 0xa8, 0xb4, 0xb8, 0xbc}
        allowed = {start + off + j for off in writable for j in range(4)} | {start + 0x70}
        assert all(storage[i] == seed[i] for i in range(len(seed)) if i not in allowed), 'Object padding/guard write'
        duplicate_positions = [i for i, (k, v) in enumerate(operations)
                               if k.lower() == 'nickname' and ident(v[0]) in spec.get('duplicates', set())]
        duplicate = bool(duplicate_positions)
        if duplicate:
            assert consumed == duplicate_positions[0]
            assert not any(e[0] in ('get_equipment', 'has_attachment') for e in trace)
        else:
            assert consumed == len(operations) or fault_result is not None
        for aliases, offset in [(('ids_name', 'name'), 0x88), (('ids_info', 'info_desc'), 0x8c),
                                (('jump_dist',), 0x6c), (('combinable',), 0x70)]:
            values = [v[0] for k, v in operations[:consumed + 1] if k.lower() in aliases]
            if values:
                wanted = values[-1] & (0xff if offset == 0x70 else 0xffffffff)
                actual = storage[start + offset] if offset == 0x70 else w(offset)
                # Explicit zero names may be finalized from metadata.
                if wanted or duplicate or offset not in (0x88, 0x8c) or w(0x4c) not in (0, 1):
                    assert actual == wanted, (aliases, actual, wanted)
        categories = {'commodity': 0, 'equipment': 1, 'shiphull': 2, 'ship': 3}
        expected_category = initial(0x4c)
        for k, values in operations[:consumed + 1]:
            if k.lower() == 'category' and values[0].lower() in categories:
                expected_category = categories[values[0].lower()]
        assert w(0x4c) == expected_category
        processed = operations[:consumed + 1]
        accepted_names = []
        for key, values in processed:
            if key.lower() == 'nickname':
                value = ident(values[0])
                if value in spec.get('duplicates', set()): break
                accepted_names.append(value)
        assert w(0x48) == (accepted_names[-1] if accepted_names else initial(0x48))
        if fault_result is not None:
            expected_fault = (h.scratch + 0x10000 if spec.get('unterminated_level') else
                              0x48 if spec.get('hull_missing') else
                              0 if spec.get('name') and spec.get('info') else 0x14)
            assert fault_result[1] == expected_fault
        else:
            for key, offset in (('ship', 0x54), ('free_ammo', 0xb8)):
                values = [v for k, v in processed if k.lower() == key]
                if values:
                    assert w(offset) == resolve_id(ident(values[-1][0]))
                    if key == 'free_ammo':
                        assert w(0xbc) == values[-1][1] & 0xffffffff
            if any(k.lower() == 'hull' for k, _ in processed):
                assert w(0x90) == 0x81234567
            recognized = {'nickname', 'equipment', 'free_ammo', 'ids_name', 'name', 'ids_info', 'info_desc',
                          'category', 'ship', 'price', 'good_buy_price', 'bad_buy_price', 'good_sell_price',
                          'bad_sell_price', 'jump_dist', 'shop_archetype', 'material_library', 'item_icon',
                          'hp_child', 'attachment_archetype', 'hull', 'addon', 'combinable'}
            assert w(4) == sum(k.lower() not in recognized for k, _ in processed)
            expected_strings = {offset: spec.get('initial_strings', {}).get(offset, '')
                                for offset in (0x74, 0x78, 0x7c, 0x80, 0x84)}
            for key, values in processed:
                offset = {'shop_archetype': 0x74, 'item_icon': 0x78, 'material_library': 0x7c,
                          'hp_child': 0x80, 'attachment_archetype': 0x84}.get(key.lower())
                if offset is not None:
                    expected_strings[offset] = values[0] if offset == 0x80 else values[0].lower()
            if not duplicate:
                if expected_category in (0, 1) and spec.get('attachment', 1):
                    if not expected_strings[0x84]: expected_strings[0x84] = spec.get('meta_attach', 'meta_attach')
                    if not expected_strings[0x80]: expected_strings[0x80] = spec.get('meta_child', 'HpMeta')
                if not expected_strings[0x74]: expected_strings[0x74] = expected_strings[0x84]
            for offset, text in expected_strings.items():
                assert w(offset) == text_ptr(text), ('cache/fallback expectation', offset, text)
        if not duplicate and fault_result is None:
            equipment_values = [v[0] for k, v in operations if k.lower() == 'equipment']
            expected_equipment = resolve_id(ident(equipment_values[-1])) if equipment_values else 0
            assert w(0x50) == (expected_equipment if expected_category in (0, 1) else 0)
            if expected_category in (0, 1):
                for offset, setting in ((0x88, 'meta_name'), (0x8c, 'meta_info')):
                    values = [v[0] for k, v in operations if k.lower() in
                              (('ids_name', 'name') if offset == 0x88 else ('ids_info', 'info_desc'))]
                    explicit = values[-1] & 0xffffffff if values else initial(offset)
                    assert w(offset) == (explicit or spec.get(setting, 12345 if offset == 0x88 else 54321))
            # Three ownership lists checked without using original node values.
            addons = [v for k, v in operations if k.lower() == 'addon']
            expected_lists = collections.defaultdict(list)
            for i, values in enumerate(addons):
                level = (values[3] or '')[:63].lower()
                offset = {'mid': 0xa4, 'high': 0xb0}.get(level, 0x98)
                expected_lists[offset].append((heap + 0x100 + 48*i, values))
            free_order = []
            for offset, head in ((0x98, heap), (0xa4, heap + 48), (0xb0, heap + 96)):
                assert w(offset) == head
                assert w(offset + 4) == (spec.get('initial_count', 0) + len(expected_lists[offset])) & 0xffffffff
                node = struct.unpack_from('<I', memory, head - heap)[0]
                for expected_node, values in expected_lists[offset]:
                    assert node == expected_node, 'Append ordering'
                    base = node - heap
                    assert memory[base + 8] == 0
                    assert struct.unpack_from('<H', memory, base + 10)[0] == 0xfffe
                    assert struct.unpack_from('<I', memory, base + 12)[0] == resolve_id(ident(values[0]))
                    hp = text_ptr('BAY' if values[1].lower() == 'internal' else values[1])
                    assert struct.unpack_from('<I', memory, base + 16)[0] == hp
                    assert memory[base + 20] == 1
                    assert struct.unpack_from('<I', memory, base + 24)[0] == 0x3f800000
                    assert struct.unpack_from('<I', memory, base + 28)[0] == max(1, values[2])
                    assert memory[base + 32] == 0 and struct.unpack_from('<I', memory, base + 36)[0] == 0
                    for p in (9, 21, 22, 23, 33, 34, 35):
                        assert memory[base + p] == heap_seed[base + p], 'Node padding modified'
                    free_order.append(node)
                    node = struct.unpack_from('<I', memory, base)[0]
                assert node == head
            assert [e[1] for e in teardown[2]] == free_order + [heap + 96, heap + 48, heap]

    cases = []
    def add(kind, ops=(), **settings): cases.append((kind, list(ops), settings))
    add('empty')
    for category in (-1, 0, 1, 2, 3, 4):
        add('initial-category', category=category)
    for value in ('Commodity', 'Equipment', 'ShipHull', 'Ship', 'eQuIpMeNt', 'nonsense', ''):
        add('category', [('category', [value])])
    for key in ('ids_name', 'name', 'ids_info', 'info_desc', 'jump_dist'):
        for value in (0, -1, -2147483648, 2147483647):
            add('integer', [(key, [value])])
    for value in range(256): add('bool-raw-al', [('combinable', [value])])
    for key in ('nickname', 'equipment', 'ship', 'hull'):
        for value in ('alpha', 'BETA', 'missing'):
            add('id-reference', [(key, [value])], category=1 if key == 'equipment' else 2)
    add('free-ammo', [('free_ammo', ['alpha', -10])])
    add('free-ammo-repeat', [('free_ammo', ['alpha', 100]), ('free_ammo', ['missing', -1])])
    for key in ('shop_archetype', 'material_library', 'item_icon', 'HP_child', 'attachment_archetype'):
        for value in ('MixedCase', '', 'X' * 63):
            add('cache', [(key, [value]), (key, ['LastValue'])])
    for cls, hp, count in itertools.product(('', None, 'mid', 'MID', 'high', 'HiGh', 'unknown', 'x' * 80),
                                           ('internal', 'InTeRnAl', 'HpMount'), (-2147483648, 0, 1, 9)):
        add('addon', [('addon', ['alpha', hp, count, cls])])
    add('addon-null-nonempty', [('addon', ['missing', 'HpMissing', 0, None])], null_nonempty=True)
    add('addon-unterminated-level-fault', [('addon', ['alpha', 'HpOne', 1, 'x' * 64])], unterminated_level=True)
    add('addon-all-lists', [('addon', ['alpha', 'internal', -5, 'mid']),
                          ('addon', ['beta', 'HpOne', 2, 'high']),
                          ('addon', ['missing', 'HpTwo', 3, 'low']),
                          ('addon', ['alpha', 'HpThree', 4, 'mid'])])
    add('addon-size-wrap', [('addon', ['alpha', 'internal', 1, 'low'])], initial_count=0xffffffff)
    for attachment, strings_seed, name, info in itertools.product((0, 1, 0x80), (False, True), (0, 999), (0, 888)):
        add('metadata-fallback', [('category', ['Equipment']), ('equipment', ['alpha'])],
            attachment=attachment, name=name, info=info,
            initial_strings={0x74: 'explicit_shop', 0x80: 'ExplicitHp', 0x84: 'explicit_attach'} if strings_seed else {})
    add('metadata-empty', category=1, meta_attach='', meta_child='')
    add('unknown', [('alien', ['ignored']), ('another_key', [999])])
    add('category-unknown-repeat', [('category', ['Equipment']), ('category', ['???']), ('equipment', ['missing'])])
    add('duplicate-first', [('nickname', ['existing']), ('price', [100])], duplicates={ident('existing')})
    add('duplicate-late', [('jump_dist', [-5]), ('nickname', ['new']), ('nickname', ['existing']), ('ids_name', [42])], duplicates={ident('existing')})
    add('duplicate-after-addon', [('addon', ['alpha', 'HpOne', 1, 'mid']), ('nickname', ['existing'])], duplicates={ident('existing')})
    add('missing-hull-fault', [('hull', ['missing'])], hull_missing=True)
    add('missing-equipment-fault', [('category', ['Equipment']), ('equipment', ['missing'])], equipment_missing=True)
    add('missing-equipment-vtable-fault', category=0, name=42, info=43, equipment_missing=True)
    for value in (-2147483648, -16777217, 0, 1, 16777217, 2147483647):
        add('pricing-reuse', [('price', [value]), ('good_buy_price', [binary80(0.95)]), ('price', [0]),
                             ('bad_buy_price', [binary80(-1.05)]),
                             ('good_sell_price', [binary80(1.05)]),
                             ('bad_sell_price', [struct.pack('<QH', 0x8000008000000001, 0x3fff)])])
    key_values = [('jump_dist', [-1]), ('name', [123]), ('ids_info', [456]), ('category', ['Equipment']),
                  ('category', ['Ship']), ('equipment', ['alpha']), ('ship', ['beta']),
                  ('shop_archetype', ['Shop']), ('attachment_archetype', ['Attach']),
                  ('HP_child', ['HpChild']), ('combinable', [0x80]), ('alien', ['what']),
                  ('addon', ['alpha', 'HpOne', 2, 'mid']), ('price', [16777217]),
                  ('good_buy_price', [binary80(1.05)])]
    for _ in range(100): add('sequence', [rng.choice(key_values) for j in range(rng.randrange(2, 12))])
    controls = [0x007f | pc | rc for pc in (0, 0x0200, 0x0300) for rc in (0, 0x0400, 0x0800, 0x0c00)]
    if args.quick:
        cases = cases[:50] + [c for c in cases if c[0] in ('addon-all-lists', 'missing-hull-fault', 'duplicate-after-addon', 'addon-unterminated-level-fault')]
        controls = [0x037f]
    counts, failures, total = collections.Counter(), collections.Counter(), 0
    for cw in controls:
        for index, (kind, operations, spec) in enumerate(cases):
            alignment = (0, 1, 3)[index % 3]
            seed, heap_seed = seed_case(alignment)
            results = [run(exports, seed, heap_seed, cw, index % 2) for exports in (orig, new)]
            assert results[0] == results[1], (kind, hex(cw), index,
                [(i, a, b) for i, (a, b) in enumerate(zip(results[0][0], results[1][0])) if a != b][:12],
                [(i, a, b) for i, (a, b) in enumerate(zip(results[0][2], results[1][2])) if a != b][:5],
                results[0][3:6], results[1][3:6])
            independent(results[1], seed, heap_seed, alignment)
            counts[kind] += 1
            if results[0][4]: failures[str(results[0][4])] += 1
            total += 1
    print(f'PASS: {total} paired original/rebuilt block calls; {abi_calls} ABI calls; '
          f'{ownership_calls} destructor calls; {total} independent oracle cases')
    if args.quick:
        print('QUICK DEBUG ONLY: no acceptance report written')
        return
    real_abi_calls, real_ownership_calls = abi_calls, ownership_calls
    assert sum(counts.values()) == total
    assert real_abi_calls == real_ownership_calls == 2 * (total - sum(failures.values()))
    # Negative controls deliberately compile flawed RECONSTRUCTED source outside
    # tracked source. Reuse exactly the same original inputs/service contracts.
    mutations = {
        'normalize_raw_bool': ('byte(good, 0x70, good_block_bool(reader, 0));',
                               'byte(good, 0x70, good_block_bool(reader, 0) != 0);'),
        'wrong_addon_list': ('head_offset = 0xa4;', 'head_offset = 0x98;'),
        'zero_node_padding': ('word(node, 0, reinterpret_cast<u32>(head));',
                             '__builtin_memset(node, 0, 40); word(node, 0, reinterpret_cast<u32>(head));'),
        'skip_duplicate_stop': ('if (good_block_find_good(list, id)) return;',
                                'if (good_block_find_good(list, id)) {}'),
        'safe_missing_hull': ('word(good, 0x90, word(hull, 0x48));',
                              'word(good, 0x90, hull ? word(hull, 0x48) : 0);'),
        'bounded_level_scan': ('while (value[length]) ++length;',
                               'while (length < 63 && value[length]) ++length;'),
    }
    scratch = pathlib.Path(os.environ['TMPDIR']) / 'fla124-block-negative'
    scratch.mkdir(exist_ok=True)
    source = (ROOT / FILES[0]).read_text()
    negative = {}
    probe_cases = [c for c in cases if c[0] in ('bool-raw-al', 'addon-all-lists', 'duplicate-first', 'missing-hull-fault', 'addon-unterminated-level-fault')]
    for i, (label, (before, after)) in enumerate(mutations.items()):
        assert source.count(before) == 1, label
        path = scratch / (label + '.cpp')
        path.write_text(source.replace(before, after))
        mutant_dll = build(path, 'good_block_' + label, 0x19000000 - i * 0x1000000)
        mutant = h.load(mutant_dll)
        mismatch = 0
        # New-side lookup dependencies live at each image's OWN export addresses.
        old_new = new
        new = mutant
        for index, (kind, operations, spec) in enumerate(probe_cases):
            seed, heap_seed = seed_case(index % 4)
            a = run(orig, seed, heap_seed, 0x037f, False)
            b = run(mutant, seed, heap_seed, 0x037f, False)
            if a != b: mismatch += 1
        new = old_new
        assert mismatch, ('Negative control escaped', label)
        negative[label] = {'probe_pairs': len(probe_cases), 'detected_mismatches': mismatch,
                           'dll_sha256': hashlib.sha256(mutant_dll.read_bytes()).hexdigest()}
    p = pefile.PE(str(original))
    original_span = p.get_data(START - p.OPTIONAL_HEADER.ImageBase, END - START)
    # Count original static instructions using objdump; never publish bytes/raw.
    disassembly = subprocess.check_output(['objdump', '-d', '-Mintel', '--start-address=' + hex(START),
                                         '--stop-address=' + hex(END), str(original)], text=True)
    addresses = {int(line.split(':', 1)[0].strip(), 16) for line in disassembly.splitlines()
                 if ':' in line and line.split(':', 1)[0].strip().startswith('627')
                 and len(line.split('\t')) >= 3 and line.split('\t')[2].strip()}
    report = {'status': 'passed', 'scope': 'P1 storage-level whole block control flow with controlled services',
              'original_sha256': ORIGINAL_HASH, 'original_start': hex(START), 'original_end_exclusive': hex(END),
              'original_span_sha256': hashlib.sha256(original_span).hexdigest(),
              'paired_block_calls': total, 'counts': dict(counts), 'x87_controls': [hex(c) for c in controls],
              'real_abi_calls_before_mutations': real_abi_calls,
              'destructor_calls_before_mutations': real_ownership_calls,
              'independent_oracle_cases': total, 'matched_faults': dict(failures),
              'original_executed_instruction_addresses': len(covered), 'original_static_instruction_lines': len(addresses),
              'unexecuted_original_instruction_addresses': [hex(a) for a in sorted(addresses - covered)],
              'negative_controls': negative, 'build_sha256': hashlib.sha256(dll.read_bytes()).hexdigest(),
              'source_hashes': {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in FILES},
              'not_verified': ['Real reader/file/Goods corpus', 'Real CreateID/hash service in this integration',
                  'Real cache allocation/index lookup and Archetype database creation', 'Native Windows/CRT/heap',
                  'Allocation failure/exception unwinding', 'Malformed lists and arbitrary storage/stack aliasing',
                  'Unmasked x87 exceptions/stack exhaustion', 'Whole-function byte identity', 'Full game']}
    (ROOT / 'analysis/good-blockreader-x86-behavior.json').write_text(json.dumps(report, indent=2) + '\n')
    print('NEGATIVE CONTROLS:', json.dumps(negative, sort_keys=True))
    print('ORIGINAL INSTRUCTION COVERAGE:', len(covered), '/', len(addresses))


if __name__ == '__main__':
    main()
