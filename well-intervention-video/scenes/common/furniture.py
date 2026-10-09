"""Recurring on-screen furniture: chapter title card + header, 'well so far' strip, term cards, scope badges.

Layout (world units, canvas 16 x 9, centre 0,0):
  header      x -7.85.., y 4.18            (chapter tag + title, top-left)
  content     x -7.8 .. 7.8,  y -3.5 .. 3.9
  term cards  top-right, x 3.3 .. 7.85, from y 3.92 down (height follows the definition)
  badges      header row, right-aligned at x 7.85
Text is laid out with real font metrics (Stage.measure), so nothing depends on guessed character widths.
"""
from __future__ import annotations

from . import palette as P
from .look import wrap_to

HEADER_Y = 4.18


def _intro(tl) -> float:
    return getattr(tl, "intro", 0.0) or 0.0


def header(st, tl, t0=None, t1=None):
    t0 = _intro(tl) if t0 is None else t0
    t1 = tl.dur if t1 is None else t1
    with st.span(t0, t1):
        tag = f"CH {tl.num:02d}"
        tw = st.measure(tag, 0.17, "bold") + 0.3
        x0 = -7.85
        plate = st.rect(x0 + tw / 2, HEADER_Y, tw, 0.36, P.PORE, 0.5, role="pill", alpha=0.95)
        a = st.text(tag, x0 + tw / 2, HEADER_Y, 0.17, P.BG, 0.51, kind="bold")
        b = st.text(tl.title.upper(), x0 + tw + 0.2, HEADER_Y, 0.21, P.TEXT, 0.5, align="l", kind="bold", alpha=0.82)
        st.fade_in([plate, a, b], t0 + 0.15, 0.45)


def title_card(st, tl):
    """Full-screen chapter opener for [0, intro): big number, title, an accent rule that draws on."""
    T = _intro(tl)
    if T <= 0:
        return
    with st.span(0.0, T):
        st.rect(0, 0, 16.5, 9.5, P.BG, 40.0, role="backdrop")
        num = st.text(f"{tl.num:02d}", -6.0, 0.55, 1.15, P.PORE, 40.2, align="l", kind="bold")
        lab = st.text("CHAPTER", -6.0, 1.55, 0.2, P.MUTED, 40.2, align="l", kind="bold")
        title = st.text(wrap_to(tl.title, 0.62, 11.0, "bold"), -6.0, -0.75, 0.62, P.TEXT, 40.2, align="l", kind="bold", valign="t")
        rule = st.line([(-6.0, -0.15), (-1.0, -0.15)], P.PORE, 0.05, 40.3)
        st.fade_in([lab, num], 0.12, 0.45)
        st.fade_in(title, 0.35, 0.5)
        st.draw_on(rule, 0.3, min(1.3, T - 0.3), "BEZIER")


def chapter_end(st, tl, d=0.5):
    """Fade the whole frame down to the bare background over the last d seconds (clean cut to the next title card)."""
    with st.span(tl.dur - d, tl.dur + 1.0):
        bd = st.rect(0, 0, 16.5, 9.5, P.BG, 60.0, role="backdrop")
        st.fade_in(bd, tl.dur - d, d)


CARD_X0, CARD_X1, CARD_TOP = 3.3, 7.85, 3.92


def card_height(definition):
    """Height of one term card (it sizes itself to its wrapped definition)."""
    dfn = wrap_to(definition, 0.145, CARD_X1 - CARD_X0 - 0.55, "sans")
    n = dfn.count("\n") + 1
    return 0.16 + 0.15 + 0.1 + 0.27 + 0.08 + n * 0.145 * 1.18 * 1.22 + 0.16


def term_cards(st, t0, d, terms, y_top=CARD_TOP):
    """Stacked top-right cards for the terms defined in this beat; each card sizes itself to its definition.
    Returns the y of the bottom edge of the last card."""
    y = y_top
    w = CARD_X1 - CARD_X0
    for term, definition in terms:
        dfn = wrap_to(definition, 0.145, w - 0.55, "sans")
        h = card_height(definition)
        cy = y - h / 2
        with st.span(t0, t0 + d):
            parts = [
                st.rect((CARD_X0 + CARD_X1) / 2, cy, w, h, P.PANEL2, 0.6, role="card"),
                st.rect(CARD_X0 + 0.16, cy, 0.05, h - 0.3, P.PORE, 0.61, role="shaft"),
                st.text("NEW TERM", CARD_X0 + 0.34, y - 0.16 - 0.075, 0.12, P.PORE, 0.62, align="l", kind="bold"),
                st.text(term.upper(), CARD_X0 + 0.34, y - 0.16 - 0.15 - 0.1 - 0.12, 0.22, P.TEXT, 0.62, align="l", kind="bold"),
                st.text(dfn, CARD_X0 + 0.34, y - 0.16 - 0.15 - 0.1 - 0.27 - 0.04, 0.145, P.MUTED, 0.62, align="l", valign="t"),
            ]
            st.fade_in(parts, t0, 0.35)
            st.fade_out(parts, t0 + d - 0.4, 0.35)
        y -= h + 0.12
    return y + 0.12


