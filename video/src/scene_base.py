"""Base class for scenes: timeline access, 3D build hook and 2D drawing hooks."""
import importlib
import json
import os

import config as C
import gfx as G
import palette as P
from tl import TL


class Scene:
    ID = ''
    BLENDER = False       # has a Blender-rendered layer
    PHASE = None          # 0..3 -> phase tracker highlight, None = hidden
    DARK = False          # tracker styling on dark backgrounds
    TRACKER_IN = 0.0      # when the phase tracker fades in (s)
    AA = '5'              # Workbench anti-aliasing samples

    def __init__(self):
        self.tl = TL(self.ID)
        self._anchors = None

    # ---------------------------------------------------------------- timing
    @property
    def nframes(self):
        return self.tl.nframes

    def render_ranges(self):
        """Frame ranges (inclusive) that need a Blender render."""
        return [(0, self.nframes + C.HANDLE - 1)]

    def has_3d(self, f):
        return self.BLENDER and any(a <= f <= b for a, b in self.render_ranges())

    # ---------------------------------------------------------------- 3D
    def build(self):
        """Create the Blender scene (called inside bpy). Return anchors dict."""
        return {}

    # ---------------------------------------------------------------- 2D
    def anchors(self, f):
        if self._anchors is None:
            path = os.path.join(C.ANCHORS, self.ID + '.json')
            self._anchors = json.load(open(path)) if os.path.exists(path) else {}
        return self._anchors.get(str(f), {})

    def draw_bg(self, ctx, t, f):
        G.bg_gradient(ctx)

    def draw(self, ctx, t, f, A):
        pass

    def draw_tracker(self, ctx, t):
        if self.PHASE is not None:
            G.phase_tracker(ctx, self.PHASE, t, self.TRACKER_IN, dark=self.DARK)

    # ---------------------------------------------------------------- audio
    def sfx(self):
        """List of (sound_name, local_time_s, gain_db)."""
        return []

    # helpers
    def A(self, A, name):
        """Anchor -> (x, y) or None if not visible / behind camera."""
        a = A.get(name)
        if not a or not a[3] or a[2] <= 0:
            return None
        return a[0], a[1]


def load(scene_id):
    mod = importlib.import_module('scenes.' + scene_id)
    return mod.S()


def all_ids():
    import script
    return [s['id'] for s in script.SCENES]
