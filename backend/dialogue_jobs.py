"""Non-blocking, single-slot Exodia dialogue queue.

A game bargain is committed before narration; cancellation never rolls back money.
Only one Exodia browser task is ever submitted at a time for this local game.
"""
from __future__ import annotations

import os
import inspect
import threading
import time
import uuid
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

from .brain import offline_flavor
from .exodia import ExodiaClient, ExodiaError, DEPARTURE_CLAIM
from .trade_dialogue import assemble_trade_dialogue


class DialogueJobs:
    def __init__(self):
        self.lock = threading.RLock()
        self.jobs: OrderedDict[str, dict] = OrderedDict()
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='exodia-shop')

    def close(self):
        self.pool.shutdown(wait=False, cancel_futures=True)

    def start(self, game, session_id: str, scene: dict, snapshot: dict) -> dict:
        with self.lock:
            # The previous active response should never coexist with a new task.
            for j in self.jobs.values():
                if j['session_id'] == session_id and j['status'] in ('queued', 'working'):
                    j['_stop'].set()
            job_id = uuid.uuid4().hex
            info = {'id': job_id, 'session_id': session_id, 'turn': snapshot['turn'],
                    'status': 'queued', 'response': None, 'error': None,
                    'created_at': time.time(), 'early_sentence': '', '_stop': threading.Event()}
            self.jobs[job_id] = info
            while len(self.jobs) > 150:
                oldest = next(iter(self.jobs))
                if self.jobs[oldest]['status'] in ('queued', 'working'):
                    break
                self.jobs.pop(oldest)
            self.pool.submit(self._run, game, info, scene, snapshot)
            return {'job_id': job_id, 'status': 'queued', 'turn': snapshot['turn'],
                    'scene': game.public(snapshot, '', scene['mood'], scene['gesture'],
                                         event=scene['event'], transaction=scene['transaction'])}

    def _run(self, game, job, scene, snapshot):
        stopped = job['_stop']
        with self.lock:
            if stopped.is_set():
                job['status'] = 'cancelled'
                return
            job['status'] = 'working'
        used_ai = False
        error = None
        metrics = {'input_chars': len(scene.get('user_text', ''))}
        def publish_early(sentence: str):
            with self.lock:
                if not stopped.is_set() and job['status'] == 'working':
                    job['early_sentence'] = sentence

        try:
            client = ExodiaClient()
            try:
                if 'on_early_sentence' in inspect.signature(client.synthesize).parameters:
                    flavor = client.synthesize(scene, snapshot, stopped, on_early_sentence=publish_early)
                else:
                    flavor = client.synthesize(scene, snapshot, stopped)
                used_ai = True
                metrics = dict(getattr(client, 'metrics', {}))
            finally:
                client.close()
        except InterruptedError:
            with self.lock:
                job['status'] = 'cancelled'
            return
        except (ExodiaError, ValueError) as exc:
            error = str(exc)[:160]
            flavor = offline_flavor(scene, snapshot)
        except Exception:
            # Do not expose unexpected internal stack traces or provider data to players.
            error = 'Exodia adapter unexpected exception; server log has technical cause'
            flavor = offline_flavor(scene, snapshot)
        with self.lock:
            if stopped.is_set():
                job['status'] = 'cancelled'
                return
            metrics['elapsed_ms'] = round((time.time()-job['created_at'])*1000)
            metrics['model_output_chars'] = len(flavor)
            if not flavor.startswith(job.get('early_sentence', '')):
                job['early_sentence'] = ''
            metrics['source'] = 'exodia_live' if used_ai else 'offline_fallback'
            job['metrics'] = metrics
            # NPC may genuinely walk out. A declared departure is translated
            # to an authoritative game event before we narrate it. No new offer.
            if (used_ai and scene['event'] not in ('walkout','deal','social_offer','social_refused','social_declined','social_terms_changed')
                    and DEPARTURE_CLAIM.search(flavor)):
                game.apply_npc_departure(job['session_id'],snapshot['turn'],scene)
            line, narration_mode = assemble_trade_dialogue(flavor, scene)
            # The AI may add personality, never rewrite an accepted bid or a
            # side-deal ruling. Report the actual source of the delivered text.
            metrics['narration_mode'] = narration_mode
            metrics['output_chars'] = len(line)
            metrics['source'] = ('exodia_live' if used_ai and narration_mode in ('model','model_repaired')
                                 else 'game_authoritative' if used_ai else 'offline_fallback')
            # Finalize only the accepted active AI turn; never leak late answers into history.
            response = game.finalize(job['session_id'], line, scene, used_ai)
            response['ai_mode'] = 'exodia' if used_ai else 'offline_fallback'
            response['performance'] = metrics
            job['response'] = response
            job['status'] = 'answered'
            job['error'] = error
            job['source'] = metrics['source']

    def cancel_session(self, session_id: str):
        with self.lock:
            for job in self.jobs.values():
                if job['session_id'] == session_id and job['status'] in ('queued', 'working'):
                    job['_stop'].set()

    def get(self, job_id: str) -> dict | None:
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return None
            if job['_stop'].is_set():
                return {'job_id': job_id, 'state': 'cancelled', 'response': None}
            return {'job_id': job_id, 'state': job['status'], 'response': job['response'],
                    'error': job['error'], 'source': job.get('source','pending'),
                    'metrics': job.get('metrics', {}),
                    'early_sentence': job.get('early_sentence', '') if job['status'] == 'working' else ''}
