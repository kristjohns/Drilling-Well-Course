"""Composite background + Blender layer + 2D overlays per scene into video segments.

usage:
  python3 compose.py <scene_id> [--frames A B]      -> build/segments/<id>.mp4
  python3 compose.py <scene_id> --png F [F ...]     -> build/preview/<id>_F.png
"""
import os
import subprocess
import sys
import time

import cairo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as C  # noqa: E402
import gfx as G  # noqa: E402
import scene_base  # noqa: E402

PREVIEW = os.path.join(C.BUILD, 'preview')


class Renderer:
    def __init__(self, scene):
        self.scene = scene
        self.cv = G.Canvas()
        self.frames_dir = os.path.join(C.FRAMES, scene.ID)

    def frame(self, f, cv=None):
        """Draw frame f of the scene into canvas cv (default own canvas)."""
        cv = cv or self.cv
        s = self.scene
        ctx = cv.ctx
        t = f / C.FPS
        A = s.anchors(f)
        cv.clear()
        ctx.save()
        s.draw_bg(ctx, t, f)
        ctx.restore()
        if s.has_3d(f):
            path = os.path.join(self.frames_dir, '%04d.png' % f)
            if os.path.exists(path) and os.path.getsize(path) > 0:
                img = cairo.ImageSurface.create_from_png(path)
                ctx.save()
                ctx.set_source_surface(img, 0, 0)
                ctx.paint()
                ctx.restore()
                s.draw_3d_post(ctx, t, f, A) if hasattr(s, 'draw_3d_post') else None
        ctx.save()
        s.draw(ctx, t, f, A)
        ctx.restore()
        ctx.save()
        s.draw_tracker(ctx, t)
        ctx.restore()
        return cv


def blend(dst, src, k):
    """Paint src canvas over dst with opacity k."""
    ctx = dst.ctx
    ctx.save()
    ctx.set_source_surface(src.surface, 0, 0)
    ctx.paint_with_alpha(k)
    ctx.restore()


def ffmpeg_writer(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra',
           '-s', f'{C.W}x{C.H}', '-r', str(C.FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
           '-x264-params', 'keyint=48:min-keyint=24', path]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def compose(sid, f_range=None, png=None):
    ids = scene_base.all_ids()
    scene = scene_base.load(sid)
    R = Renderer(scene)
    prev = None
    k = ids.index(sid)
    if k > 0:
        try:
            prev = Renderer(scene_base.load(ids[k - 1]))
        except ModuleNotFoundError:
            print('note: previous scene not available, no cross-fade')
    pcv = G.Canvas()
    n = scene.nframes
    fr = range(*(f_range or (0, n)))
    if png is not None:
        os.makedirs(PREVIEW, exist_ok=True)
        for f in png:
            out = _composite(R, prev, f, pcv)
            out.surface.write_to_png(os.path.join(PREVIEW, f'{sid}_{f:04d}.png'))
        return
    path = os.path.join(C.SEGMENTS, sid + '.mp4')
    if f_range:
        path = os.path.join(C.SEGMENTS, f'{sid}_{f_range[0]}_{f_range[1]}.mp4')
    proc = ffmpeg_writer(path)
    t0 = time.time()
    for f in fr:
        out = _composite(R, prev, f, pcv)
        out.surface.flush()
        proc.stdin.write(bytes(out.surface.get_data()))
    proc.stdin.close()
    proc.wait()
    dt = time.time() - t0
    print(f'[{sid}] composed {len(fr)} frames in {dt:.0f}s ({dt / max(1, len(fr)):.3f}s/f) -> {path}',
          flush=True)


def _composite(R, prev, f, pcv):
    cv = R.frame(f)
    if prev is not None and f < C.HANDLE:
        k = G.ease_in_out((f + 0.5) / C.HANDLE)
        prev.frame(prev.scene.nframes + f, pcv)
        blend(pcv, cv, k)
        return pcv
    return cv


if __name__ == '__main__':
    a = sys.argv[1:]
    sid = a[0]
    if '--png' in a:
        i = a.index('--png') + 1
        compose(sid, png=[int(x) for x in a[i:] if not x.startswith('--')])
    elif '--frames' in a:
        i = a.index('--frames') + 1
        compose(sid, (int(a[i]), int(a[i + 1])))
    else:
        compose(sid)
