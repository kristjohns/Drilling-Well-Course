"""Build a scene in Blender (bpy module), export label anchors, render frames.

usage: python3 run_blender.py <scene_id> [--still F [F ...]] [--no-render] [--aa N]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bl  # noqa: E402
import config as C  # noqa: E402
import scene_base  # noqa: E402


def main():
    args = sys.argv[1:]
    sid = args[0]
    scene = scene_base.load(sid)
    if not scene.BLENDER:
        print(sid, 'has no 3D layer')
        return
    bl.reset(C.FPS)
    bl.setup_workbench(aa=scene.AA)
    t0 = time.time()
    anchors = scene.build() or {}
    print(f'[{sid}] built in {time.time() - t0:.1f}s', flush=True)
    last = scene.nframes + C.HANDLE - 1
    os.makedirs(C.ANCHORS, exist_ok=True)
    bl.export_anchors(os.path.join(C.ANCHORS, sid + '.json'), anchors, 0, last)
    print(f'[{sid}] anchors exported', flush=True)
    out_dir = os.path.join(C.FRAMES, sid)
    if '--still' in args:
        i = args.index('--still') + 1
        frames = []
        while i < len(args) and not args[i].startswith('--'):
            frames.append(int(args[i]))
            i += 1
        os.makedirs(out_dir, exist_ok=True)
        for f in frames:
            bl.render_still(os.path.join(out_dir, '%04d.png' % f), f)
        return
    if '--no-render' in args:
        return
    for a, b in scene.render_ranges():
        t1 = time.time()
        bl.render(out_dir, a, b)
        n = b - a + 1
        print(f'[{sid}] rendered {a}-{b} ({n} frames) in {time.time() - t1:.0f}s '
              f'= {(time.time() - t1) / n:.2f}s/frame', flush=True)


if __name__ == '__main__':
    main()
