"""Render several scenes' Blender layers one after another (resumable).

usage: python3 render_queue.py s02_setting s06_rig ...
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.join(os.path.dirname(HERE), 'build', 'logs')

if __name__ == '__main__':
    os.makedirs(LOGS, exist_ok=True)
    for sid in sys.argv[1:]:
        t0 = time.time()
        with open(os.path.join(LOGS, sid + '.log'), 'a') as log:
            subprocess.run(['nice', '-n', '10', sys.executable, os.path.join(HERE, 'run_blender.py'),
                            sid], stdout=log, stderr=subprocess.STDOUT)
        print(f'{sid} done in {(time.time() - t0) / 60:.1f} min', flush=True)
