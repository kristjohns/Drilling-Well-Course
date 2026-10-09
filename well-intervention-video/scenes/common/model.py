"""One illustrative well and the physics behind every number in the film.

The well is a *composite* subsea oil producer, not a real well. Every number the narration or a chart quotes comes from this
file, so pictures and voice cannot disagree. Units: metres, bar, newtons unless the name says otherwise.

  well path        vertical to 500 m, build to 55 deg by 1,400 m MD, hold 55 deg to the reservoir
  completion       5-1/2 in tubing in 9-5/8 in casing, DHSV, three gas-lift mandrels, sliding sleeve, packer, nipple, perfs
  forces           pressure acting on wire / coiled tube, buoyed weight, balance point (pipe-light -> pipe-heavy)
  buckling         Dawson-Paslay / Chen helical load, friction-limited reach of coiled tubing in a horizontal section
  gravity limit    angle at which a freely falling toolstring stops sliding (tan(angle) = 1 / friction)
"""
from __future__ import annotations
import math

# ---------------------------------------------------------------------------------------------- constants
G_BAR_PER_M_SG = 0.0980665
IN = 0.0254
STEEL_RHO = 7850.0
STEEL_E = 207e9
GRAV = 9.80665

WATER_DEPTH = 300.0
P_WELLHEAD = 200.0            # shut-in tubing head pressure at the tree, bar
P_RES = 310.0                 # reservoir pressure, bar
FLUID_SG = 1.0                # fluid in the hole for the buoyancy calculation

# ---------------------------------------------------------------------------------------------- well path (MD, m)
KOP, END_BUILD, ANGLE = 500.0, 1400.0, 55.0


def incl(md: float) -> float:
    """Inclination in degrees at measured depth md."""
    if md <= KOP:
        return 0.0
    if md >= END_BUILD:
        return ANGLE
    return ANGLE * (md - KOP) / (END_BUILD - KOP)


def tvd(md: float) -> float:
    if md <= KOP:
        return md
    a = math.radians(ANGLE)
    R = (END_BUILD - KOP) / a
    if md <= END_BUILD:
        th = math.radians(incl(md))
        return KOP + R * math.sin(th)
    return KOP + R * math.sin(a) + (md - END_BUILD) * math.cos(a)


def departure(md: float) -> float:
    if md <= KOP:
        return 0.0
    a = math.radians(ANGLE)
    R = (END_BUILD - KOP) / a
    if md <= END_BUILD:
        th = math.radians(incl(md))
        return R * (1 - math.cos(th))
    return R * (1 - math.cos(a)) + (md - END_BUILD) * math.sin(a)


# ---------------------------------------------------------------------------------------------- completion (MD, m)
DHSV_MD = 450.0
GL_MANDRELS = (1200.0, 2100.0, 3000.0)
SLEEVE_MD = 3550.0
PACKER_MD = 3650.0
NIPPLE_MD = 3720.0
TAIL_MD = 3800.0
PERFS_MD = (3900.0, 4100.0)
TD_MD = 4200.0

TUBING_OD_IN, TUBING_ID_IN = 5.5, 4.892
CASING_OD_IN, CASING_ID_IN = 9.625, 8.681
TUBING_ID_M = TUBING_ID_IN * IN

# ---------------------------------------------------------------------------------------------- slickline
WIRE_D_IN = 0.108


def wire_area_m2(d_in: float = WIRE_D_IN) -> float:
    return math.pi / 4 * (d_in * IN) ** 2


def wire_force_n(p_bar: float = P_WELLHEAD, d_in: float = WIRE_D_IN) -> float:
    """Force pushing a wire of diameter d out of a well at pressure p (stuffing box seal diameter = wire diameter)."""
    return p_bar * 1e5 * wire_area_m2(d_in)


def slide_angle_deg(mu: float) -> float:
    """Steepest inclination at which a free-falling tool still slides: along-hole weight W cos(i) = friction mu W sin(i)."""
    return math.degrees(math.atan(1.0 / mu))


# ---------------------------------------------------------------------------------------------- coiled tubing
CT_OD_IN, CT_WALL_IN = 2.0, 0.156


def ct_geom(od_in: float = CT_OD_IN, wall_in: float = CT_WALL_IN) -> dict:
    od, wall = od_in * IN, wall_in * IN
    idm = od - 2 * wall
    a_steel = math.pi / 4 * (od ** 2 - idm ** 2)
    I = math.pi / 64 * (od ** 4 - idm ** 4)
    return dict(od=od, id=idm, a_od=math.pi / 4 * od ** 2, a_steel=a_steel, I=I,
                w_air=a_steel * STEEL_RHO * GRAV, w_buoyed=a_steel * STEEL_RHO * GRAV * (1 - FLUID_SG * 1000 / STEEL_RHO))


