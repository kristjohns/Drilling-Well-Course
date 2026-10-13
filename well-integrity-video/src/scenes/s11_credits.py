"""Closing card: sources and production notes (no narration)."""
from __future__ import annotations

import skia

from engine.core import C, W, H, clamp, draw_text, ease_out, paint, window
from engine.scene import Scene, CREDITS_DUR

SOURCES = [
    "Havtil: Facilities Regulations § 48; Activities Regulations §§ 85, 88; Management Regulations § 5",
    "Standards Norway: NORSOK D-010:2021+AC:2024, Well integrity in drilling and well operations",
    "Offshore Norge: Guideline 117 Well integrity (rev. 6); Guideline 135 Classification of incidents (rev. 7)",
    "ISO 16530-1:2017 Well integrity, life cycle governance",
    "Havtil (2024): Temporarily abandoned wells 2024, public report",
    "Havtil (2024-2026): plug and abandonment seminars; Plugging and abandonment under the spotlight (2025)",
    "Havtil / Reflekt (2025): Knowledge acquisition, creeping shale as a well barrier element",
    "Havtil (2026) and Equinor (2026): investigations of the Deepsea Bollsta well control incident, Troll",
    "Statoil and the Petroleum Safety Authority: Snorre A (2004) and Gullfaks C (2010) investigations",
    "Vignes and Aadnøy (2010): Well-integrity issues offshore Norway, SPE Production & Operations",
    "SINTEF (2024): CCS well design requirements, report 2024:00065 for Standards Norway",
    "Equinor and Northern Lights (2025); Equinor (2025): industrialising plugging operations",
]


class SceneImpl(Scene):
    id = "s11_credits"
    chapter_card = False
    fixed_dur = CREDITS_DUR

    def draw(self, c, t):
        a = window(t, 0.3, self.dur - 0.8, 1.0, 0.8)
        draw_text(c, "SOURCES", 160, 150, 22, C.primary, 700, a, tracking=6)
        for i, s in enumerate(SOURCES):
            k = ease_out(clamp((t - 0.6 - i * 0.12) / 0.6)) * a
            draw_text(c, s, 160, 215 + i * 50, 24, C.text, 400, k)
        y = 215 + len(SOURCES) * 50 + 40
        c.drawLine(160, y - 20, W - 160, y - 20, paint(C.line, a, stroke=1))
        notes = ["Well schematics, pressures and values are illustrative and not for engineering use.",
                 "Narration: synthetic voice (Kokoro-82M, Apache-2.0). Animation rendered in code with Skia.",
                 "Map coastlines are schematic."]
        for i, s in enumerate(notes):
            draw_text(c, s, 160, y + 20 + i * 40, 22, C.muted, 400, a * ease_out(clamp((t - 2.5) / 0.8)))
        draw_text(c, "WELL INTEGRITY", W - 160, H - 90, 30, C.text, 700, a, "right", display=True, tracking=6)
