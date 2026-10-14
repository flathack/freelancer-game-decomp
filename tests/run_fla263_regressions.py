#!/usr/bin/env python3
"""Run full published P1/P2/lookup regressions without changing their reports.
Each command and actual output is saved privately under build/fla263-regression.
No quick flags; no mock results; the existing published report bytes are restored.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
SUITES = [
    'verify_good_block_reader_x86.py',
    'verify_archetype_metadata_x86.py',
    'verify_archetype_metadata_coupled_x86.py',
    'verify_good_info_price_x86.py',
    'verify_archetype_lookup_x86.py',
    'verify_good_info_initialize_x86.py',
    'verify_good_info_destroy_x86.py',
    'verify_good_info_copy_x86.py',
    'verify_good_info_assign_x86.py',
    'verify_good_info_list_initialize_x86.py',
    'verify_good_index_lookup_x86.py',
    'verify_good_id_lookup_x86.py',
    'verify_nickname_id_access_x86.py',
]


SUPPLEMENTAL = [
    'verify_good_archetype_x86.py',
    'verify_good_index_emplace_x86.py',
    'verify_flid_x86.py',
    'verify_create_id.py',
    'verify_string_cache_x86.py',
    'verify_string_index_x86.py',
    'verify_subobject_id_x86.py',
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--supplemental', action='store_true',
                        help='Run missing dependency/lookup suites; preserve the 13-suite report.')
    args = parser.parse_args()
    suites = SUPPLEMENTAL if args.supplemental else SUITES
    suffix = '-supplemental' if args.supplemental else ''
    dest = ROOT / ('build/fla263-regression' + suffix)
    dest.mkdir(parents=True, exist_ok=True)
    before = {p: p.read_bytes() for p in (ROOT / 'analysis').glob('*.json')}
    env = dict(os.environ)
    env['PATH'] = str(ROOT / '.tools/bin') + os.pathsep + env['PATH']

    def run(name):
        command = [str(ROOT / '.venv/bin/python'), str(ROOT / 'tests' / name)]
        started = time.time()
        with (dest / (name + '.log')).open('wb') as output:
            result = subprocess.run(command, cwd=ROOT, env=env, stdout=output,
                                    stderr=subprocess.STDOUT, timeout=1800)
        return {'suite': name, 'argv': command, 'exit_code': result.returncode,
                'seconds': round(time.time() - started, 3),
                'output_file': str(dest / (name + '.log'))}

    records = []
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(run, name) for name in suites]
            for future in concurrent.futures.as_completed(futures):
                record = future.result()
                records.append(record)
                print(json.dumps(record), flush=True)
                (dest / 'execution-records.json').write_text(json.dumps(records, indent=2)+'\n')
    finally:
        for path, data in before.items():
            now = path.read_bytes()
            if now != data:
                (dest / path.name).write_bytes(now)
                path.write_bytes(data)
        for path in (ROOT / 'analysis').glob('*.json'):
            if path not in before:
                (dest / path.name).write_bytes(path.read_bytes())
                path.unlink()
    records.sort(key=lambda r: r['suite'])
    report = {'issue': 'FLA-263', 'full_suites': records, 'quick_runs': 0,
              'all_commands_exit_zero': len(records)==len(suites) and all(r['exit_code']==0 for r in records),
              'published_reports_preserved': all(p.read_bytes()==b for p,b in before.items()),
              'test_hashes': {n:hashlib.sha256((ROOT/'tests'/n).read_bytes()).hexdigest() for n in suites},
              'limits': ['Published baseline suites retain their own explicitly modeled services.',
                         'New ownership/callback acceptance is separately tested, not inferred from these baselines.']}
    target = ROOT / ('analysis/fla263/regression' + suffix + '-verification.json')
    target.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'report':str(target),'passed':report['all_commands_exit_zero']}),flush=True)
    return 0 if report['all_commands_exit_zero'] and report['published_reports_preserved'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
