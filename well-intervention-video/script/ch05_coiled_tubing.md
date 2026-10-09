# Ch 5: Coiled tubing: a pipe on a reel
BUDGET: 540

## 5.01 | 57 | anim
VO: Coiled tubing is a continuous steel pipe, with no joints, from one to three and a half inches across, wound on a reel. One reel can hold from about one and a half to over seven kilometres. It is made from flat steel strip, rolled into a tube and welded along the seam, and the strips are welded end to end at a slant, so the length is continuous. The steel is strong, with a yield strength of eighty thousand pounds per square inch or more, yet it bends round the reel without breaking. And because it is a pipe, we can pump through it. A wireline can carry. A coiled tube can carry, push, and pump.
SHOT: Manufacturing in three stages drawn left to right: flat strip coil unrolling, forming rolls curling it into a tube with an induction seam weld spark, strips butt-welded end-to-end at a slant (diagonal weld seam zoom), then the finished pipe winding onto a big reel (the reel fills with turns; length counter to 5,000 m). A cutaway of the tube cross-section: wall 3.96 mm. Three capability pills: CARRY, PUSH, PUMP, the last two highlight in a different colour.
FLAGS: GEN; SIM: manufacturing steps simplified; VERIFY: reel capacities (about 1.5 to 7.6 km) and size range (0.75 to 3.5 in) are manufacturer-level ranges from search summaries
TERMS:

## 5.02 | 47.5 | anim
VO: Here is a coiled tubing spread. The reel stands on the deck. From the reel the tube rises over the gooseneck, a curved guide, and straight down into the injector head, which hangs from a crane or a frame above the tree. Under the injector comes the stripper, which seals around the moving pipe, then a stack of blowout preventers, then the lubricator, then the tree. The operator sits in a control cabin, watching pressure, depth, weight and pump rate. A pump connects to the centre of the reel, and the fluid goes out through the tube.
SHOT: Full side elevation. The reel with a core and turns, a pump-and-swivel at its hub, an arc-shaped gooseneck above the injector, the injector head (box with two chain loops), stripper, BOP stack, lubricator, tree on top of the well. The tube path draws on in glowing steel from the reel over the gooseneck and down. Labels pop as each part is named. A control cabin to the left with gauges. A small pump unit with an arrow to the reel hub. Fluid particles flow down the tube.
FLAGS: GEN; SIM: arrangement schematic; offshore units are skid-mounted and use a crane or a frame to carry the injector
TERMS: injector head; gooseneck; stripper

## 5.03 | 41 | anim
VO: The injector head is the engine. Two endless chains run on opposite sides of the tube, each carrying gripper blocks shaped to its diameter. Hydraulic cylinders squeeze the chains together onto the pipe. Turn the chains one way and the pipe is driven into the well. Turn them the other way and it comes out. The injector can hold the pipe still against the well pressure, or pull the whole weight of a long string, tens of tonnes. Everything depends on the grip.
SHOT: Close-up of the injector: two chain loops with gripper blocks (moving procedurally), a squeezing hydraulic cylinder pair with arrows, the tube between them. Block motion reverses on cue (push in / pull out) with arrows and a force gauge. A red slip marker if the grip is lost (not shown as failing).
FLAGS: GEN; SIM: block count and cylinder positions simplified
TERMS:

## 5.04 | 51.5 | anim
VO: Below the injector, the stripper is a set of rubber elements squeezed around the tube by hydraulic pressure. It is the dynamic seal, the same job as the stuffing box, and like it, it wears. Below the stripper comes the blowout preventer, usually with four sets of rams in a stack. From the top: blind rams, which seal an empty hole; shear rams, which cut the tube; slip rams, which grip it so it cannot fall; and pipe rams, which seal around it. In an emergency they close in sequence: pipe rams to seal, slips to hold, shear to cut, blind to seal the bore.
SHOT: Cutaway stripper (rubber ring squeezed by a piston around the tube; wear) then the quad BOP stack in the order given with the tube through it. Closing animation, step by step with a number badge: 1 pipe rams close and seal around the tube (rubber faces), 2 slip rams grip, 3 shear rams cut the tube (upper tube lifts away), 4 blind rams close and seal the empty bore.
FLAGS: GEN; VERIFY: the conventional quad stack order (blind, shear, slip, pipe from the top) and the closing sequence is from industry-practice summaries, not read from API 16ST
TERMS:

## 5.05 | 46.5 | anim
VO: At the end of the tube hangs the bottom hole assembly. First a connector, which fixes it to the tube. Then check valves, two flaps that only open for flow going down, so that well fluid cannot come up the inside of the tube. Then a disconnect, which can release everything below if it gets stuck: drop a ball, pump it down, and pressure parts the tool. Then the working tool itself: a jetting nozzle, a motor and mill, an inflatable packer, a perforating gun, a logging tool. Same tube, different tool on the end.
SHOT: Vertical exploded BHA assembling top to bottom: connector (dimple/roll-on), dual flapper check valves (cutaway with flaps closing under upward flow, opening under downward flow), hydraulic disconnect (ball drops, seat shifts, collet parts), then a carousel of working tools swapping on the bottom (nozzle, motor+mill, packer, gun, logging tool).
FLAGS: GEN; SIM: BHA length and components vary with the job
TERMS: bottom hole assembly

## 5.06 | 46 | anim
VO: Now the physics. With the well open at two hundred bar, the pressure pushes the tube out with that force of about four tonnes. At first, the tube in the hole weighs almost nothing, so the injector has to push it in. As more goes in, its weight, reduced by buoyancy, grows. About a kilometre of two-inch tube is enough to balance the push. Beyond that, the tube is heavy, and the injector holds it back instead of pushing. That crossover is called the balance point, and the whole operation is planned around it.
SHOT: Left: vertical hole with the tube going in, a depth counter, arrows for the pressure push (red, up) and the buoyed weight (blue, down) with the injector between. Right: a chart of injector force vs depth: starts at +40.5 kN (push), falls linearly (slope 39 N per m), crosses zero at 1,035 m ("balance point"), continues into negative (hold-back). The current depth dot moves as the tube goes in; the injector arrow flips from push to hold at the crossing.
FLAGS: GEN; SIM: vertical well, 1.0 sg fluid, 2 in x 0.156 in tube, 200 bar, friction ignored; real jobs add stripper friction and well deviation
TERMS: balance point

## 5.07 | 58.5 | anim
VO: Coiled tubing has an unusual enemy: it gets tired. Every time it comes off the reel it is bent over the gooseneck, then straightened into the injector. Going in and coming out, that is at least six bends and straightenings every trip. Each bend takes the steel past its yield point, a couple of percent of strain, so the steel flows plastically. A paperclip bent back and forth breaks in a few cycles; steel tubing lasts far longer, but not for ever. Internal pressure makes it worse. So every string has a fatigue life, tracked by software that logs each cycle and each pressure, and the string is retired well before it is used up, commonly at about eighty percent.
SHOT: Side view of the tube leaving the reel, bending over the gooseneck, straightening into the injector: strain colour heat map on the bending zones (outer fibre red). A cycle counter ticking 1..6 per trip. A life bar fills across several trips (green -> amber -> red) with a retirement tick at 80 percent. A second small chart: life drops as internal pressure rises (two curves, low and high pressure).
FLAGS: GEN; SIM: strain values are elastic estimates (outer fibre radius over bend radius: about 2.3 percent at a 1.1 m radius); the cycle count of six is the commonly cited minimum; SEEN: the practice of retiring a string at about 80 percent of its estimated fatigue life is from a patent text
TERMS: fatigue life