def term_card(st, t0, d, term, definition, slot=0):
    """Back-compat single card (slot ignored: use term_cards for stacking)."""
    term_cards(st, t0, d, [(term, definition)])


def badge(st, t0, t1, label, color, x_right=7.85, y=HEADER_Y):
    """Scope badge in the header row (top-right), right edge at x_right. Returns its width."""
    w = st.measure(label, 0.15, "bold") + 0.36
    with st.span(t0, t1):
        parts = [st.rect(x_right - w / 2, y, w, 0.34, color, 0.7, role="pill"),
                 st.text(label, x_right - w / 2, y, 0.15, P.BG, 0.71, kind="bold")]
        st.fade_in(parts, t0, 0.3)
    return w


_GLOSSARY = None


def _aliases(term):
    """The term plus its glossary aliases (longest first), for finding where it is first spoken."""
    global _GLOSSARY
    if _GLOSSARY is None:
        import os
        import yaml
        path = os.path.join(os.path.dirname(__file__), "..", "..", "script", "glossary.yaml")
        try:
            _GLOSSARY = yaml.safe_load(open(path, encoding="utf-8")) or {}
        except OSError:
            _GLOSSARY = {}
    names = [term] + list((_GLOSSARY.get(term) or {}).get("aliases") or [])
    return sorted({n for n in names if n}, key=len, reverse=True)


def spoken_at(b, term):
    """Chapter time at which `term` (or an alias) is first spoken in beat b; falls back to the beat start."""
    import re
    for i, s in enumerate(b._sentences()):
        for name in _aliases(term):
            m = re.search(r"(?<![A-Za-z0-9])" + re.escape(name) + r"(?![A-Za-z0-9])", s, re.I)
            if m:
                return b.word(i, m.group(0))
    return b.start + 0.5


MAX_CARDS = 5        # per beat
CARD_GAP = 0.12
CARD_FLOOR = 0.2     # a card never reaches below this y (content and subtitles live below)


def card_layout(b):
    """Where and when each term card of beat b appears: [(term, definition, t0, d, y_top, y_bottom)], in spoken order.
    A card appears as its term is first spoken and takes the highest free slot among the cards on screen at that moment;
    if none fits above CARD_FLOOR, the oldest card on screen leaves early to make room."""
    items = []
    for t in b.terms[:MAX_CARDS]:
        t0 = min(max(spoken_at(b, t["term"]) - 0.3, b.start + 0.3), b.end - 3.0)
        d = max(min(7.5, b.end - t0 - 0.25), 3.0)
        items.append([t0, t["term"], t["def"], d])
    items.sort(key=lambda x: x[0])
    out = []                                   # [term, def, t0, d, y_top, y_bot]
    for t0, term, dfn, d in items:
        h = card_height(dfn)
        while True:
            live = sorted([c for c in out if c[2] <= t0 + 0.05 and c[2] + c[3] > t0 + 0.2], key=lambda c: -c[4])
            y = None
            for cand in [CARD_TOP] + [c[5] - CARD_GAP for c in live]:
                if cand - h < CARD_FLOOR:
                    continue
                if all(cand - h > c[4] + CARD_GAP or cand < c[5] - CARD_GAP + 1e-6 for c in live):
                    y = cand
                    break
            if y is not None or not live:
                break
            oldest = min(live, key=lambda c: c[2])
            oldest[3] = max(t0 - oldest[2] + 0.1, 0.5)   # it leaves as the new one arrives
        y = CARD_TOP if y is None else y
        out.append([term, dfn, t0, d, y, y - h])
    return [tuple(c) for c in out]


def auto_overlays(st, tl):
    """Title card, term cards, scope badges and the chapter-end fade, straight from the script (they cannot drift).
    Each term card appears as its term is spoken; badges stay while the beat's narration runs."""
    title_card(st, tl)
    for b in tl.beats:
        for term, dfn, t0, d, y_top, _ in card_layout(b):
            term_cards(st, t0, d, [(term, dfn)], y_top)
        t_badge_end = min(b.end - 0.2, b.start + 6.5)
        t_badge_end = max(t_badge_end, b.start + 1.5)
        x_right = 7.85
        if "NO" in b.scope:
            x_right -= badge(st, b.start + 0.3, t_badge_end, "NORWAY / NORSOK-SPECIFIC", P.NO_BADGE, x_right) + 0.15
        if b.sim:
            badge(st, b.start + 0.3, t_badge_end, "SIMPLIFIED", P.SIM_BADGE, x_right)
    chapter_end(st, tl)


def extra_transitions(tl):
    """Extra dissolve points besides beat starts (the end of the chapter title card, when the timeline has one)."""
    intro = _intro(tl)
    return [intro] if intro > 0 else []
