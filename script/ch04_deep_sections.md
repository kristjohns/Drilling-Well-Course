# Ch 4: Drilling the deep sections
BUDGET: 180

## 4.01 | 39.5 | anim
VO: At the bottom of the drill string is the bottom-hole assembly, the BHA: the bit, a steering tool, measurement sensors, and heavy steel drill collars. A puzzle: we need tonnes of force on the bit. Do we push from the rig? [pause 1.5] No. The rig holds the pipe back. It hangs in tension, like a plumb line, and only part of the heavy collars' weight rests on the bit. In a vertical hole, push down with the slender pipe instead and it would buckle, so we keep the compression in the collars.
SHOT: Vertical drill string drawn full height with the hook at the top: tension (blue arrows) in the long drill pipe, a neutral point marker about 80 % of the way up the collars, compression (red arrows) in the collars at the bottom with the bit. Puzzle beat: a ghost string pushed from the top buckles into a sine shape and is crossed out. A weight-on-bit gauge shows only part of the collar weight on the bit.
FLAGS: GEN
TERMS: bottom-hole assembly; drill collar

## 4.02 | 46.5 | anim
VO: Why steer at all? To reach a target that is not straight below, to stay clear of other wells, and, in a vertical wildcat like ours, to keep the hole straight. That is directional drilling. To steer, we tilt the bit or push it sideways. A mud motor, driven by the mud flowing through it, has a slight bend in its housing: stop turning the pipe and just slide, and the hole curves. A rotary steerable tool pushes pads against the wall, so it steers while the whole string turns. At the tip, a PDC bit, polycrystalline diamond compact, shears rock with diamond cutters, like a lathe tool.
SHOT: Overhead map: a well deviating from the rig position to an offset target around a neighbour well; then a vertical well kept straight. Steering panels: (a) bent-housing motor: one continuous path, straight while rotating, curving while sliding (toolface arrow), straight again on the new tangent; (b) rotary steerable: pads push sideways on the wall while the string spins. Close-up of a PDC bit shearing a rock layer like a lathe tool.
FLAGS: GEN; SIM: our example well is nearly vertical; steering is shown as concept only
TERMS: directional drilling; mud motor; rotary steerable system; PDC bit

## 4.03 | 49.5 | anim
VO: A curved hole has a cost. Pulling pipe through a bend is like a rope around a capstan: the tension needed multiplies by e to the mu theta, where theta is the total angle the hole turns through. The sharpness of the bend, in degrees per thirty metres, is the dogleg severity. Pipe rotating through a sharp bend is flexed back and forth on every turn, which breeds fatigue cracks, so we limit it. To know where we are, measurement-while-drilling sensors, MWD, measure the hole's inclination and direction, and we compute the path from those angles. Each survey carries a small error, so the uncertainty in our position, an ellipse, grows the farther we drill.
SHOT: A rope round a capstan with the equation T2 = T1·e^(μθ) after the picture (T2 > T1); then a deviated well with drag arrows and θ marked as the total turn. A dogleg zoom: "° per 30 m", with a rotating pipe flexing (alternating tension/compression on its outer fibre). A plan-view uncertainty ellipse that grows along the well path, computed from survey stations.
FLAGS: GEN; SIM: friction factor and dogleg numbers are illustrative
TERMS: dogleg severity; measurement while drilling

## 4.04 | 40.5 | anim
VO: Meanwhile the mud is the hardest-working part of the system. Its weight holds back the formation fluids and props up the wall, which it seals with a thin filter cake. It carries cuttings up, cools the bit, and carries signals to the surface. It may be water-based, or oil-based in deep sections, and most of its extra weight comes from barite, a mineral powder about four times as dense as water. On the Norwegian shelf, cuttings coated in oil-based mud may not be dumped at sea: they are shipped to shore or injected underground.
SHOT: Cutaway annulus with panels in turn: pressure arrows on the wall and a thin filter-cake layer on the permeable sand; cuttings rising in the stream (flow particles); cool/lubricate at the bit; pulses travelling up the pipe. A barite cloud in a beaker raises a density gauge (4.2 sg barite). A skip of oily cuttings goes onto a supply boat instead of overboard.
FLAGS: GEN; NO; VERIFY: the NCS ban on discharging oil-based-mud cuttings (OSPAR Decision 2000/3, Norwegian activities rules) is from memory, not checked against the primary text
TERMS: filter cake; water-based mud; oil-based mud; barite

## 4.05 | 36 | anim
VO: Now the twist. With the pumps on, the mud has to push its way up the narrow gap around the pipe. Friction adds pressure at the bottom. So bottom-hole pressure is higher while we pump than when we stop. Expressed as an equivalent mud weight, that pumping pressure is the equivalent circulating density, ECD. And every time we stop the pumps to screw on another stand of pipe, about twenty-eight metres, a pause drillers call a connection, the pressure at the bottom drops.
SHOT: Annulus cutaway with a bottom-hole pressure gauge (counter). Pumps ON: flow particles and friction arrows along the annulus, gauge reads high; pumps OFF at a connection: friction vanishes, gauge drops, a step trace on a pressure-vs-time chart (ECD trace amber, static line dashed amber). Equation after the animation: ECD = MW + annular friction ΔP / (g · TVD).
FLAGS: GEN; SIM: Newtonian-style friction picture; real annular hydraulics use Herschel-Bulkley rheology
TERMS: equivalent circulating density; connection

## 4.06 | 47 | anim
VO: So the real window is squeezed from both sides. With the pumps off, or worse, while pulling pipe out, pressure must still beat the pore pressure. With the pumps on, it must stay under the fracture limit at the weakest point, usually the last casing shoe. In a narrow window, sometimes no mud weight does both. Managed pressure drilling, MPD, adds a knob. A rotating seal closes the top of the annulus around the turning pipe, the returns go through a choke, and when the pumps stop the choke adds back pressure at the surface, holding bottom-hole pressure steady. Then the mud alone is no longer the whole barrier.
SHOT: The window chart returns, zoomed on the open hole below the 9⅝ in shoe (3,400 m to TD): pumps-off marker at 1.62 sg, pumps-on (ECD) marker at ~1.67 sg, both amber; "weakest point: shoe at 3,400 m, 1.71 sg" tick. A hypothetical narrower window shows the two markers unable to fit ("sometimes no mud weight does both"). Then the MPD schematic: a rotating seal on top of the annulus, a choke on the return line; as the pump trace drops, the choke back-pressure trace rises and the BHP trace stays flat.
FLAGS: GEN; NO; VERIFY: NORSOK D-010 treatment of managed pressure drilling (dedicated section in Rev 5?) not confirmed; SIM: MPD variants collapsed into one concept
TERMS: managed pressure drilling; back pressure
