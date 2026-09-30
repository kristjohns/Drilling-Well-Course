"""Scene-local timeline access: beat and word timings in seconds / frames."""
import json
import os
import re

import numpy as np

import config as C

_TL = None


def load():
    global _TL
    if _TL is None:
        with open(C.TIMELINE) as fh:
            _TL = json.load(fh)
    return _TL


class TL:
    def __init__(self, scene_id):
        tl = load()
        sc = next(s for s in tl['scenes'] if s['id'] == scene_id)
        self.id = scene_id
        self.fps = tl['fps']
        self.g0 = sc['start']
        self.duration = sc['end'] - sc['start']
        self.nframes = sc['frame_end'] - sc['frame_start']
        self.beats = {}
        self.text = {}
        for b in sc['beats']:
            self.beats[b['id']] = (b['start'] - self.g0, b['end'] - self.g0)
            self.text[b['id']] = b['text']
        self._pauses = {}

    # seconds (scene-local)
    def t(self, beat, frac=0.0, off=0.0):
        s, e = self.beats[beat]
        return s + (e - s) * frac + off

    def end(self, beat, off=0.0):
        return self.beats[beat][1] + off

    def dur(self, beat):
        s, e = self.beats[beat]
        return e - s

    # frames (scene-local, 0-based)
    def f(self, beat, frac=0.0, off=0.0):
        return int(round(self.t(beat, frac, off) * self.fps))

    def fe(self, beat, off=0.0):
        return int(round(self.end(beat, off) * self.fps))

    def sec(self, frame):
        return frame / self.fps

    def frame(self, sec):
        return int(round(sec * self.fps))

    @property
    def last(self):
        return self.nframes - 1

    # word timing estimate -------------------------------------------------
    def word(self, beat, word, occurrence=1, off=0.0):
        """Estimated local time at which `word` is spoken within a beat.

        Characters are spread uniformly over the clip, then snapped to the
        start of the nearest detected pause-boundary when close.
        """
        say = self._say(beat)
        idx = -1
        for _ in range(occurrence):
            idx = say.lower().find(word.lower(), idx + 1)
        if idx < 0:
            raise KeyError(f'{word!r} not in beat {beat}')
        s, e = self.beats[beat]
        est = s + (e - s) * idx / max(1, len(say))
        # snap to the end of a pause if one is within 0.35 s
        best = None
        for p in self.pauses(beat):
            ps = s + p
            if abs(ps - est) < 0.35 and (best is None or abs(ps - est) < abs(best - est)):
                best = ps
        return (best if best is not None else est) + off

    def fw(self, beat, word, occurrence=1, off=0.0):
        return int(round(self.word(beat, word, occurrence, off) * self.fps))

    def _say(self, beat):
        import script
        for sc in script.SCENES:
            for b in sc['beats']:
                if b[0] == beat:
                    return b[1]
        raise KeyError(beat)

    def pauses(self, beat):
        """Clip-relative times where speech resumes after a silence > 0.12 s."""
        if beat in self._pauses:
            return self._pauses[beat]
        out = []
        path = os.path.join(C.AUDIO_DIR, beat + '.wav')
        if os.path.exists(path):
            import soundfile as sf
            x, sr = sf.read(path, dtype='float32')
            hop = int(sr * 0.01)
            env = np.array([np.abs(x[i:i + hop]).max() for i in range(0, len(x) - hop, hop)])
            quiet = env < 0.01
            run = 0
            for i, q in enumerate(quiet):
                if q:
                    run += 1
                else:
                    if run >= 12:
                        out.append(i * 0.01)
                    run = 0
        self._pauses[beat] = out
        return out
