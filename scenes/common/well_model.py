"""Single source of truth for the *illustrative* composite well used in every chapter.

Nothing here is a real well. Every number is [SIM]: chosen to be physically coherent and
typical-looking for a North Sea HPHT-lite wildcat. Narration, charts and Blender scenes all
read from this module so they cannot disagree.

Units: depths in metres TVD below mean sea level (vertical well; rig-floor air gap ignored),
pressures in bar, densities / gradients as equivalent mud weight in sg (1 sg = 0.0981 bar/m).
"""
from __future__ import annotations
import bisect
from dataclasses import dataclass

G = 0.0981  # bar per metre per sg

WATER_DEPTH = 300.0   # seabed depth below sea level, m
TD = 4200.0           # total depth, m
RES_TOP = 3950.0      # top of reservoir sandstone
RES_BASE = 4110.0     # base of the sand: water leg below the free-water level (4,052 m) is ~58 m thick
GOC, FWL = 3990.0, 4052.0   # gas-oil contact, free-water level (pressure-defined)
OWC = 4046.0          # oil-water contact is slightly above FWL (capillary transition) [SIM]
SAND_A = (2980.0, 3000.0)   # thin overpressured overburden sand with flow potential (P&A, Ch 9)

# Pore pressure and fracture gradient as EMW (sg) vs depth. Piecewise linear. [SIM]
_PP = [(300, 1.03), (2400, 1.06), (3300, 1.40), (3900, 1.55), (4200, 1.54)]
_FG = [(300, 1.20), (1000, 1.50), (2000, 1.62), (3000, 1.69), (4200, 1.76)]
# Wellbore-collapse (shear failure) lower limit, sg. Below pore pressure in this basin. [SIM]
_CO = [(300, 0.95), (2400, 1.00), (3300, 1.30), (3900, 1.45), (4200, 1.46)]


def _interp(tab, z):
    xs = [p[0] for p in tab]
    if z <= xs[0]:
        return tab[0][1]
    if z >= xs[-1]:
        return tab[-1][1]
    i = bisect.bisect_right(xs, z)
    (x0, y0), (x1, y1) = tab[i - 1], tab[i]
    return y0 + (y1 - y0) * (z - x0) / (x1 - x0)


def pp(z):  # pore pressure, sg EMW
    return _interp(_PP, z)


def fg(z):  # fracture gradient, sg EMW
    return _interp(_FG, z)


def collapse(z):  # shear-collapse pressure, sg EMW
    return _interp(_CO, z)


def lower_limit(z):  # what the mud must beat: max(pore, collapse)  [Ch1: [SIM] drawn as pore only in beat 1]
    return max(pp(z), collapse(z))


def bar(z, sg):  # hydrostatic pressure of an sg column at depth z (from sea level), bar
    return sg * G * z


# ---- bottom-up casing design (Ch 1) ------------------------------------------------------
TRIP_ECD_MARGIN = 0.07   # sg added to pore pressure for mud weight (trip + ECD allowance) [SIM]
FRAC_MARGIN = 0.03       # sg below fracture the shoe LOT must clear [SIM]
KICK_HEIGHT = 150.0      # m of gas influx used for the simple kick-tolerance term [SIM]
RHO_GAS = 0.25           # sg, gas at depth [SIM]
MIN_SURFACE_SHOE = 1000.0  # shallow hazards + BOP anchor: surface casing no shallower [SIM]


def required_shoe_emw(z, mw_next):
    """Fracture strength needed at a shoe at depth z to drill the next section with mud weight mw_next."""
    return mw_next + FRAC_MARGIN + KICK_HEIGHT * (mw_next - RHO_GAS) / z


