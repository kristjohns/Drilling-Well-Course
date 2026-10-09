"""Gas lift hardware, drawn procedurally: the side-pocket mandrel, the gas-lift valve and the kick-over tool.

Geometry (long-section, y up):
  * main bore on the left (full tubing ID), an off-centre pocket on the right separated by a web;
  * at the top of the mandrel an orienting sleeve: a half-turn helical guide (mule shoe) leading to a vertical slot;
  * an open guide region above the pocket, then the pocket: latch lug, upper seal bore, injection ports to the annulus,
    lower seal bore, and at the bottom a discharge opening into the main bore.
The valve is an injection-pressure-operated (IPO) bellows valve: latch (fishing neck, locking ring, shear pin), nitrogen
dome, bellows, stem and ball on a seat, inlet ports between two packing stacks, a reverse-flow check valve and the nose.
Annulus gas enters through the mandrel ports between the packings, lifts the ball off the seat, flows down past the check
valve and out of the nose into the pocket bottom, and from there into the tubing.

Everything is parameterised by the bore ID `s` (world units) so the same drawing works as a full-screen cutaway, an inset
or a small icon. All functions draw on a world-coordinate canvas inside a Stage.procedural callback.
"""
from __future__ import annotations
import math

from . import palette as P
from . import pdraw as D
from .look import lighten, darken
from .stage import hex_rgb

# fractions along the valve length, from the top of the fishing neck
VF = dict(neck=(0.0, 0.10), latch=(0.10, 0.26), ring=(0.195, 0.235), pin=0.145, dome=(0.27, 0.46), bellows=(0.46, 0.585),
          seat=0.675, ports=(0.615, 0.66), pack_up=(0.515, 0.605), pack_lo=(0.695, 0.785), check=(0.82, 0.905), nose=(0.905, 1.0))


class SPM:
    """Side-pocket mandrel geometry. bx = main-bore centre; s = bore ID; y_top..y_bot = drawn length."""

    def __init__(self, bx, y_top, y_bot, s=1.0, sleeve_frac=0.094, open_frac=0.322, pocket_frac=0.255, slot_frac=0.6):
        self.bx, self.y_top, self.y_bot, self.s = bx, y_top, y_bot, s
        H = y_top - y_bot
        self.H = H
        self.wall = 0.16 * s
        self.web = 0.14 * s
        self.pr = 0.28 * s                               # pocket radius
        self.xL = bx - 0.5 * s                           # inner faces of the main bore
        self.xR = bx + 0.5 * s
        self.px = self.xR + self.web + self.pr           # pocket centre
        self.xO = self.px + self.pr                      # inner face of the outer wall (body section)
        self.sw_top0 = y_top - 0.03 * H                  # swage: tubing OD -> body OD
        self.sw_top1 = y_top - 0.08 * H
        self.ys0 = y_top - 0.09 * H                      # orienting sleeve, top
        self.ys1 = self.ys0 - sleeve_frac * H            # sleeve bottom (lowest point of the helix)
        self.y_slot = self.ys0 - slot_frac * (self.ys0 - self.ys1)   # bottom of the vertical slot (top end of the helix)
        self.y_pt = self.ys1 - open_frac * H             # pocket top
        self.y_pb = self.y_pt - pocket_frac * H          # pocket bottom
        self.sw_bot0 = self.y_pb - 0.035 * H
        self.sw_bot1 = self.sw_bot0 - 0.04 * H
        # the valve, set: neck sticks up just above the pocket top, nose just above the pocket bottom
        self.v_top = self.y_pt + 0.05 * s
        self.L = self.v_top - (self.y_pb + 0.05 * s)
        self.vw = 0.44 * s
        f = lambda k: self.v_top - k * self.L
        self.y_port = f(sum(VF["ports"]) / 2)
        self.y_lug = f(VF["ring"][0]) + 0.02 * s
        self.seal_up = (f(VF["pack_up"][0]) + 0.02 * s, f(VF["pack_up"][1]) - 0.02 * s)
        self.seal_lo = (f(VF["pack_lo"][0]) + 0.02 * s, f(VF["pack_lo"][1]) - 0.02 * s)
        self.y_dis = self.y_pb + 0.13 * s                # discharge opening into the main bore
        # kick-over tool proportions: the orienting key sits well above the arm pivot, so that when the key reaches the top
        # of the slot the kicked-over tool hangs just above the valve, and the slack-off stays inside the slot
        self.key_r = 0.33 * s                            # key radius (tool OD / 2)
        self.key_to_pivot = 0.5 * s
        self.arm = 1.25 * s
        self.kick = math.asin(min((self.px - self.bx) / self.arm, 0.99))   # arm angle that puts the tool over the pocket
        self.tool_len = 0.9 * s                          # pulling / running tool on the arm
        self.body_len = 2.2 * s
        # derived positions for the job (key heights)
        self.key_top = self.ys0 - 0.08 * s               # key at the top of the slot
        drop = self.arm * math.cos(self.kick)
        self.key_land = self.v_top - 0.12 * s + self.tool_len + drop + self.key_to_pivot   # pulling tool over the valve's neck
        self.key_folded_low = self.ys1 - 0.25 * s

    def key_for_tool_bottom(self, y_tool_bottom, kick=1.0):
        """Key height that puts the payload tool's bottom at y_tool_bottom for a given kick fraction."""
        drop = self.arm * math.cos(self.kick * kick)
        return y_tool_bottom + self.tool_len + drop + self.key_to_pivot

    def valve_y(self, k):
        return self.v_top - k * self.L

    def helix(self, u):
        """Point on the orienting helix for u in [0, 1] (0 = lowest, left; 1 = slot bottom, pocket side); returns (x, y, phi)."""
        phi = math.pi * (1.0 - u)
        return self.bx + self.key_r * math.cos(phi), self.ys1 + u * (self.y_slot - self.ys1), phi


