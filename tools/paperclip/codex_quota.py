#!/usr/bin/python3
"""Codex CLI counterpart of the Freelancer Hermes weekly-quota launcher."""
import os,signal,subprocess,sys
import freelancer_quota as gate
CODEX='/home/hermes/.paperclip/cli/current/node_modules/.bin/codex'
def scoped(args,prompt,cwd):
    return ('exec' in args and ('Freelancer' in prompt or 'Freelancer-Decomp' in cwd))
def main(args):
    signal.signal(signal.SIGTERM,lambda *_:sys.exit(143))
    prompt=sys.stdin.buffer.read() if 'exec' in args and '-' in args else None
    text=prompt.decode('utf-8',errors='replace') if prompt is not None else ' '.join(args)
    protected=scoped(args,text,os.getcwd())
    if protected:
        allowed,remaining=gate.probe();gate.log(allowed,remaining)
        if not allowed:return 75
    child=subprocess.Popen([CODEX,*args],stdin=subprocess.PIPE if prompt is not None else None,start_new_session=True)
    if prompt is not None:
        try:child.stdin.write(prompt);child.stdin.close()
        except BrokenPipeError:pass
    try:
        while True:
            try:return child.wait(timeout=gate.INTERVAL)
            except subprocess.TimeoutExpired:
                if protected:
                    allowed,remaining=gate.probe();gate.log(allowed,remaining)
                    if not allowed:gate.stop(child);return 75
    finally:
        if child.poll() is None:gate.stop(child)
if __name__=='__main__':raise SystemExit(main(sys.argv[1:]))
