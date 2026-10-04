# Ch 4: Drilling the deep sections
BUDGET: 180

## 4.01 | 28 | anim
VO: At the bottom of the drill string is the bottom-hole assembly, the BHA: the bit, a steering tool, instruments, and heavy steel drill collars. Here is a surprise for a mechanical engineer. We drill by pulling. The pipe hangs in tension, and the collars push the bit down. Push with the pipe instead, and a slender column would buckle.
SHOT: Vertical drill string drawn full height: tension (blue arrows) in the long drill pipe, a neutral point marker, compression (red arrows) in the collars at the bottom with the bit. A ghost second string pushed from the top buckles into a sine shape and is crossed out.
FLAGS: GEN
TERMS: bottom-hole assembly; drill collar

## 4.02 | 33.5 | anim
VO: Modern PDC bits cut by shearing, like a lathe tool, with diamond cutters. To steer, we need a bend. A mud motor with a bent housing steers when we stop turning the pipe and just slide. A rotary steerable tool steers while the whole string turns. Why steer at all, what we call directional drilling? To hit a target that is not straight below, and to stay clear of other wells.
SHOT: Close-up of a PDC bit shearing a rock layer. Then two panels: (a) bent-housing motor: slide mode curves the path, rotate mode averages the bend out to a straight path; (b) rotary steerable: a pad pushes sideways on the wall while the string spins. Overhead map shows a well deviating from the rig position to an offset target around a neighbour well.
FLAGS: GEN; SIM: our example well is nearly vertical; steering is shown as concept only
TERMS: PDC bit; mud motor; rotary steerable system; directional drilling

## 4.03 | 32.5 | anim
VO: A curved hole has a cost. Drag in a bend acts like a rope around a capstan: it grows exponentially with the wrapped angle. The sharpness of the bend, the dogleg severity, also bends the pipe every time it turns, so we limit it. To know where we are, measurement-while-drilling sensors in the string measure inclination and direction, but every survey has an error ellipse that grows with depth.
SHOT: A rope round a capstan with the equation T2 = T1 e^(mu theta) drawn after the picture; then a deviated well in 3D-ish side view with drag arrows. A dogleg zoom with a bend radius. A plan-view uncertainty ellipse that grows along the well path.
FLAGS: GEN; SIM: friction factor and dogleg numbers are illustrative
TERMS: dogleg severity; measurement while drilling

## 4.04 | 22 | anim
VO: Meanwhile the mud is the hardest-working part of the system. It holds back the formation. It carries cuttings up. It cools the bit, and carries signals to the surface. It may be water-based or oil-based, and it gets its weight from barite, a dense mineral powder.
SHOT: Cutaway annulus with four labelled panels in turn: pressure arrows on the wall; cuttings rising in the stream; cool/lubricate at the bit; pulses travelling up the pipe. A barite particle cloud in a beaker raises the level on a density gauge.
FLAGS: GEN; NO; VERIFY: environmental discharge rules for oil-based cuttings on the NCS are regulation-specific and were not checked; none are cited
TERMS: barite; water-based mud; oil-based mud

## 4.05 | 32 | anim
VO: Now the twist. With the pumps on, the mud has to push its way up the narrow gap around the pipe. Friction adds pressure at the bottom. So bottom-hole pressure is higher while we pump than when we stop. That is the equivalent circulating density, ECD. And it means that every time we stop the pumps to add a pipe, a connection, the pressure at the bottom drops.
SHOT: Annulus cutaway with a bottom-hole pressure gauge. Pumps ON: friction arrows along the annulus, gauge reads high; pumps OFF at a connection: friction vanishes, gauge drops, a step trace on a pressure-vs-time chart. Equation after the animation: ECD = MW + friction pressure / (g x depth).
FLAGS: GEN; SIM: Newtonian-style friction picture; real annular hydraulics use Herschel-Bulkley rheology
TERMS: equivalent circulating density; connection

## 4.06 | 32 | anim
VO: So the real window is squeezed from both sides. With the pumps off, pressure must still beat the pore pressure. With the pumps on, it must stay under the fracture limit. Sometimes no mud weight does both. Managed pressure drilling, MPD, adds a knob: seal the top of the annulus, route the mud through a choke, and add back pressure when the pumps stop, holding bottom-hole pressure steady.
SHOT: The window chart returns: two horizontal markers (pumps-off BHP, pumps-on ECD) wiggle between pore and fracture curves and touch the limits. Then the MPD schematic: a sealed annulus, a choke on the return line; as the pump trace drops, the choke closes and the BHP trace stays flat.
FLAGS: GEN; NO; VERIFY: NORSOK D-010 treatment of managed pressure drilling (dedicated section in Rev 5?) not confirmed; SIM: MPD variants collapsed into one concept
TERMS: managed pressure drilling; choke; back pressure