# ---------------------------------------------------------------------------------------------- the mandrel
def draw_spm(c, look, g: SPM, a=1.0, annulus=None, port_glow=0.0, highlight=None):
    """The mandrel cutaway. annulus: optional fill colour for the annulus strip right of the body.
    port_glow: 0..1 glow on the injection ports. highlight: 'sleeve' | 'pocket' | 'lug' | None."""
    if a <= 0.003:
        return
    s, w = g.s, g.wall
    bore = darken(hex_rgb(P.BG), 0.35)
    # annulus (outside the mandrel, right)
    if annulus:
        D.fill(c, g.xO + w, g.y_bot, g.xO + w + 0.55 * s, g.y_top, annulus, 0.22 * a)
        D.steel(c, g.xO + w + 0.55 * s, g.y_bot, g.xO + w + 0.55 * s + 0.1 * s, g.y_top, P.STEEL_DK, 0.7 * a)
    # bore, pocket and guide region (dark)
    D.fill(c, g.xL, g.y_bot, g.xR, g.y_top, bore, a)
    D.fill(c, g.xR, g.sw_bot0, g.xO, g.sw_top1, bore, a)
    # left wall (full length)
    D.steel(c, g.xL - w, g.y_bot, g.xL, g.y_top, P.STEEL, a)
    # right side: tubing wall above and below the body, swages, outer body wall
    D.steel(c, g.xR, g.sw_top0, g.xR + w, g.y_top, P.STEEL, a)
    D.steel(c, g.xR, g.y_bot, g.xR + w, g.sw_bot1, P.STEEL, a)
    D.steel_poly(c, [(g.xR, g.sw_top0), (g.xR + w, g.sw_top0), (g.xO + w, g.sw_top1), (g.xO, g.sw_top1 - 0.02 * s), (g.xR, g.sw_top1 + 0.15 * s)], P.STEEL, a)
    D.steel_poly(c, [(g.xR, g.sw_bot1), (g.xR + w, g.sw_bot1), (g.xO + w, g.sw_bot0), (g.xO, g.sw_bot0 + 0.02 * s), (g.xR, g.sw_bot0 - 0.15 * s)], P.STEEL, a)
    yp_lo, yp_hi = g.y_port - 0.05 * s, g.y_port + 0.05 * s
    D.steel(c, g.xO, g.sw_bot0, g.xO + w, yp_lo, P.STEEL, a)
    D.steel(c, g.xO, yp_hi, g.xO + w, g.sw_top1, P.STEEL, a)
    # web between bore and pocket (with the discharge opening near the bottom) and its bevelled top (the guide)
    xw0, xw1 = g.xR, g.xR + g.web
    D.steel(c, xw0, g.sw_bot0, xw1, g.y_dis - 0.06 * s, P.STEEL, a)
    D.steel(c, xw0, g.y_dis + 0.06 * s, xw1, g.y_pt, P.STEEL, a)
    D.steel_poly(c, [(xw0, g.y_pt), (xw1, g.y_pt), (xw1, g.y_pt + 0.05 * s), (xw0, g.y_pt + 0.28 * s)], P.STEEL, a)
    # pocket bottom cap
    D.steel(c, xw1, g.sw_bot0, g.xO, g.y_pb, P.STEEL_DK, a)
    # seal bores: polished bands on the pocket walls
    for y0, y1 in (g.seal_up, g.seal_lo):
        D.fill(c, xw1 - 0.02 * s, y1, xw1, y0, lighten(hex_rgb(P.STEEL), 0.35), 0.8 * a)
        D.fill(c, g.xO, y1, g.xO + 0.02 * s, y0, lighten(hex_rgb(P.STEEL), 0.35), 0.8 * a)
    # latch lug: small shoulders at the pocket top
    for x0, x1 in ((xw1, xw1 + 0.06 * s), (g.xO - 0.06 * s, g.xO)):
        D.steel_poly(c, [(x0, g.y_lug), (x1, g.y_lug), (x1, g.y_lug + 0.07 * s), (x0, g.y_lug + 0.07 * s)], P.STEEL_DK, a)
    if highlight == "lug":
        D.glow(c, look, g.px, g.y_lug + 0.03 * s, 0.25 * s, P.WARN, 0.6 * a)
    # ports glow
    if port_glow > 0:
        D.glow(c, look, g.xO + w / 2, g.y_port, 0.18 * s, P.GAS, port_glow * a)
    # orienting sleeve: liners on both sides, the back face (lighter steel) cut by the helix, and the slot
    t = 0.07 * s
    D.steel(c, g.xL, g.ys1, g.xL + t, g.ys0, P.STEEL_DK, a)
    pts = [g.helix(i / 30)[:2] for i in range(31)]
    back = [(g.xL + t, g.ys0)] + [(x, y) for x, y in pts] + [(g.xR - t, g.y_slot), (g.xR - t, g.ys0)]
    D.poly(c, back, P.STEEL_DK, 0.75 * a)
    D.poly(c, back, darken(hex_rgb(P.STEEL), 0.2), 0.25 * a)
    D.steel(c, g.xR - t, g.y_slot, g.xR, g.ys0, P.STEEL_DK, a)
    sx0, sx1 = g.bx + g.key_r - 0.06 * s, g.bx + g.key_r + 0.06 * s
    D.fill(c, sx0, g.y_slot, sx1, g.ys0 - 0.02 * s, bore, a)      # the slot
    hl = 1.0 if highlight == "sleeve" else 0.0
    D.stroke(c, pts, P.WARN, 0.035 * s, (0.7 + 0.3 * hl) * a)
    D.stroke(c, [(sx0, g.y_slot), (sx0, g.ys0 - 0.02 * s)], P.WARN, 0.022 * s, (0.6 + 0.4 * hl) * a)
    D.stroke(c, [(sx1, g.y_slot + 0.06 * s), (sx1, g.ys0 - 0.02 * s)], P.WARN, 0.022 * s, (0.6 + 0.4 * hl) * a)
    if hl:
        D.glow(c, look, g.bx, (g.ys0 + g.ys1) / 2, 0.55 * s, P.WARN, 0.18 * a)
    D.steel(c, g.xL - 0.0, g.ys0, g.xR, g.ys0 + 0.05 * s, P.STEEL_DK, a)