def design_bottom_up(td=TD, step=10.0, min_surface=MIN_SURFACE_SHOE):
    """Walk up from TD. Returns list of dicts, deepest first: section TD, mud weight, shoe depth.

    Shoe = shallowest depth where fg(z) >= required_shoe_emw(z, MW of the section below it)."""
    steps, bottom = [], td
    while True:
        mw = max(pp(z) for z in range(int(WATER_DEPTH), int(bottom) + 1, 10)) + TRIP_ECD_MARGIN
        mw = round(mw, 2)
        z = bottom - step
        # walk up while the shallower depth is still strong enough
        while z > WATER_DEPTH + 10 and fg(z) >= required_shoe_emw(z, mw):
            z -= step
        shoe = z + step
        steps.append(dict(section_td=bottom, mw=mw, shoe_calc=shoe))
        if shoe <= min_surface:
            steps[-1]["shoe"] = min_surface
            steps[-1]["constrained"] = "surface casing no shallower than shallow-hazard / BOP anchor depth"
            break
        steps[-1]["shoe"] = shoe
        bottom = shoe
    return steps


# ---- the resulting (rounded) casing programme --------------------------------------------
@dataclass(frozen=True)
class String:
    name: str       # e.g. "30in conductor"
    od_in: float
    hole_in: float
    top: float      # m (0 = seabed hung from wellhead)
    shoe: float     # m
    role: str


def _ceil50(x):
    """Round DEEPER to the next 50 m: a shoe set deeper than the calculated minimum is still strong enough."""
    return float(50 * -(-x // 50))


def programme():
    s = design_bottom_up()
    shoes = sorted(_ceil50(d["shoe"]) for d in s)   # shallowest first: surface, intermediate, ... deepest
    # conductor shoe is soil-driven (pile design), not pressure-driven.
    conductor = WATER_DEPTH + 90.0
    assert len(shoes) == 3, f"expected 3 pressure-designed strings, got {shoes}"
    return [
        String("30in conductor", 30.0, 36.0, WATER_DEPTH, conductor, "foundation / structural (soil-driven)"),
        String("20in surface casing", 20.0, 26.0, WATER_DEPTH, shoes[0], "anchors BOP, isolates shallow hazards"),
        String("13-3/8in intermediate", 13.375, 17.5, WATER_DEPTH, shoes[1], "isolates normal-pressure section"),
        String("9-5/8in intermediate", 9.625, 12.25, WATER_DEPTH, shoes[2], "isolates overpressure ramp"),
    ]


HOLE_TD_IN = 8.5   # reservoir section, drilled open hole to TD


def check_programme():
    """Every rounded shoe must still satisfy the design rule for the section drilled below it."""
    strings = [st for st in programme() if "conductor" not in st.name]
    below_td = [st.shoe for st in strings[1:]] + [TD]
    for st, td_below in zip(strings, below_td):
        mw = round(max(pp(z) for z in range(int(WATER_DEPTH), int(td_below) + 1, 10)) + TRIP_ECD_MARGIN, 2)
        need = required_shoe_emw(st.shoe, mw)
        assert fg(st.shoe) >= need - 1e-9 or st.shoe == MIN_SURFACE_SHOE, (st, mw, need, fg(st.shoe))
    return True


def section_mud_weights():
    """Mud weight used while drilling the open hole below each shoe (sg), keyed by section label."""
    strings = [st for st in programme() if "conductor" not in st.name]
    tds = [st.shoe for st in strings[1:]] + [TD]
    out = {}
    for st, td in zip(strings, tds):
        out[st.name] = round(max(pp(z) for z in range(int(WATER_DEPTH), int(td) + 1, 10)) + TRIP_ECD_MARGIN, 2)
    return out

if __name__ == "__main__":
    for d in design_bottom_up():
        print(d)
    for st in programme():
        print(st)
    print("check_programme:", check_programme())
    print("mud weights below each shoe:", section_mud_weights())
    print("hydrostatic at TD with 1.62 sg:", round(bar(TD, 1.62), 1), "bar; pore at reservoir top:", round(bar(RES_TOP, pp(RES_TOP)), 1), "bar")