def ct_push_force_n(p_bar: float = P_WELLHEAD, od_in: float = CT_OD_IN) -> float:
    """Pressure force trying to eject coiled tubing through the stripper: p x area of the outside diameter."""
    return p_bar * 1e5 * math.pi / 4 * (od_in * IN) ** 2


def balance_depth_m(p_bar: float = P_WELLHEAD, od_in: float = CT_OD_IN, wall_in: float = CT_WALL_IN) -> float:
    """Vertical depth of tubing in the hole whose buoyed weight equals the pressure force (the 'balance point')."""
    g = ct_geom(od_in, wall_in)
    return ct_push_force_n(p_bar, od_in) / g["w_buoyed"]


def ct_net_force_n(depth_m: float, p_bar: float = P_WELLHEAD) -> float:
    """Injector force at the stripper, + = pushing down. Vertical well, friction ignored."""
    g = ct_geom()
    return ct_push_force_n(p_bar) - g["w_buoyed"] * depth_m


def helical_load_n(od_in: float = CT_OD_IN, wall_in: float = CT_WALL_IN, bore_in: float = TUBING_ID_IN) -> float:
    """Chen/Cheatham helical buckling load of tubing lying on the low side of a horizontal pipe: sqrt(2) * 2 sqrt(E I w / r)."""
    g = ct_geom(od_in, wall_in)
    r = (bore_in - od_in) * IN / 2
    return math.sqrt(2) * 2 * math.sqrt(STEEL_E * g["I"] * g["w_buoyed"] / r)


def horizontal_reach_m(mu: float, **kw) -> float:
    """Length of horizontal hole in which friction alone consumes the helical buckling load (first estimate of reach)."""
    g = ct_geom()
    return helical_load_n(**kw) / (mu * g["w_buoyed"])


def ct_min_bend_strain(od_in: float = CT_OD_IN, radius_m: float = 1.1) -> float:
    """Outer-fibre bending strain on a reel core / gooseneck of the given radius (elastic-plastic ignored): r_outer / R."""
    return (od_in * IN / 2) / radius_m


if __name__ == "__main__":
    print(f"tubing ID {TUBING_ID_IN} in = {TUBING_ID_M * 1000:.1f} mm; well TD {TD_MD:.0f} m MD, TVD {tvd(TD_MD):.0f} m")
    for md in (DHSV_MD, *GL_MANDRELS, SLEEVE_MD, PACKER_MD, NIPPLE_MD, TAIL_MD, *PERFS_MD):
        print(f"  MD {md:6.0f}  TVD {tvd(md):6.0f}  incl {incl(md):4.1f}")
    f = wire_force_n()
    print(f"slickline {WIRE_D_IN} in ({WIRE_D_IN * IN * 1000:.2f} mm) at {P_WELLHEAD:.0f} bar: {f:.0f} N = {f / GRAV:.1f} kgf = {f * 0.2248:.1f} lbf")
    print(f"   at 345 bar: {wire_force_n(345):.0f} N")
    for mu in (0.2, 0.3, 0.4, 0.5):
        print(f"gravity limit, mu {mu}: {slide_angle_deg(mu):.1f} deg")
    g = ct_geom()
    print(f"CT {CT_OD_IN} in x {CT_WALL_IN} in: OD {g['od'] * 1000:.1f} mm ID {g['id'] * 1000:.1f} mm steel {g['a_steel'] * 1e6:.0f} mm2 "
          f"air {g['w_air']:.1f} N/m ({g['w_air'] / GRAV:.2f} kg/m) buoyed {g['w_buoyed']:.1f} N/m")
    F = ct_push_force_n()
    print(f"CT push force at {P_WELLHEAD:.0f} bar: {F / 1000:.1f} kN = {F / GRAV / 1000:.2f} tonnes-force; balance depth {balance_depth_m():.0f} m")
    print(f"   at 345 bar: {ct_push_force_n(345) / 1000:.1f} kN, balance {balance_depth_m(345):.0f} m")
    print(f"helical load {helical_load_n() / 1000:.1f} kN")
    for mu in (0.1, 0.2, 0.3, 0.4):
        print(f"  horizontal reach to helical onset, mu {mu}: {horizontal_reach_m(mu):.0f} m")
    for R in (0.8, 1.1, 1.4):
        print(f"bend strain radius {R} m: {ct_min_bend_strain(radius_m=R) * 100:.2f} % (elastic estimate)")
    print(f"friction pressure etc not modelled; lubricator stand-off: n/a")
