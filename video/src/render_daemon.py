"""Background render daemon: renders scenes listed in build/queue.txt.

Append scene ids to build/queue.txt to schedule them; finished ids go to
build/done.txt. Up to RENDER_JOBS Blender processes run at once (a single
Workbench render does not saturate all cores). A line 'STOP' ends the daemon
once the queue is drained.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(os.path.dirname(HERE), 'build')
QUEUE = os.path.join(BUILD, 'queue.txt')
DONE = os.path.join(BUILD, 'done.txt')
LOGS = os.path.join(BUILD, 'logs')
MAX_JOBS = int(os.environ.get('RENDER_JOBS', '2'))


def read(path):
    if not os.path.exists(path):
        return []
    return [ln.strip() for ln in open(path) if ln.strip()]


def blender_count():
    out = subprocess.run(['pgrep', '-f', 'run_blende[r].py'], capture_output=True, text=True)
    return len(out.stdout.split())


if __name__ == '__main__':
    os.makedirs(LOGS, exist_ok=True)
    running = {}
    while True:
        for sid, (proc, t0, log) in list(running.items()):
            rc = proc.poll()
            if rc is not None:
                log.close()
                with open(DONE, 'a') as fh:
                    fh.write(sid + ('\n' if rc == 0 else '_FAILED\n'))
                print(f'{sid} rc={rc} in {(time.time() - t0) / 60:.1f} min', flush=True)
                del running[sid]
        queue, done = read(QUEUE), set(read(DONE))
        todo = [q for q in queue if q not in done and q != 'STOP' and q not in running]
        if not todo and not running and 'STOP' in queue:
            break
        if todo and blender_count() < MAX_JOBS:
            sid = todo[0]
            log = open(os.path.join(LOGS, sid + '.log'), 'a')
            proc = subprocess.Popen(['nice', '-n', '10', sys.executable,
                                     os.path.join(HERE, 'run_blender.py'), sid],
                                    stdout=log, stderr=subprocess.STDOUT)
            running[sid] = (proc, time.time(), log)
            print(f'started {sid}', flush=True)
            time.sleep(5)
            continue
        time.sleep(15)
