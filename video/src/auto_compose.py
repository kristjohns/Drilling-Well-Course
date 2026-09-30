"""Compose scene segments automatically as soon as their frames are rendered."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build  # noqa: E402
import scene_base  # noqa: E402

if __name__ == '__main__':
    ids = scene_base.all_ids()
    while True:
        missing = [s for s in ids if not os.path.exists(build.seg_path(s))]
        if not missing:
            print('all segments composed', flush=True)
            break
        did = False
        for sid in missing:
            k = ids.index(sid)
            ready = build.frames_complete(sid) and (k == 0 or build.frames_complete(ids[k - 1]))
            if ready:
                import compose
                compose.compose(sid)
                did = True
                break
        if not did:
            time.sleep(60)
