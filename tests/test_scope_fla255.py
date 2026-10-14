#!/usr/bin/env python3
"""Scope evidence checks only. These do NOT execute reconstructed game code."""
import importlib.util
import json
import pathlib
import struct
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('scope_fla255', ROOT/'tools/scope_fla255.py')
SCOPE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(SCOPE)


class InventoryChecks(unittest.TestCase):
    def test_text_order_and_repeated_keys_are_retained(self):
        fmt, sections = SCOPE.read_sections(b'[Light]\nnickname = local\ninherit = a\ninherit = b\n[Good]\naddon = one\naddon = two\n')
        self.assertEqual(fmt, 'TEXT-cp1252')
        self.assertEqual(sections, [('Light',['nickname','inherit','inherit']),('Good',['addon','addon'])])

    def test_binary_sections_and_zero_values(self):
        strings = b'Good\0inherit\0Light\0'
        entries = struct.pack('<HH',0,1)+struct.pack('<HB',5,0)+struct.pack('<HH',13,0)
        fmt, sections = SCOPE.read_sections(b'BINI'+struct.pack('<II',1,12+len(entries))+entries+strings)
        self.assertEqual(fmt, 'BINI-v1')
        self.assertEqual(sections, [('Good',['inherit']),('Light',[])])

    def test_empty_real_binary_file_shape(self):
        self.assertEqual(SCOPE.read_sections(b'BINI'+struct.pack('<II',1,12)), ('BINI-v1',[]))

    def test_invalid_binary_version_is_not_accepted(self):
        with self.assertRaises(ValueError):
            SCOPE.read_sections(b'BINI'+struct.pack('<II',2,12))

    def test_truncated_binary_is_not_counted(self):
        with self.assertRaises((ValueError,struct.error)):
            SCOPE.read_sections(b'BINI'+struct.pack('<II',1,16)+b'\x00\x00\x01\x00')

    def test_nonadjacent_instruction_ranges_stay_separate(self):
        self.assertEqual(SCOPE.segments([(10,12),(12,16),(20,24)]),[[10,16],[20,24]])


class EvidenceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence=json.loads((ROOT/'analysis/fla255/original-evidence.json').read_text())
        cls.matrix=json.loads((ROOT/'analysis/fla255/acceptance-matrix.json').read_text())

    def test_fixed_base_and_anchor_hash(self):
        self.assertEqual(self.evidence['base_commit'],SCOPE.BASE)
        self.assertEqual(self.evidence['original_module']['sha256'],SCOPE.COMMON_SHA)
        entries=[f['entry_va'] for f in self.evidence['functions']]
        self.assertEqual(len(entries),len(set(entries)))
        for f in self.evidence['functions']:
            self.assertEqual(sum(s['bytes'] for s in f['half_open_spans']),f['body_bytes'])
            self.assertTrue(all(len(s['sha256'])==64 for s in f['half_open_spans']))

    def test_all_class_switch_entries_and_separate_table_hash(self):
        table=next(t for t in self.evidence['tables'] if t['name']=='inherit_class_dispatch_table')
        self.assertEqual(len(table['slots']),26)
        self.assertEqual(table['start_va'],'0x062f4170')
        self.assertEqual(table['end_va_exclusive'],'0x062f41d8')
        self.assertEqual(table['sha256'],'90dff599687699450e3d52b953a92721a3cc1bd8a355e288fcfd1a4b02b92d19')
        kernel=self.evidence['proposed_kernel_direct_dependency_closure']
        entries={f['entry_va'] for f in self.evidence['functions']}
        self.assertTrue(set(kernel['body_entries'])<=entries)

    def test_every_acceptance_row_has_oracles_and_is_only_planned(self):
        keys=['id','stage','fixture','original_oracle','reconstruction_oracle','abi_check','independent_expectation','defect_control','status']
        rows=self.matrix['cases']
        self.assertTrue(rows)
        self.assertEqual(len(rows),len({r['id'] for r in rows}))
        for row in rows:
            for key in keys:
                self.assertTrue(row.get(key),(row['id'],key))
            self.assertEqual(row['status'],'planned_not_executed')
        self.assertEqual(self.evidence['real_original_or_reconstructed_loader_cases_executed'],0)

    def test_inventory_is_metadata_only_and_complete_for_config_entries(self):
        inventories=json.loads((ROOT/'analysis/fla255/corpus-inventory.json').read_text())
        self.assertFalse(inventories['contents_uploaded'])
        for corpus in inventories['corpora']:
            self.assertTrue(corpus['available'])
            files=corpus['active_relevant_entries_in_configuration_order']
            self.assertEqual(len(files),15)
            self.assertEqual(corpus['missing_files'],0)
            self.assertEqual([f['configuration_order'] for f in files],list(range(1,16)))
            self.assertFalse(corpus['contents_exported'])
            self.assertTrue(all('content' not in f and 'values' not in f for f in files))


if __name__=='__main__':
    unittest.main()
