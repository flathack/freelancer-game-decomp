#!/usr/bin/env python3
"""Validate exported instruction bytes and report remaining executable gaps."""
import argparse,csv,hashlib,json,pathlib
import pefile
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('module'); args=ap.parse_args()
    out=ROOT/'analysis/raw'/args.module
    prov=json.loads((out/'provenance.json').read_text())
    path=ROOT/prov['module']
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if actual!=prov['sha256']: raise ValueError('Original changed')
    pe=pefile.PE(str(path)); base=pe.OPTIONAL_HEADER.ImageBase
    instructions=0; orphan_bytes=0; previous_end=0; orphan_starts=[]; last_orphan_end=None
    for r in csv.DictReader((out/'instructions.tsv').open(),delimiter='\t'):
        address=int(r['address'],16); data=bytes.fromhex(r['bytes'])
        if pe.get_data(address-base,len(data))!=data: raise ValueError(f'Wrong bytes at {address:x}')
        if address<previous_end: raise ValueError('Overlapping instruction export')
        previous_end=address+len(data); instructions+=1
        if not r['function']:
            orphan_bytes+=len(data)
            if last_orphan_end!=address: orphan_starts.append(r['address'])
            last_orphan_end=address+len(data)
        else: last_orphan_end=None
    gaps=[]
    for r in csv.DictReader((out/'unclassified-executable.tsv').open(),delimiter='\t'):
        address=int(r['start'],16); size=int(r['length']); data=pe.get_data(address-base,size)
        if len(data)!=size: raise ValueError('Gap beyond file-backed bytes')
        category='padding_candidate' if data and set(data)<=set([0,0x90,0xcc]) else 'needs_analysis'
        gaps.append(dict(start=r['start'],end=r['end'],bytes=size,category=category,sha256=hashlib.sha256(data).hexdigest()))
    report=dict(original_sha256=actual,instruction_rows_verified=instructions,
                instruction_bytes_outside_functions=orphan_bytes,orphan_run_starts=orphan_starts,
                unclassified_bytes=sum(g['bytes'] for g in gaps),
                padding_candidate_bytes=sum(g['bytes'] for g in gaps if g['category']=='padding_candidate'),
                other_unclassified_bytes=sum(g['bytes'] for g in gaps if g['category']=='needs_analysis'),
                full_function_discovery_proven=False,gaps=gaps)
    (out/'coverage-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['gaps','orphan_run_starts']},indent=2))
if __name__=='__main__': main()
