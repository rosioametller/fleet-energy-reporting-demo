# Static inspection of this independent release; never print matched values.
import ast
import json
from pathlib import Path
import re
import struct

ROOT=Path(__file__).resolve().parents[1]
SKIP={'.git','.venv','.qa','.local-state','__pycache__'}

def candidate_paths():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(s in SKIP for s in p.relative_to(ROOT).parts))

def inspect_tree():
    findings=[]
    patterns={
        'PERSONAL_ABSOLUTE_PATH':r'(?i)[A-Z]:[/\\]+Users[/\\]+',
        'EMAIL_LITERAL':r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',
        'PRIVATE_KEY_MATERIAL':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
        'TOKEN_LIKE_LITERAL':r'\b(?:ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16})\b',
    }
    for p in candidate_paths():
        rel=p.relative_to(ROOT).as_posix()
        if p.name.startswith(('.env','cookies','storage_state','auth.')) or p.suffix.lower() in {'.sqlite','.sqlite3','.db','.xlsx','.xlsm','.pbix','.zip','.pyc'}:
            findings.append(dict(file=rel,line=1,type='UNEXPECTED_ARTIFACT'))
        if p.suffix=='.png':
            raw=p.read_bytes();offset=8
            while offset+12<=len(raw):
                size=struct.unpack('>I',raw[offset:offset+4])[0];kind=raw[offset+4:offset+8]
                if kind in {b'tEXt',b'iTXt',b'zTXt'}:findings.append(dict(file=rel,line=1,type='IMAGE_METADATA_REQUIRES_REVIEW'))
                offset+=size+12
            continue
        if p.suffix not in {'.py','.js','.css','.html','.json','.md','.txt','.cmd'} and p.name not in {'.gitignore','LICENSE'}:
            findings.append(dict(file=rel,line=1,type='UNEXPECTED_FILE_TYPE'));continue
        data=p.read_text(encoding='utf-8')
        for n,line in enumerate(data.splitlines(),1):
            for kind,pattern in patterns.items():
                if re.search(pattern,line):findings.append(dict(file=rel,line=n,type=kind))
            for address in re.findall(r'https?://[^\s\"\'<>]+',line):
                from urllib.parse import urlsplit
                # Source f-strings may contain bracketed expressions in the port.
                literal=re.sub(r'\{[^{}]*\}', '0', address)
                try:host=urlsplit(literal).hostname
                except ValueError:
                    findings.append(dict(file=rel,line=n,type='URL_EXPRESSION_REQUIRES_REVIEW'));continue
                if host and host not in {'127.0.0.1','127.0.0.2','localhost'}:
                    findings.append(dict(file=rel,line=n,type='NONLOCAL_URL_REQUIRES_REVIEW'))
    seed=json.loads((ROOT/'datos_demo/seed.json').read_text(encoding='utf-8'))
    if not all(re.fullmatch(r'DEMO-9\d\d',u['plate']) and u['internal_key'].startswith('LAB-7') for u in seed['units']):
        findings.append(dict(file='datos_demo/seed.json',line=1,type='SYNTHETIC_SEED_MISMATCH'))
    return dict(files=len(candidate_paths()),findings=findings,scope='Only candidate source, documentation and original screenshots; excludes generated state and dependencies',
        limitations='Static patterns and source review are complementary; no guarantee for arbitrary future additions.')

if __name__=='__main__':
    result=inspect_tree();output=ROOT/'.qa/release-inspection.json';output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(files=result['files'],findings=result['findings']),ensure_ascii=True))
    raise SystemExit(1 if result['findings'] else 0)
