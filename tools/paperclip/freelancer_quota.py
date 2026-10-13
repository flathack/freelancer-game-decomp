#!/usr/bin/python3
"""Paperclip Hermes launcher: Freelancer requires >30% weekly Codex quota left."""
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

HERMES = '/home/hermes/.local/bin/hermes'
INTERVAL = 60

def freelancer(args):
    if not args or args[0] != 'chat':
        return False
    for flag in ('-q', '--query'):
        if flag in args:
            i = args.index(flag)
            if i + 1 < len(args):
                prompt = args[i + 1]
                return ('/opt/data/projects/Freelancer-Decomp' in prompt or
                        'Freelancer: Decompilierung fortführen' in prompt)
    return False

def decision(document):
    if document.get('provider') != 'openai-codex' or document.get('unavailable_reason'):
        return False, None
    windows = [w for w in document.get('windows', [])
               if isinstance(w, dict) and str(w.get('label', '')).casefold() == 'weekly']
    if not windows:
        return False, None
    used = []
    for window in windows:
        value = window.get('used_percent')
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False, None
        if not math.isfinite(value) or not 0 <= value <= 100:
            return False, None
        used.append(value)
    remaining = 100 - max(used)
    return remaining > 30, remaining

def probe():
    try:
        p = subprocess.run([HERMES, 'usage', '--provider', 'openai-codex', '--json'],
                           capture_output=True, text=True, timeout=25)
        if p.returncode:
            return False, None
        return decision(json.loads(p.stdout))
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return False, None

def log(allowed, remaining):
    amount = 'unknown' if remaining is None else f'{remaining:g}%'
    print(f'[freelancer-quota] weekly remaining={amount}; '
          f'{"allowed" if allowed else "blocked"}; requires >30%', flush=True)

def stop(child):
    if child.poll() is not None:
        return
    os.killpg(child.pid, signal.SIGINT)
    try:
        child.wait(timeout=20)
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGTERM)
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()

def process_identity(pid):
    try:
        root = Path('/proc') / str(pid)
        return (root / 'stat').read_text().rsplit(')', 1)[1].split()[19]
    except (OSError, IndexError):
        return None

def watch_existing(pid):
    identity = process_identity(pid)
    try:
        args = (Path('/proc') / str(pid) / 'cmdline').read_bytes().decode().split('\0')
        args = args[args.index('chat'):]
    except (OSError, ValueError):
        return 75
    if not identity or not freelancer(args):
        return 75
    while process_identity(pid) == identity:
        allowed, remaining = probe();log(allowed, remaining)
        if not allowed:
            for sig, grace in ((signal.SIGINT, 20), (signal.SIGTERM, 10), (signal.SIGKILL, 0)):
                if process_identity(pid) != identity:
                    break
                try:
                    os.kill(pid, sig)
                except ProcessLookupError:
                    break
                deadline = time.monotonic() + grace
                while time.monotonic() < deadline and process_identity(pid) == identity:
                    time.sleep(0.5)
            print('[freelancer-quota] Existing decompilation stopped. Files retained.', flush=True)
            return 0
        time.sleep(INTERVAL)
    return 0

def main(args):
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    if len(args) == 2 and args[0] == "--watch-pid":
        return watch_existing(int(args[1]))
    if args == ['--quota-check']:
        allowed, remaining = probe();log(allowed, remaining)
        return 0 if allowed else 75
    if not freelancer(args):
        os.execv(HERMES, [HERMES, *args])
    allowed, remaining = probe();log(allowed, remaining)
    if not allowed:
        print('[freelancer-quota] No model started. Retry on the next routine tick.', flush=True)
        return 0
    child = subprocess.Popen([HERMES, *args], start_new_session=True)
    try:
        while True:
            try:
                return child.wait(timeout=INTERVAL)
            except subprocess.TimeoutExpired:
                allowed, remaining = probe();log(allowed, remaining)
                if not allowed:
                    stop(child)
                    print('[freelancer-quota] Active decompilation stopped. Files retained.', flush=True)
                    return 0
    except (KeyboardInterrupt, SystemExit):
        stop(child)
        return 130
    finally:
        if child.poll() is None:
            stop(child)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
