#!/usr/bin/env python3
"""Validate saved real FLA-263 executions; never synthesize test executions.
This is a provenance/coverage audit, not another differential or native run.
The unchanged FLA-255 acceptance matrix is referenced, not rewritten.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import pefile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'analysis/fla263'
SCOPE = 'c93583dcdca63e257d9a18dd9d51aa62905f5042'
COMMON = 'e6c08a7cfdfc5cf8c5d00047cc0b5e361bcaf31cdd91fe89f384d5920dd8c483'
OWN = '638ddb21e3aba145148a4d702f532cf4c973d2196d4c03cdcdb934de2880b3c7'
COMM = 'd63770aa1c5dd10be3df06ed90443789602a8b1c8230c980108ee0fbe585d22c'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((DATA / name).read_text())


def main():
    assert digest(ROOT / 'src/archetype_ownership.cpp') == OWN
    assert digest(ROOT / 'src/good_info_comm.cpp') == COMM
    original = ROOT / 'original/_FL Fresh Install-deutsch/EXE/common.dll'
    assert digest(original) == COMMON
    manifest = json.loads((ROOT / 'analysis/fla255/original-evidence.json').read_text())
    image = pefile.PE(str(original))
    spans = []
    for function in manifest['functions']:
        for span in function['half_open_spans']:
            start = int(span['start_va'], 16)
            end = int(span['end_va_exclusive'], 16)
            actual = image.get_data(start-image.OPTIONAL_HEADER.ImageBase, end-start)
            assert hashlib.sha256(actual).hexdigest() == span['sha256'], span
            spans.append({'entry': function['entry_va'], 'start': span['start_va'],
                          'end_exclusive': span['end_va_exclusive'], 'sha256': span['sha256']})
    base_paths = subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', SCOPE, '--', 'src', 'tests', 'analysis'],
        cwd=ROOT, text=True).splitlines()
    preserved = [p for p in base_paths if p.startswith(('src/', 'tests/', 'analysis/fla255/'))
                 or (p.startswith('analysis/') and p.count('/') == 1 and p.endswith('.json'))]
    unchanged = subprocess.run(['git', 'diff', '--exit-code', SCOPE, '--', *preserved],
                               cwd=ROOT, capture_output=True, text=True)
    assert unchanged.returncode == 0, unchanged.stdout
    # New implementation/evidence files may now be tracked; only pinned base
    # paths above must stay unchanged before AND after the candidate commit.
    executions = read('execution-current.json')['runs']
    expected = {'verify_archetype_lifecycle_x86.py', 'verify_archetype_ownership_x86.py',
                'verify_archetype_ownership_defects_x86.py', 'verify_archetype_ownership_edges_x86.py'}
    assert {Path(r['argv'][1]).name for r in executions} == expected
    logs = {}
    for execution in executions:
        assert execution['exit_code'] == 0
        test = Path(execution['argv'][1])
        assert digest(test) == execution['test_sha256']
        log = Path(execution['log'])
        assert log.is_file()
        logs[str(log.relative_to(ROOT))] = digest(log)
    owner = read('ownership-verification.json')
    lifetime = read('lifecycle-verification.json')
    edges = read('ownership-edges.json')
    defects = read('ownership-defects.json')
    comm = read('comm-verification.json')
    for report in (owner, lifetime, edges, comm):
        assert report['original_sha256'] == COMMON
        assert report['native_runs'] == 0
        assert report.get('faults_counted_as_returns', 0) == 0
        assert all(c['exit_code'] == 0 for c in report['commands'])
    for report in (lifetime, edges, defects):
        assert report['source_sha256'] == OWN
    assert comm['source_sha256'] == COMM
    assert comm['test_sha256'] == digest(ROOT / 'tests/verify_good_info_comm_x86.py')
    comm_log = ROOT / 'build/fla263-comm/final-run.log'
    assert json.loads(comm_log.read_text()) == comm
    logs[str(comm_log.relative_to(ROOT))] = digest(comm_log)
    for name, report in (('ownership-verification.json', owner),
                         ('lifecycle-verification.json', lifetime),
                         ('ownership-edges.json', edges)):
        test = {'ownership-verification.json': 'verify_archetype_ownership_x86.py',
                'lifecycle-verification.json': 'verify_archetype_lifecycle_x86.py',
                'ownership-edges.json': 'verify_archetype_ownership_edges_x86.py'}[name]
        record = next(r for r in executions if Path(r['argv'][1]).name == test)
        last = Path(record['log']).read_text().splitlines()[-1]
        assert json.loads(last)['counts'] == report['counts']
    controls = defects['compiled_defects'] + comm['compiled_defects']
    assert len(controls) == 19
    assert all(d['compiled'] and d['rejected'] for d in controls)
    for defect in defects['compiled_defects']:
        assert all(c['exit_code'] == 0 for c in defect['commands'])
    regression_records = []
    for name in ('regression-verification.json', 'regression-supplemental-verification.json'):
        report = read(name)
        assert report['all_commands_exit_zero'] and report['published_reports_preserved']
        assert report['quick_runs'] == 0
        for test, sha in report['test_hashes'].items():
            assert digest(ROOT / 'tests' / test) == sha
        for record in report['full_suites']:
            assert record['exit_code'] == 0
            log = Path(record['output_file'])
            assert log.is_file()
            logs[str(log.relative_to(ROOT))] = digest(log)
        regression_records += report['full_suites']
    assert len(regression_records) == 20
    assert len({r['suite'] for r in regression_records}) == 20
    groups = {}
    for name, report in (('ownership', owner), ('lifecycle', lifetime), ('edges', edges)):
        groups[name] = {'regular_pairs': sum(v for k, v in report['counts'].items() if 'fault' not in k),
                        'fault_pairs': sum(v for k, v in report['counts'].items() if 'fault' in k)}
    groups['callback'] = {'regular_pairs': comm['normal_pairs'], 'fault_pairs': comm['fault_pairs']}
    totals = {k: sum(g[k] for g in groups.values()) for k in ('regular_pairs', 'fault_pairs')}
    assert totals == {'regular_pairs': 13317, 'fault_pairs': 66}
    mapping = {
        'N01': ['ownership.run: 9216 constructor pairs, all 256 low bytes, four alignments, three seeds', 'lifecycle.alignment_cases'],
        'N02': ['ownership.run: Root/Equipment/Attached constructors and intermediate vptr writes', 'lifecycle.alignment_cases'],
        'N03': ['ownership.run: 1620 populated assignment pairs, destination sizes 0/1/3; source 0/1/3/7', 'lifecycle.copy_cases: 180 copies, source sizes 0/1/2/7'],
        'N04': ['lifecycle.self_cases: 54 self-assignment pairs', 'ownership.run: null/same/different clients and alias inheritance'],
        'N05': ['ownership.run: 900 matched inherit pairs including all 26 arms and out-of-range values; 90 mismatch pairs', 'frozen CLASS_FIELDS and field_oracle'],
        'N06': ['ownership.run: independent exact client slot0/4/28 event order, target nickname/client restoration', 'lifecycle.copy_cases: release-before-addref'],
        'N07': ['lifecycle.reader_cases: 36 real reader/query/inherit pairs, missing/null/valid and base/subtype getter semantics', 'edges.unsigned_query: 21 unsigned exact-match cases'],
        'N08': ['ownership.run: 120 standalone vector pairs', 'edges.subtype_vectors: 240 populated Root/subtype-vector pairs with reuse/growth/self and poisoning'],
        'N09': ['comm.paired: 384 direct/slot callback pairs, null/empty/1/62/63/64/255/8191 and unknown keys', 'lifecycle.lifecycle_cases: mixed-case and repeated callbacks through reconstructed P1 and production GoodInfo tables'],
        'N10': ['comm.paired: 24 unterminated-source faults, exact address/access/size and pre-fault bytes', 'compiled bounded_scan control rejected; full late NUL at length8191'],
        'N11': ['lifecycle.destroy_cases: 72 copy/destroy-order pairs and 162 scalar/cookie deleting RET4 pairs', 'allocation/free and client/payload event order; explicit modeled CRT array iterator'],
        'N12': ['lifecycle.lifecycle_cases: 72 poisoned-heap read/copy/lookup/P1/callback/destroy cycles with alternating destruction order and varying seeds'],
        'N13': ['lifecycle.x87_cases: 108 live binary80/CW/SW/tag preservation and raw signed-zero/NaN copy pairs', 'full unchanged P1/P2 control-word and binary80 discriminator baselines'],
        'N14': ['lifecycle.failure_cases: 6 null allocator and 6 client faults', 'edges.failure_edges: 18 copy allocator faults, 6 actual nullallocator returns, 12 inherit/destroy client faults; no native SEH claim'],
        'N15': ['13 unchanged full baseline suites plus 7 supplemental dependency/lookup suites, all exit0, no quick runs', '35 exact denial spans actually probed; 19 compiled behavioral controls rejected'],
    }
    matrix = json.loads((ROOT / 'analysis/fla255/acceptance-matrix.json').read_text())
    required = [r['id'] for r in matrix['cases'] if r['stage'] == 'next_kernel']
    assert set(required) == set(mapping)
    assert len(lifetime['denial_spans_actually_probed']) == 35
    assert lifetime['actual_entry_abi_returns_by_side']['original'] == lifetime['actual_entry_abi_returns_by_side']['rebuilt']
    report = {
        'issue': 'FLA-263', 'scope_commit': SCOPE, 'audit_kind': 'saved-real-execution-provenance',
        'original_sha256': COMMON, 'verified_original_spans': spans,
        'source_sha256': {'src/archetype_ownership.cpp': OWN, 'src/good_info_comm.cpp': COMM},
        'test_and_runtime_sha256': {str(p.relative_to(ROOT)): digest(p) for p in
            sorted((ROOT / 'tests').glob('*fla263*')) +
            sorted((ROOT / 'tests').glob('verify_archetype_ownership*.py')) +
            [ROOT / 'tests/verify_archetype_lifecycle_x86.py', ROOT / 'tests/verify_good_info_comm_x86.py',
             ROOT / 'tests/fixtures/archetype_ownership_runtime.cpp', ROOT / 'tests/fixtures/good_info_comm_runtime.cpp']},
        'log_sha256': logs, 'groups_not_additive_coverage_percentage': groups, 'totals': totals,
        'baseline_suites': len(regression_records), 'compiled_controls_rejected': len(controls),
        'abi_returns_lifecycle_by_side': lifetime['actual_entry_abi_returns_by_side'],
        'destructor_returns': lifetime['destructor_return_convention'],
        'faults_counted_as_returns': 0, 'native_runs': 0,
        'acceptance': [{'id': key, 'status': 'evidence_ready_for_independent_review', 'evidence': mapping[key]} for key in required],
        'modeled_services': sorted(set(owner['modeled_services'] + lifetime['modeled_services'] + comm['modeled_services'])),
        'limits': ['P01-P08/W01 and P1 malformed 0x06270e80/0x06270ef5/0x06270f51 remain open.',
                   'No real DB/Factories/LoadEquipment/Ships/Hulls or complete Goods file loader.',
                   'No native Windows/CRT/SEH/unmasked x87 or universal corruption/overlap guarantees.',
                   'This audit validates recorded executions; it does not rerun differential cases.',
                   'Athena independently rederives expectations at a fixed implementation commit; Apollo approval/integration still pending.'],
        'milestone_approved': False,
    }
    (DATA / 'acceptance-evidence.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'provenance_audit': 'PASS', 'acceptance_rows': len(required),
                      'totals': totals, 'full_baseline_suites': len(regression_records),
                      'compiled_controls_rejected': len(controls), 'original_spans_verified': len(spans),
                      'review_and_approval': 'pending'}))


if __name__ == '__main__':
    main()