# ---------------------------------------------------------------------------------------------- the valve
def draw_valve(c, look, x, y_top, L, w, a=1.0, detail="full", lift=0.0, check_open=0.0, ring=1.0, pin=1.0,
               body=P.STEEL, outline=None, labels=False):
    """Gas-lift valve, top of fishing neck at y_top, length L, body width w.
    lift: 0..1 ball off seat (bellows compressed); check_open 0..1; ring: 1 = locking ring expanded (latched), 0 = retracted;
    pin: 1 = shear pin intact, 0 = sheared. detail 'full' = cutaway with internals, 'body' = solid with packings."""
    if a <= 0.003:
        return
    y = lambda k: y_top - k * L
    rw = w / 2
    # outline glow (selection / state)
    if outline:
        D.glow(c, look, x, y(0.5), 0.0, outline, 0.0)
        D.flat(c, x - rw - 0.04 * w, y(1.0) - 0.02 * w, x + rw + 0.04 * w, y(0.0) + 0.02 * w, outline, 0.25 * a, r=0.05 * w, edge=False)
    # neck and latch
    D.steel(c, x - 0.21 * w, y(VF["neck"][1]), x + 0.21 * w, y(0.0), body, a)
    D.steel(c, x - 0.25 * w, y(0.015), x + 0.25 * w, y(0.0), body, a)                        # neck shoulder (fishing neck)
    D.steel(c, x - 0.41 * w, y(VF["latch"][1]), x + 0.41 * w, y(VF["latch"][0]), body, a)
    r0, r1 = VF["ring"]
    ext = 0.06 * w + 0.07 * w * ring
    for sd in (-1, 1):
        x_in = x + sd * 0.38 * w
        x_out = x + sd * (0.41 * w + ext)
        D.poly(c, [(x_in, y(r1)), (x_out, y(r1) + 0.004 * L), (x_out, y(r0) - 0.01 * L), (x_in, y(r0))], P.WARN, a)
    py = y(VF["pin"])
    if pin > 0.5:
        D.disc(c, x, py, 0.06 * w, P.BAD, a)
    else:
        D.disc(c, x - 0.07 * w, py + 0.01 * L, 0.04 * w, P.BAD, a)
        D.disc(c, x + 0.07 * w, py - 0.01 * L, 0.04 * w, P.BAD, a)
    # body shell
    top, bot = y(VF["latch"][1]), y(VF["nose"][0])
    sh = 0.11 * w
    p0, p1 = VF["ports"]
    if detail == "full":
        cav = darken(hex_rgb(P.BG), 0.15)
        D.fill(c, x - rw + sh, bot, x + rw - sh, top, cav, a)
        # shell walls with the inlet ports
        for sd in (-1, 1):
            xa, xb = (x - rw, x - rw + sh) if sd < 0 else (x + rw - sh, x + rw)
            D.steel(c, xa, y(p0), xb, top, body, a)
            D.steel(c, xa, bot, xb, y(p1), body, a)
        # dome: nitrogen charge
        d0, d1 = VF["dome"]
        D.fill(c, x - rw + sh, y(d1), x + rw - sh, y(d0), P.N2, 0.35 * a)
        D.steel(c, x - rw, y(d0) + 0.01 * L, x + rw, y(d0), body, a)
        if L > 2.0:
            D.text(c, look, "N₂", x, (y(d0) + y(d1)) / 2, 0.06 * L, P.TEXT, 0.9 * a, kind="bold")
        # bellows: top fixed under the dome, bottom moves up as the valve opens
        b0, b1 = VF["bellows"]
        dy = 0.032 * L * lift
        D.bellows(c, x, y(b1) + dy, y(b0), 0.62 * w, 7, P.STEEL, a)
        # stem and ball
        ball_y = y(VF["seat"]) + 0.05 * w + dy
        D.steel(c, x - 0.05 * w, ball_y, x + 0.05 * w, y(b1) + dy, P.STEEL, a)
        D.disc(c, x, ball_y, 0.1 * w, lighten(hex_rgb(P.STEEL), 0.15), a)
        D.ring(c, x, ball_y, 0.1 * w, 0.012 * w, darken(hex_rgb(P.STEEL), 0.4), a)
        # seat
        sy = y(VF["seat"])
        D.steel(c, x - rw + sh, sy - 0.03 * w, x - 0.09 * w, sy + 0.01 * w, P.STEEL_DK, a)
        D.steel(c, x + 0.09 * w, sy - 0.03 * w, x + rw - sh, sy + 0.01 * w, P.STEEL_DK, a)
        # check valve: a dart held up on its seat by a spring; flow pushes it down
        k0, k1 = VF["check"]
        cy0 = y(k0)
        D.steel(c, x - rw + sh, cy0 - 0.02 * w, x - 0.11 * w, cy0 + 0.01 * w, P.STEEL_DK, a)
        D.steel(c, x + 0.11 * w, cy0 - 0.02 * w, x + rw - sh, cy0 + 0.01 * w, P.STEEL_DK, a)
        dd = 0.025 * L * check_open
        D.poly(c, [(x, cy0 + 0.06 * w - dd), (x - 0.15 * w, cy0 - 0.08 * w - dd), (x + 0.15 * w, cy0 - 0.08 * w - dd)], P.WARN, a)
        D.zigzag(c, x - 0.1 * w, x + 0.1 * w, cy0 - 0.08 * w - dd, y(k1), 4, P.STEEL, 0.02 * w, a)
    else:
        D.steel(c, x - rw, bot, x + rw, top, body, a)
        D.fill(c, x - rw, y(p1), x - rw + sh * 0.8, y(p0), darken(hex_rgb(P.BG), 0.2), a)
        D.fill(c, x + rw - sh * 0.8, y(p1), x + rw, y(p0), darken(hex_rgb(P.BG), 0.2), a)
    # packing stacks (outside the body, sealing in the pocket's seal bores)
    for k0, k1 in (VF["pack_up"], VF["pack_lo"]):
        for sd in (-1, 1):
            xa, xb = (x - rw - 0.06 * w, x - rw + 0.02 * w) if sd < 0 else (x + rw - 0.02 * w, x + rw + 0.06 * w)
            D.rubber_stack(c, xa, xb, y(k1), y(k0), 3, a)
    # nose with the outlet
    n0, n1 = VF["nose"]
    D.steel_poly(c, [(x - rw, y(n0)), (x + rw, y(n0)), (x + 0.3 * w, y(n1)), (x - 0.3 * w, y(n1))], body, a)
    D.fill(c, x - 0.08 * w, y(n1), x + 0.08 * w, y(n1) + 0.03 * L, darken(hex_rgb(P.BG), 0.2), a)


