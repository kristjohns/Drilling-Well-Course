"""Shared colour palette (sRGB hex). One meaning per colour, used identically in every chapter.

Intervention additions: ACID lime, N2 grey-blue (nitrogen / foam), GREASE butter yellow (seal grease), SCALE off-white,
WAX tan, HYDRATE pale ice, KILL amber-brown (heavy kill fluid), WIRE light steel, COPPER (conductor / shaped-charge liner),
RUBBER near-black elastomer.

Fluid convention follows the oilfield norm (water blue, oil green, gas crimson). Pressure curves use
the same hues as the fluids they represent so the viewer never has to re-learn a legend:
  pore pressure  = formation-water blue      fracture limit = orange
  mud / ECD      = amber                      safe window     = green wash
D-010 barrier outlines (primary blue / secondary red) are drawn ONLY in the flat 'barrier schematic' panel
style (outline-only), so they cannot be confused with fluids.
"""

BG        = "#0b1220"   # deep navy background
PANEL     = "#141d30"   # card / chart background
PANEL2    = "#1c2742"   # raised panel
GRID      = "#2b3a5c"   # chart grid / ticks
TEXT      = "#e8eef6"   # primary text
MUTED     = "#8fa0bd"   # secondary text
OUTLINE   = "#05080f"

SEA       = "#123a6b"
SEABED    = "#7a6a52"
ROCK      = "#5b4d3f"
ROCK2     = "#6e5d4b"
SAND      = "#c8a96a"   # reservoir sandstone
SHALE     = "#4a4540"

STEEL     = "#c4d0de"   # casing / pipe
STEEL_DK  = "#7f8da1"
CEMENT    = "#b9b2a6"
MUD       = "#ffb703"   # drilling fluid (amber)
KILL_MUD  = "#c77d00"
SPACER    = "#e9ecef"

WATER     = "#3a86ff"   # formation water / pore pressure
PORE      = "#4cc9f0"   # pore-pressure curve (light water blue)
OIL       = "#4caf50"
GAS       = "#e5446d"
FRAC      = "#ff6f3c"   # fracture limit
COLLAPSE  = "#9b5de5"   # shear-collapse limit
SAFE      = "#2a9d8f"   # window fill / OK / verified
WARN      = "#ffd166"
BAD       = "#ef476f"

PRIMARY_B = "#4895ef"   # D-010 primary barrier outline (barrier panels only)
SECOND_B  = "#f25c54"   # D-010 secondary barrier outline (barrier panels only)

NO_BADGE  = "#d62839"   # Norway-specific badge
SIM_BADGE = "#ffd166"

# --- intervention additions
ACID      = "#a3e635"   # acid / treatment fluid
N2        = "#9fb0c8"   # nitrogen, foam
GREASE    = "#efe08a"   # seal grease (grease injection head)
SCALE     = "#e8e4d8"   # mineral scale
WAX       = "#c9a77a"   # wax / paraffin
HYDRATE   = "#bfe9ff"   # gas hydrate
WIRE      = "#d6dde8"   # wireline / slickline
COPPER    = "#d98c5f"   # conductor, liner
RUBBER    = "#272b35"   # elastomer
RUBBER_HI = "#a8b3c6"
