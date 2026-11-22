#!/usr/bin/env python3
"""Non-recording PCM timing check for the user's actual Hermes Mac server.

Call the SAME /stream request shape as the Godot game, report timing only.
No recordings, API keys, transcripts, or conversation data are saved.
Run when no other Hermes jobs are in progress.
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
import httpx

ROOT = Path(__file__).resolve().parent.parent


def main(argv=None):
    ap=argparse.ArgumentParser(description='Compare Hermes streamed PCM speed with in-game F5 voice diagnostics')
    ap.add_argument('--url', default='http://10.0.0.129:8000')
    ap.add_argument('--profile', default='f01_sakura_genki')
    ap.add_argument('--engine', choices=('qwen','kokoro','chatterbox'), default='qwen')
    ap.add_argument('--repetitions', type=int, default=3)
    ap.add_argument('--text', default='What a lovely surprise! That is a fair bargain. I am delighted to see you again.')
    args=ap.parse_args(argv)
    parsed=urlparse(args.url)
    if parsed.scheme!='http' or parsed.path not in ('','/'):
        ap.error('Use a direct local Hermes http://host:port URL')
    if args.repetitions not in range(1,7):
        ap.error('Repetitions must be between 1 and 6')
    manifest=json.loads((ROOT/'godot/assets/hermes_profile_manifest.json').read_text('utf-8'))
    preset=manifest.get(args.profile)
    if not preset:
        ap.error('Unknown Hermes profile: '+args.profile)
    voice=args.profile if args.engine=='chatterbox' else str(preset['qwen' if args.engine=='qwen' else 'kokoro'])
    payload={'engine':args.engine,'voice':voice,'input':args.text,'mood':'neutral',
             'instruct':preset['instruct'],'archetype':'female_warm',
             'speed':1.0,'pitch_shift':0.0,'temperature':0.45,
             'repetition_penalty':1.3,'streaming_interval':0.5,'stream_chunk_min':85}
    print(f'Profile {args.profile} | {args.engine}/{voice} | speed 1.0 | pitch 0 | {len(args.text)} chars')
    print('Compare these PCM durations with the same line generated in Hermes Studio and F5 in the game.')
    with httpx.Client(timeout=httpx.Timeout(180.0, connect=6.0)) as client:
        for run in range(1,args.repetitions+1):
            started=time.perf_counter()
            try:
                with client.stream('POST',args.url.rstrip('/')+'/stream',json=payload) as response:
                    response.raise_for_status()
                    rate=int(response.headers.get('X-Sample-Rate','24000'))
                    if not 8000<=rate<=192000:raise ValueError('Invalid X-Sample-Rate')
                    first=None
                    samples=0
                    for chunk in response.iter_bytes():
                        if chunk and first is None:first=time.perf_counter()
                        samples+=len(chunk)
                    elapsed=time.perf_counter()-started
                    seconds=samples/2/rate
                    print(f'#{run} PCM={seconds:.2f}s first_packet={(first-started if first else 0):.2f}s wall={elapsed:.2f}s rate={rate}Hz underrun_inference=not_measured model={response.headers.get("X-Model-Id","unknown")} run={response.headers.get("X-Run-Id","unknown")}')
            except (httpx.HTTPError,ValueError) as exc:
                print(f'#{run} ERROR {type(exc).__name__}: {str(exc)[:160]}',file=sys.stderr)
                return 1
    return 0

if __name__=='__main__':
    raise SystemExit(main())