def valve_flow_path(x, y_top, L, w, x_annulus, x_tubing, y_tubing_out):
    """Gas path for a valve in a pocket: from the annulus through the inlet port, through the seat, down past the check valve,
    out of the nose, then across into the tubing and up. Returns a polyline."""
    y = lambda k: y_top - k * L
    yp = y(sum(VF["ports"]) / 2)
    return [(x_annulus, yp), (x + w / 2, yp), (x + 0.12 * w, yp), (x, y(VF["seat"]) + 0.02 * L), (x, y(VF["check"][0]) - 0.03 * L),
            (x, y(1.0) - 0.02 * L), (x_tubing, y(1.0) - 0.02 * L), (x_tubing, y_tubing_out)]


# ---------------------------------------------------------------------------------------------- the kick-over tool
def draw_kot(c, look, g: SPM, y_key, phi=0.0, kick=0.0, a=1.0, tool="pulling", grip=0.0, wire_top=4.6, line_tension=0.0):
    """Kick-over tool on the line, positioned by its orienting key height y_key.
    phi: rotation (radians; 0 = arm faces the pocket); kick: 0..1 of the kick-over angle; tool: 'pulling' | 'running';
    grip: 0..1 the pulling tool's dogs closed on a fishing neck. Returns (x_tool, y_tool_bottom) of the payload tool."""
    if a <= 0.003:
        return None
    s = g.s
    bx = g.bx
    tw = 0.62 * s
    y_p = y_key - g.key_to_pivot
    y_body_top = y_p + g.body_len
    # wire and stem above
    D.stroke(c, [(bx, wire_top), (bx, y_body_top + 0.9 * s)], P.WIRE, 0.03 * s, a)
    D.steel(c, bx - 0.16 * s, y_body_top + 0.02 * s, bx + 0.16 * s, y_body_top + 0.9 * s, P.STEEL_DK, a)
    # the key (spring-loaded nub) projected at rotation phi; behind the body it is hidden
    front = math.sin(phi) >= -0.15 or abs(math.cos(phi)) > 0.6
    kx = bx + g.key_r * math.cos(phi)
    key_a = a * (1.0 if math.sin(phi) >= -0.05 else 0.35)
    # body
    D.steel(c, bx - tw / 2, y_p + 0.05 * s, bx + tw / 2, y_body_top, P.STEEL, a)
    D.steel(c, bx - tw / 2 - 0.02 * s, y_body_top - 0.12 * s, bx + tw / 2 + 0.02 * s, y_body_top, P.STEEL_DK, a)
    # recess where the arm folds (it turns with the tool)
    rx = bx + 0.22 * s * math.cos(phi)
    rec_a = a * max(0.0, math.sin(phi) * 0.5 + 0.5) * (1.0 - kick)
    D.fill(c, rx - 0.04 * s, y_p + 0.08 * s, rx + 0.04 * s, y_p + 1.1 * s, darken(hex_rgb(P.STEEL), 0.5), 0.8 * rec_a)
    # key
    kw, kh = 0.09 * s, 0.16 * s
    D.flat(c, kx - kw, y_key - kh / 2, kx + kw, y_key + kh / 2, P.WARN, key_a, r=0.02 * s)
    D.zigzag(c, kx - 0.03 * s * math.cos(phi), kx, y_key - kh / 2 - 0.12 * s, y_key - kh / 2, 3, P.STEEL, 0.012 * s, 0.7 * key_a)
    # the arm: pivot at the bottom of the body, swings out in the pocket direction (projected with cos phi)
    th = g.kick * kick
    dx = g.arm * math.sin(th) * math.cos(phi)
    x_e, y_e = bx + dx, y_p - g.arm * math.cos(th)
    D.stroke(c, [(bx, y_p), (x_e, y_e)], darken(hex_rgb(P.WARN), 0.1), 0.15 * s, a)
    D.stroke(c, [(bx, y_p), (x_e, y_e)], P.WARN, 0.10 * s, a)
    D.disc(c, bx, y_p, 0.09 * s, P.STEEL, a)
    D.disc(c, bx, y_p, 0.035 * s, darken(hex_rgb(P.STEEL), 0.5), a)
    D.disc(c, x_e, y_e, 0.07 * s, P.STEEL, a)
    # payload tool, hanging vertically from the arm end
    ttw = 0.34 * s
    y_tb = y_e - g.tool_len
    if tool == "pulling":
        D.steel(c, x_e - ttw / 2, y_tb + 0.12 * s, x_e + ttw / 2, y_e, P.PRIMARY_B, a)
        # skirt and dogs
        D.steel(c, x_e - ttw / 2 - 0.02 * s, y_tb, x_e - ttw / 2 + 0.05 * s, y_tb + 0.16 * s, P.STEEL_DK, a)
        D.steel(c, x_e + ttw / 2 - 0.05 * s, y_tb, x_e + ttw / 2 + 0.02 * s, y_tb + 0.16 * s, P.STEEL_DK, a)
        gi = 0.05 * s * grip
        for sd in (-1, 1):
            xd = x_e + sd * (ttw / 2 - 0.05 * s) - sd * gi
            D.poly(c, [(xd, y_tb + 0.06 * s), (xd - sd * 0.06 * s, y_tb + 0.03 * s), (xd, y_tb + 0.12 * s)], P.WARN, a)
    else:
        D.steel(c, x_e - ttw / 2, y_tb, x_e + ttw / 2, y_e, P.SAFE, a)
        D.disc(c, x_e, y_tb + 0.1 * s, 0.035 * s, P.BAD, a)
    return x_e, y_tb


