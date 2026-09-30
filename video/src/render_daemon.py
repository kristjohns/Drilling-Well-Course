"""Background render daemon: renders scenes listed in build/queue.txt, one at a time.

Append scene ids to build/queue.txt to schedule them; finished ids go to
build/done.txt. A line 'STOP' ends the daemon once the queue is drained.
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


def read(path):
    if not os.path.exists(path):
        return []
    return [ln.strip() for ln in open(path) if ln.strip()]


def other_blender_running():
    out = subprocess.run(['pgrep', '-f', 'run_blende[r].py'], capture_output=True, text=True)
    return bool(out.stdout.strip())


if __name__ == '__main__':
    os.makedirs(LOGS, exist_ok=True)
    while True:
        queue, done = read(QUEUE), set(read(DONE))
        todo = [q for q in queue if q not in done and q != 'STOP']
        if not todo:
            if 'STOP' in queue:
                break
            time.sleep(20)
            continue
        if other_blender_running():
            time.sleep(20)
            continue
        sid = todo[0]
        t0 = time.time()
        with open(os.path.join(LOGS, sid + '.log'), 'a') as log:
            r = subprocess.run(['nice', '-n', '10', sys.executable,
                                os.path.join(HERE, 'run_blender.py'), sid],
                               stdout=log, stderr=subprocess.STDOUT)
        with open(DONE, 'a') as fh:
            fh.write(sid + ('\n' if r.returncode == 0 else '_FAILED\n'))
        print(f'{sid} rc={r.returncode} in {(time.time() - t0) / 60:.1f} min', flush=True)
