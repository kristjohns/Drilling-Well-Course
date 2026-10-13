"""Scene base class: timing helpers, chapter cards, overlays."""
from __future__ import annotations

import json
import os

import skia

from .core import (C, W, H, FPS, background, clamp, draw_text, ease_in_out, ease_out, ease_out_quint, lerp,
                   paint, prog, window, with_alpha, mix, font, rgb)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TIMELINE = os.path.join(ROOT, "build", "audio", "timeline.json")
CREDITS_DUR = 18.0

CHAPTERS = [
    ("1", "What is well integrity?"),
    ("2", "The Norwegian framework"),
    ("3", "Barrier philosophy"),
    ("4", "Verification and testing"),
    ("5", "Annulus pressure management"),
    ("6", "Classifying well integrity"),
    ("7", "When barriers fail"),
    ("8", "Plug and abandonment"),
    ("9", "A new chapter: CO₂ storage"),
    ("10", "Digital well integrity and key lessons"),
]


def load_timeline():
    return json.load(open(TIMELINE))


class Scene:
    id = ""
    bg = "dots"
    chapter_card = True
    extra_tail = 0.0  # visual-only seconds appended after the narration

    def __init__(self, tl: dict | None = None):
        tl = tl if tl is not None else load_timeline()
        full = tl
        ids = list(full.keys())
        narrated_total = sum(v["duration"] for v in full.values())
        self.total = narrated_total + CREDITS_DUR
        if self.id in tl:
            me = tl[self.id]
            self.cues = {k: tuple(v) for k, v in me["cues"].items()}
            self.sentences = me["sentences"]
            self.dur = me["duration"] + self.extra_tail
            self.chapter = me.get("chapter", "")
            self.title = me.get("title", "")
            self.global_start = sum(full[i]["duration"] for i in ids[: ids.index(self.id)])
        else:
            self.cues, self.sentences = {}, []
            self.dur = getattr(self, "fixed_dur", CREDITS_DUR)
            self.chapter, self.title = "", ""
            self.global_start = narrated_total
        self.setup()

    # -------------------------------------------------- timing helpers
    def c0(self, cue):
        return self.cues[cue][0]

    def c1(self, cue):
        return self.cues[cue][1]

    def at(self, cue, frac):
        a, b = self.cues[cue]
        return a + (b - a) * frac

    def p(self, t, cue, offset=0.0, dur=1.0, ease=ease_in_out):
        return prog(t, self.c0(cue) + offset, dur, ease)

    def pf(self, t, cue, f0=0.0, f1=1.0, ease=ease_in_out):
        """progress over a fraction range of a cue's speech."""
        a, b = self.at(cue, f0), self.at(cue, f1)
        return prog(t, a, max(0.01, b - a), ease)

    def vis(self, t, a, b=None, fi=0.6, fo=0.6, a_off=0.0, b_off=0.0):
        """visible from start of cue a (+a_off) until start of cue b (+b_off) or end of a."""
        ta = (self.c0(a) if isinstance(a, str) else a) + a_off
        if b is None:
            tb = self.c1(a) if isinstance(a, str) else a
        else:
            tb = (self.c0(b) if isinstance(b, str) else b)
        tb += b_off
        return window(t, ta, tb, fi, fo)

    def word_time(self, cue, word, occurrence=1):
        """Estimate when a word is spoken within a cue (character-proportional)."""
        a, b = self.cues[cue]
        # find the sentence(s) of this cue
        sents = [s for s in self.sentences if a - 0.01 <= s[0] <= b + 0.01]
        for s0, s1, text in sents:
            low = text.lower()
            idx = -1
            start = 0
            for _ in range(occurrence):
                idx = low.find(word.lower(), start)
                if idx < 0:
                    break
                start = idx + 1
            if idx >= 0:
                return s0 + (s1 - s0) * (idx / max(1, len(text)))
        return a

    # -------------------------------------------------- lifecycle
    def setup(self):
        pass

    def draw(self, c: skia.Canvas, t: float):
        pass

    def render(self, c: skia.Canvas, t: float):
        c.drawImage(background(self.bg), 0, 0)
        a = window(t, 0.0, self.dur - 0.55, 0.55, 0.55)
        if a < 1.0:
            c.saveLayerAlpha(None, int(255 * a))
            self.draw(c, t)
            self.overlays(c, t)
            c.restore()
        else:
            self.draw(c, t)
            self.overlays(c, t)

    # -------------------------------------------------- overlays
    def overlays(self, c, t):
        if self.chapter_card and self.chapter:
            self.chapter_overlay(c, t)
        self.progress_bar(c, t)

    def chapter_overlay(self, c, t):
        num, title = self.chapter, self.title
        # big card during the opening pause
        card_end = min(self.c0(next(iter(self.cues))) + 0.2, 3.4) if self.cues else 3.0
        k_in = ease_out_quint(clamp(t / 0.9))
        k_out = ease_in_out(clamp((t - (card_end - 0.6)) / 0.7))
        a_card = k_in * (1 - k_out)
        if a_card > 0.01:
            cx, cy = W / 2, H / 2
            # number
            sz = 190
            c.save()
            c.translate(0, (1 - k_in) * 30 - k_out * 30)
            draw_text(c, f"{int(num):02d}", cx, cy - 10, sz, C.primary, 200, a_card * 0.9, "center", display=True)
            draw_text(c, title, cx, cy + 82, 54, C.text, 600, a_card, "center", display=True)
            lw = 520 * ease_out(clamp((t - 0.3) / 1.2))
            c.drawLine(cx - lw / 2, cy + 120, cx + lw / 2, cy + 120, paint(C.primary, 0.8 * a_card, stroke=2))
            draw_text(c, "CHAPTER", cx, cy - 190, 20, C.muted, 600, a_card, "center", tracking=6)
            c.restore()
        # small persistent tag
        a_tag = ease_in_out(clamp((t - (card_end - 0.3)) / 0.8))
        if a_tag > 0.01:
            x, y = 64, 64
            draw_text(c, f"{int(num):02d}", x, y, 22, C.primary, 700, a_tag)
            c.drawLine(x + 36, y - 16, x + 36, y + 4, paint(C.line, a_tag, stroke=1.5))
            draw_text(c, title.upper(), x + 50, y, 18, C.muted, 600, a_tag, tracking=2.2)

    def progress_bar(self, c, t):
        g = (self.global_start + t) / self.total
        y = H - 6
        c.drawRect(skia.Rect(0, y, W, H), paint(C.grid, 0.5))
        c.drawRect(skia.Rect(0, y, W * g, H), paint(C.primary, 0.55))