def draw_straight_tool(c, look, x, y_bottom, s, a=1.0, wire_top=4.6):
    """A plain toolstring (stem + tool) for 'a straight tool passes it by'."""
    if a <= 0.003:
        return
    D.stroke(c, [(x, wire_top), (x, y_bottom + 2.2 * s)], P.WIRE, 0.03 * s, a)
    D.steel(c, x - 0.16 * s, y_bottom + 0.6 * s, x + 0.16 * s, y_bottom + 2.2 * s, P.STEEL_DK, a)
    D.steel(c, x - 0.22 * s, y_bottom, x + 0.22 * s, y_bottom + 0.6 * s, P.STEEL, a)


# ---------------------------------------------------------------------------------------------- plan view
def draw_plan(c, look, cx, cy, R, phi, kick=0.0, a=1.0, title="plan view"):
    """Top-down section through the mandrel: main bore circle, pocket circle, the tool with its arm direction and key."""
    if a <= 0.003:
        return
    D.flat(c, cx - 1.55 * R, cy - 1.35 * R, cx + 2.45 * R, cy + 1.55 * R, P.PANEL, 0.92 * a, r=0.1, edge=True)
    D.text(c, look, title, cx + 0.45 * R, cy + 1.3 * R, 0.14, P.MUTED, a, kind="bold")
    # mandrel outline: bore + pocket
    D.disc(c, cx, cy, R * 1.08, P.STEEL, a)
    D.disc(c, cx + 1.45 * R, cy, R * 0.62, P.STEEL, a)
    D.fill(c, cx, cy - R * 0.62, cx + 1.45 * R, cy + R * 0.62, P.STEEL, a)
    D.disc(c, cx, cy, R, darken(hex_rgb(P.BG), 0.3), a)
    D.disc(c, cx + 1.45 * R, cy, R * 0.5, darken(hex_rgb(P.BG), 0.3), a)
    D.text(c, look, "pocket", cx + 1.45 * R, cy - 0.85 * R, 0.13, P.MUTED, a)
    # tool
    tr = 0.62 * R
    D.disc(c, cx, cy, tr, P.STEEL_DK, a)
    D.ring(c, cx, cy, tr, 0.02, darken(hex_rgb(P.STEEL), 0.5), a)
    ux, uy = math.cos(phi), math.sin(phi)
    # key
    D.disc(c, cx + ux * tr * 1.08, cy + uy * tr * 1.08, 0.11 * R, P.WARN, a)
    # arm (folded: a short bar on the tool; kicked: reaches the pocket centre)
    reach = tr * 0.8 + kick * (1.45 * R - tr * 0.8)
    D.stroke(c, [(cx, cy), (cx + ux * reach, cy + uy * reach)], P.WARN, 0.07 * R, a)
    D.disc(c, cx + ux * reach, cy + uy * reach, 0.12 * R + 0.1 * R * kick, P.PRIMARY_B, a)