## 5.08 | 60 | anim
VO: The other limit is reach. In a horizontal well, you push the tube along the low side of the hole. Friction builds along its length, and the tube feels a compressive load, like pushing a rope. At a certain load the tube buckles, first into a gentle wave, then into a helix that presses hard against the wall. The friction then climbs steeply, and however hard the injector pushes, no more tube goes in. That is lock-up. How far you get depends strongly on friction: in our example, a friction coefficient of 0.3 gives roughly fourteen hundred metres, and 0.1 gives over four thousand. So engineers add lubricants, run a larger and stiffer tube, or add a tractor or a vibrating tool.
SHOT: Horizontal well section (casing tube) with coiled tube being pushed in from the left: initially straight, then sinusoidal waves appear at the far end, then a helix forms and tightens; force and friction arrows; the injector arrow grows but the tube stops. A bar chart: reach vs friction coefficient (0.1: 4,305 m, 0.2: 2,153 m, 0.3: 1,435 m, 0.4: 1,076 m) drawn from the model. Three remedy icons appear: lubricant, tapered wall, tractor/vibrator.
FLAGS: GEN; SIM: the reach is the length of horizontal hole at which friction alone consumes the helical buckling load (Chen/Cheatham) for a 2 in tube in 5.5 in tubing with 1.0 sg fluid; lock-up reach is longer but the first estimate is the planning number, and tubing grade, curvature and fluid add to the picture
TERMS: lock-up

## 5.09 | 52 | anim
VO: Because the tube is hollow, coiled tubing can circulate. To clean out sand, we run in with a jetting nozzle, pump fluid down the tube, and the fluid returns up the annulus between tube and tubing, carrying the sand. What matters is the speed of that upward flow. Too slow, and the sand falls out again. Fast enough, and it travels to the surface. If the reservoir is too weak to lift the fluid, we add nitrogen to make a foam. And friction in a long, narrow tube limits the pump rate, so the size of the tube is always a trade between strength and flow.
SHOT: Tubing cutaway with sand fill (gold) over the perforations; coiled tube with nozzle jets stirs the sand into suspension; flow particles go down the tube and up the annulus carrying sand grains to the top (return line to a separator). Annular velocity gauge with a threshold band: grains settle below, rise above. A nitrogen (grey) bubble foam variant. A small inset trade chart: tube ID versus friction pressure.
FLAGS: GEN; SIM: no numbers on velocity; sand transport depends on grain size, fluid viscosity and well angle
TERMS:

## 5.10 | 47.5 | anim
VO: Three more jobs. Nitrogen lift: nitrogen pumped down the tube displaces the heavy liquid in the well. The column lightens, and the reservoir can start to flow again. Acid placement: the nozzle sits at the right depth, pumping acid across the perforations while the tube is moved up and down, so every part is treated. And scale removal. A jet of water or acid washes soft scale off the wall; hard scale needs a mill. A mill is turned by a downhole motor, driven by the fluid we pump, so the tube itself never has to rotate.
SHOT: Three panels in turn. (1) Nitrogen lift: the tube displaces the column from the bottom; liquid level falls, the column pressure gauge drops, production arrows start. (2) Acid placement: the nozzle moves up and down across the perforation zone; the acid front (lime) spreads into each perforation evenly, with a coverage bar. (3) Scale: jet vs mill: a motor (rotor/stator cutaway with fluid spinning the rotor) with a mill head cutting a hard scale plug; scale chips fall. A "tube does not rotate" note with a straight arrow.
FLAGS: GEN; SIM: panels are generic
TERMS:

## 5.11 | 32.5 | anim
VO: Coiled tubing also sets plugs and packers, perforates, and pushes a logging tool into a horizontal well where gravity fails. It places cement, and fishes. Hang a string inside the tubing and it becomes a velocity string. Add a downhole motor and a bit and it will even drill: coiled tubing drilling cuts a side-track out of an existing well, through its tubing, without a rig.
SHOT: Six small tiles pop in a 3x2 grid: setting a plug, perforating, logging in a horizontal well, cement squeeze, fishing, velocity string. Then a larger tile: a sidetrack kicking out of a window in the casing, with a thin tube-and-motor drilling the new branch.
FLAGS: GEN; VERIFY: coiled tubing drilling through tubing is shown as a capability; the practicality depends on well and size
TERMS:
