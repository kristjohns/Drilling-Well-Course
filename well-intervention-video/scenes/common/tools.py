"""Wireline and coiled-tubing tool drawings: vertical components stacked top-down, each returns NS(parts, h, ...).

All functions draw a component whose top edge is at y and whose centre line is x = cx, scaled by s. They are schematic (the
proportions are chosen to read on screen, not to be to scale).
"""
from __future__ import annotations
import math

from . import palette as P
from .kit import NS


def _rr(st, cx, y_top, w, h, color, z, role="steel", dx=0.0):
    return st.rect(cx + dx, y_top - h / 2, w, h, color, z, role=role)


def rope_socket(st, cx, y, s=1.0, z=0.7):
    """Rope socket: where the wire is tied off. A cone with a knot, over a body."""
    parts = [st.poly([(cx - 0.04 * s, y), (cx + 0.04 * s, y), (cx + 0.12 * s, y - 0.2 * s), (cx - 0.12 * s, y - 0.2 * s)], P.STEEL, z, role="flat"),
             st.circle(cx, y - 0.06 * s, 0.075 * s, P.WARN, z + 0.01, role="disc"),
             _rr(st, cx, y - 0.2 * s, 0.26 * s, 0.35 * s, P.STEEL_DK, z)]
    return NS(parts=parts, h=0.55 * s, w=0.26 * s)


def stem_bar(st, cx, y, s=1.0, z=0.7, h=1.4):
    """Weight bar (stem): a long heavy cylinder with machined bands."""
    body = _rr(st, cx, y, 0.3 * s, h * s, P.STEEL, z)
    bands = [st.rect(cx, y - 0.2 * s - k * 0.32 * s, 0.34 * s, 0.03 * s, P.STEEL_DK, z + 0.01, role="solid") for k in range(int((h - 0.3) / 0.32))]
    return NS(parts=[body] + bands, h=h * s, w=0.3 * s)


def jar_closed(st, cx, y, s=1.0, z=0.7):
    """Mechanical jar: an outer housing and an inner mandrel that slides (shown closed). Returns NS(parts, mandrel, housing, ...)."""
    housing = [_rr(st, cx, y - 0.2 * s, 0.34 * s, 0.9 * s, P.STEEL_DK, z)]
    mandrel = [_rr(st, cx, y, 0.18 * s, 0.5 * s, P.STEEL, z + 0.02), st.rect(cx, y - 0.55 * s, 0.26 * s, 0.14 * s, P.WARN, z + 0.03, role="solid")]
    return NS(parts=housing + mandrel, mandrel=mandrel, housing=housing, h=1.1 * s, w=0.34 * s)


def knuckle_joint(st, cx, y, s=1.0, z=0.7):
    """Knuckle joint: a ball-and-socket hinge."""
    parts = [_rr(st, cx, y, 0.2 * s, 0.14 * s, P.STEEL, z), st.circle(cx, y - 0.24 * s, 0.14 * s, P.STEEL_DK, z + 0.01, role="disc"),
             _rr(st, cx, y - 0.3 * s, 0.2 * s, 0.2 * s, P.STEEL, z)]
    return NS(parts=parts, h=0.5 * s, w=0.28 * s)


def running_tool(st, cx, y, s=1.0, z=0.7, color=P.PRIMARY_B):
    """Running / pulling tool: a body with a shear pin and dogs that engage the plug neck. Returns NS(parts, pin, dogs)."""
    body = _rr(st, cx, y, 0.3 * s, 0.7 * s, color, z, role="flat")
    pin = st.rect(cx, y - 0.3 * s, 0.38 * s, 0.05 * s, P.WARN, z + 0.02, role="solid")
    dogs = [st.rect(cx - 0.17 * s, y - 0.58 * s, 0.1 * s, 0.2 * s, P.STEEL, z + 0.02, role="steel"), st.rect(cx + 0.17 * s, y - 0.58 * s, 0.1 * s, 0.2 * s, P.STEEL, z + 0.02, role="steel")]
    return NS(parts=[body, pin] + dogs, pin=pin, dogs=dogs, h=0.75 * s, w=0.3 * s)


def toolstring(st, cx, y, s=1.0, z=0.7, include=("socket", "stem", "jar", "knuckle", "run")):
    """A stacked toolstring; returns NS(parts, h, by_name={name: NS}, y_bottom)."""
    parts, by, cur = [], {}, y
    for name in include:
        if name == "socket":
            c = rope_socket(st, cx, cur, s, z)
        elif name == "stem":
            c = stem_bar(st, cx, cur, s, z)
        elif name == "jar":
            c = jar_closed(st, cx, cur, s, z)
        elif name == "knuckle":
            c = knuckle_joint(st, cx, cur, s, z)
        elif name == "run":
            c = running_tool(st, cx, cur, s, z)
        else:
            continue
        by[name] = c
        parts += c.parts
        cur -= c.h
    return NS(parts=parts, by=by, h=y - cur, y_bottom=cur)


def plug_assembly(st, cx, y, s=1.0, z=0.6):
    """A plug on a lock mandrel: fishing neck on top, body, spring-loaded keys, sealing element and an equalising prong below.
    y = top of the fishing neck. Keys are drawn retracted (x = +-0.4 s); extend them by +-0.22 s. The keys sit 0.6 s below the neck top
    and the seal 1.35 s below it, so with the keys in a nipple groove the seal lies in the lower seal bore.
    Returns NS(parts, keys, neck, seal, y_keys, h, y_seal, prong, y_bottom)."""
    neck = [st.rect(cx, y - 0.2 * s, 0.2 * s, 0.3 * s, P.STEEL, z, role="steel"), st.rect(cx, y - 0.06 * s, 0.44 * s, 0.12 * s, P.STEEL, z, role="steel")]
    body = [st.rect(cx, y - 0.95 * s, 0.7 * s, 1.1 * s, P.STEEL_DK, z, role="steel")]
    seal = [st.rect(cx, y - 1.35 * s, 1.0 * s, 0.3 * s, P.RUBBER, z + 0.01, role="solid"), st.rect(cx, y - 1.35 * s, 1.0 * s, 0.3 * s, P.RUBBER_HI, z, alpha=0.4, role="flat")]
    y_keys = y - 0.6 * s
    keys = [st.rect(cx - 0.4 * s, y_keys, 0.1 * s, 0.34 * s, P.WARN, z + 0.02, role="solid"), st.rect(cx + 0.4 * s, y_keys, 0.1 * s, 0.34 * s, P.WARN, z + 0.02, role="solid")]
    prong = [st.rect(cx, y - 2.05 * s, 0.14 * s, 0.7 * s, P.STEEL, z + 0.02, role="steel")]
    return NS(parts=neck + body + seal + keys + prong, kobj=keys, neck=neck, seal=seal, y_keys=y_keys, h=2.4 * s, y_neck_top=y, y_bottom=y - 2.4 * s,
              y_seal=y - 1.35 * s, prong=prong)


def perf_gun(st, cx, y, s=1.0, z=0.6, n=3):
    """A perforating gun: a carrier tube with ports. Returns NS(parts, ports_y)."""
    h = (0.35 + 0.55 * n) * s
    body = st.rect(cx, y - h / 2, 0.5 * s, h, P.STEEL_DK, z, role="steel")
    ports, ys = [], []
    for i in range(n):
        yy = y - (0.35 + 0.55 * i) * s
        ports.append(st.rect(cx, yy, 0.52 * s, 0.1 * s, P.WARN, z + 0.02, role="solid"))
        ys.append(yy)
    return NS(parts=[body] + ports, ports_y=ys, h=h, w=0.5 * s)
