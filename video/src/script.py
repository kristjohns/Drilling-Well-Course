"""Narration script, split into scenes and beats.

Each beat is one TTS clip. Animation keyframes are tied to beat start times,
so visuals stay in sync with the voice-over even if the wording changes.

`say` is what the voice reads (spelled for pronunciation);
`text` is the clean on-screen / subtitle version (defaults to `say`).
"""

SCENES = [
    # ------------------------------------------------------------------ 1
    dict(id='s01_intro', title='Intro', beats=[
        ('hook1', "Three kilometers beneath the floor of the North Sea lies a layer of sandstone. "
                  "Its pores are filled with oil and gas, trapped there for millions of years."),
        ('hook2', "To reach it, we have to drill a hole barely wider than a dinner plate, through "
                  "hundreds of meters of seawater, and kilometers of solid rock."),
        ('hook3', "We have to do it without ever losing control of the enormous pressures down there."),
        ('hook4', "And when the well has done its job, decades later, we have to seal it so well "
                  "that it stays sealed... forever."),
        ('hook5', "In this video, we'll follow one subsea well on the Norwegian Continental Shelf "
                  "through its entire life."),
        ('hook6', "How it's designed. How it's drilled. How it's completed. "
                  "And finally, how it's plugged and abandoned."),
    ]),
    # ------------------------------------------------------------------ 2
    dict(id='s02_setting', title='The setting', beats=[
        ('set1', "Let's set the scene."),
        ('set2', "Our well sits in about three hundred and fifty meters of water, "
                 "and nothing of it will ever stick up above the waves."),
        ('set3', "Instead, everything, from the wellhead to the valves that control the flow, sits on "
                 "the seabed. The oil and gas travel through pipelines to a production facility, which "
                 "can be many kilometers away. That's what makes it a subsea well."),
        ('set4', "Our target is a sandstone reservoir, about three kilometers below the seabed. Its "
                 "pores, the tiny spaces between the grains of sand, hold the oil and gas."),
        ('set5', "And sitting right on top of it is a layer of dense, impermeable shale: the cap rock. "
                 "It's the reason the oil and gas are still here. For millions of years, it has been "
                 "nature's own lid."),
        ('set6', "Keep that idea in mind. Because at the very end of this well's life, "
                 "our job will be to put that lid back."),
    ]),
    # ------------------------------------------------------------------ 3
    dict(id='s03_pressure', title='Design: the drilling window', beats=[
        ('pr1', "Before a single meter is drilled, the well is designed in painstaking detail. "
                "And almost every decision comes down to one thing: pressure."),
        ('pr2', "The fluids in the rock are under pressure. We call it the pore pressure."),
        ('pr3', "If the pressure in our wellbore ever falls below it, oil, gas or water will start "
                "pushing their way into the well. That's called a kick. "
                "And a kick that isn't controlled can become a blowout."),
        ('pr4', "So we keep the well full of a heavy fluid called drilling mud. The pressure at the "
                "bottom of a column of fluid is simply its density, times gravity, times the height "
                "of the column."),
        ('pr5', "Take mud one and a half times as dense as water, three thousand meters deep, and the "
                "pressure at the bottom is about four hundred and forty bar. "
                "That's like balancing a grand piano on your fingertip."),
        ('pr6', "But we can't just make the mud as heavy as possible. Push too hard, and we'll crack "
                "the rock open. That's the fracture pressure. Mud pours away into the formation, the "
                "level in the well drops... and that can trigger a kick of its own."),
        ('pr7', "So the mud pressure must always stay inside a window: above the pore pressure, "
                "but below the fracture pressure."),
        ('pr8', "Plot both against depth, and you get the single most important chart in well "
                "design: the drilling window."),
    ]),
    # ------------------------------------------------------------------ 4
    dict(id='s04_casing', title='Design: casing', beats=[
        ('cs1', "Now here's the problem. As we go deeper, the window moves."),
        ('cs2', "Sooner or later, the mud weight we need at the bottom of the hole would fracture "
                "the weaker rock higher up."),
        ('cs3', "The solution is to seal off the hole we've drilled so far with steel pipe, called "
                "casing, cemented firmly in place. Then we carry on with a smaller bit, and a "
                "heavier mud."),
        ('cs4', "Repeat that, step by step, and you get the classic telescope shape of an "
                "offshore well."),
        ('cs5', "A thirty-inch conductor. A twenty-inch surface casing. Thirteen and three-eighths. "
                "Nine and five-eighths. And finally, a seven-inch liner through the reservoir.",
         "30\" conductor · 20\" surface casing · 13⅜\" · 9⅝\" · 7\" liner"),
        ('cs6', "Every string is engineered for three load cases. Burst, from pressure inside. "
                "Collapse, from pressure outside. And tension, from its own enormous weight, "
                "which can reach hundreds of tonnes."),
    ]),
    # ------------------------------------------------------------------ 5
    dict(id='s05_barriers', title='Design: two barriers', beats=[
        ('ba1', "There's one more golden rule. Under the Norwegian standard, Norsok D zero ten, "
                "there must always be two independent, tested barriers between the reservoir "
                "and the outside world.",
         "Under the Norwegian standard NORSOK D-010, there must always be two independent, tested "
         "barriers between the reservoir and the outside world."),
        ('ba2', "If one fails, the other one holds."),
        ('ba3', "We draw them as two envelopes: the primary barrier in blue, and the secondary "
                "barrier in red. And we'll keep checking them at every stage of the well's life."),
    ]),
    # ------------------------------------------------------------------ 6
    dict(id='s06_rig', title='Drilling: the rig', beats=[
        ('rg1', "With the design approved, it's time to drill."),
        ('rg2', "The job is done by a semi-submersible drilling rig: a floating platform standing "
                "on huge pontoons, ballasted down below the waves so that it barely notices the "
                "North Sea swell."),
        ('rg3', "It's held in position above the well by anchors, or by computer-controlled thrusters."),
        ('rg4', "At its heart is the derrick. Here, the top drive rotates the drill string: a chain "
                "of steel pipe, screwed together length by length, until it's several kilometers long."),
    ]),
    # ------------------------------------------------------------------ 7
    dict(id='s07_tophole', title='Drilling: top hole', beats=[
        ('th1', "The first sections are drilled riser-less, with no pipe connecting the well to the rig.",
         "The first sections are drilled riserless, with no pipe connecting the well to the rig."),
        ('th2', "A thirty-six inch hole is drilled into the soft sediments, and seawater and rock "
                "cuttings simply spill out onto the seabed."),
        ('th3', "The conductor is run and cemented in place. It carries the low-pressure wellhead "
                "housing, and forms the structural foundation of the well."),
        ('th4', "Next comes a twenty-six inch hole, and the twenty-inch surface casing, crowned by the "
                "high-pressure wellhead housing. This is the anchor point for everything that follows."),
    ]),
    # ------------------------------------------------------------------ 8
    dict(id='s08_bop', title='Drilling: the BOP', beats=[
        ('bp1', "Before drilling any deeper, into rock that could hold pressure, we need our safety "
                "net: the blowout preventer, or B O P.",
         "Before drilling any deeper, into rock that could hold pressure, we need our safety net: "
         "the blowout preventer, or BOP."),
        ('bp2', "It's a stack of massive hydraulic valves, around fifteen meters tall and weighing "
                "several hundred tonnes, latched onto the wellhead."),
        ('bp3', "Annular preventers can squeeze a rubber seal around almost anything in the hole. "
                "Pipe rams close tightly around the drill pipe."),
        ('bp4', "And as a last line of defence, the blind shear rams can cut straight through the "
                "pipe, and seal the well completely."),
        ('bp5', "On top sits the marine riser: a wide steel pipe running all the way up to the rig, "
                "so the mud can return to the surface."),
    ]),
    # ------------------------------------------------------------------ 9
    dict(id='s09_circulation', title='Drilling: mud and bit', beats=[
        ('mc1', "Now the real drilling begins, and the mud becomes the star of the show."),
        ('mc2', "Powerful pumps push it down through the inside of the drill string. It jets out "
                "through nozzles in the bit, cooling it, and flushing away the rock cuttings."),
        ('mc3', "Then it carries those cuttings back up the annulus, the gap between the drill string "
                "and the wall, and up the riser to the rig."),
        ('mc4', "There, shale shakers sieve out the rock, and the cleaned mud goes back to the pits, "
                "ready to go round again."),
        ('mc5', "The bit itself is usually a P D C bit, studded with synthetic diamond cutters that "
                "shear the rock like a plane shaving wood.",
         "The bit itself is usually a PDC bit, studded with synthetic diamond cutters that shear the "
         "rock like a plane shaving wood."),
        ('mc6', "Just behind it, sensors measure the well's direction and the properties of the rock, "
                "and send their data to the surface as pressure pulses in the mud itself."),
        ('mc7', "And with a rotary steerable system, the driller can bend the well, gently, towards a "
                "target that may be kilometers away."),
    ]),
    # ------------------------------------------------------------------ 10
    dict(id='s10_cementing', title='Drilling: casing and cement', beats=[
        ('ce1', "Section by section, the well goes deeper. Drill. Run casing. Cement. Test."),
        ('ce2', "Every cement job follows the same choreography. First a bottom plug, then the cement, "
                "then a top plug, and finally mud, to push the whole train down the casing."),
        ('ce3', "When the top plug lands, the pressure spikes. We've bumped the plug. The cement has "
                "been squeezed up into the annulus, where it sets hard and seals it off."),
        ('ce4', "Then, after drilling a few meters of new hole, a leak-off test checks that the rock "
                "below the casing shoe can take the heavier mud to come."),
    ]),
    # ------------------------------------------------------------------ 11
    dict(id='s11_wellcontrol', title='Drilling: well control', beats=[
        ('wc1', "And if a kick does happen? The first warning usually comes at the surface. "
                "The mud pits start to gain volume."),
        ('wc2', "The crew shuts in the well with the B O P, reads the pressures, and circulates the "
                "influx out through the choke line, while pumping in heavier kill mud.",
         "The crew shuts in the well with the BOP, reads the pressures, and circulates the influx out "
         "through the choke line, while pumping in heavier kill mud."),
        ('wc3', "The well is under control again. And that is exactly why we always keep two barriers."),
    ]),
    # ------------------------------------------------------------------ 12
    dict(id='s12_completion', title='Completion', beats=[
        ('co1', "Once the reservoir section is drilled, the well is still just a hole lined with "
                "steel. Completion turns it into a producer."),
        ('co2', "First, the seven-inch liner is cemented across the reservoir. "
                "To connect the well to the rock, we fire perforating guns."),
        ('co3', "Each shaped charge fires a jet of metal at around seven kilometers per second, "
                "punching through steel and cement, and deep into the reservoir."),
        ('co4', "Next comes the upper completion. The production tubing is the pipe the oil and gas "
                "will actually flow through."),
        ('co5', "A production packer seals the gap between the tubing and the casing."),
        ('co6', "A downhole safety valve, a few hundred meters below the seabed, is held open by "
                "hydraulic pressure. Lose that pressure, and it snaps shut on its own."),
        ('co7', "The B O P and riser are then pulled, and in their place we install the subsea "
                "christmas tree: a compact assembly of valves that controls the flow from the well.",
         "The BOP and riser are then pulled, and in their place we install the subsea christmas "
         "tree: a compact assembly of valves that controls the flow from the well."),
        ('co8', "It's tied in to the production system with flowlines, and an umbilical supplies it "
                "with hydraulic power, electricity, and chemicals."),
        ('co9', "The well is cleaned up, tested, and handed over. Two barriers, once again. The tubing, "
                "packer and safety valve in blue. The casing, cement, wellhead and tree in red."),
    ]),
    # ------------------------------------------------------------------ 13
    dict(id='s13_production', title='Production', beats=[
        ('pd1', "For the next twenty or thirty years, the well produces."),
        ('pd2', "The reservoir pressure slowly falls, more and more water comes with the oil, and "
                "eventually, every well reaches the end of its life."),
        ('pd3', "And then comes the final chapter."),
    ]),
    # ------------------------------------------------------------------ 14
    dict(id='s14_pa', title='Plug and abandonment', beats=[
        ('pa1', "On the Norwegian shelf, plugging and abandonment, or P and A, comes with a remarkable "
                "requirement. The well must be sealed with an eternal perspective.",
         "On the Norwegian shelf, plugging and abandonment, or P&A, comes with a remarkable "
         "requirement. The well must be sealed with an eternal perspective."),
        ('pa2', "Not for years. Not for decades. For as long as the rock itself."),
        ('pa3', "First, the well is killed with heavy fluid to balance the reservoir pressure. "
                "The christmas tree is removed, a B O P is installed once again, and the tubing "
                "is pulled out.",
         "First, the well is killed with heavy fluid to balance the reservoir pressure. The christmas "
         "tree is removed, a BOP is installed once again, and the tubing is pulled out."),
        ('pa4', "Just like during drilling, we need two independent barriers. But this time they're "
                "permanent, and each one must seal the entire cross-section of the well, including "
                "every annulus. Rock to rock."),
        ('pa5', "And that's where it gets tricky. Behind the casing, the original cement may be "
                "missing, or of poor quality. A plug inside the pipe won't stop fluid sneaking up "
                "the outside."),
        ('pa6', "So the casing is either milled away completely, or perforated, washed, and "
                "cemented, so the new cement bonds straight to the formation."),
        ('pa7', "The primary barrier is set just above the reservoir, in the cap rock, where the rock "
                "is strong enough to hold the pressure below. The secondary barrier backs it up. "
                "Each one is a plug of solid cement, typically tens of meters long."),
        ('pa8', "Near the seabed, a final surface plug seals the well off from the ocean."),
        ('pa9', "Every plug is verified: tagged with weight, and pressure tested."),
        ('pa10', "Finally, the casings are cut a few meters below the seabed, and the wellhead is "
                 "lifted to the surface."),
        ('pa11', "What's left is... just the seabed. The cap rock has been restored. "
                 "Nature's lid is back in place."),
    ]),
    # ------------------------------------------------------------------ 15
    dict(id='s15_outro', title='Recap', beats=[
        ('ou1', "So, let's recap the life of a subsea well."),
        ('ou2', "It's designed around the drilling window, with a telescope of casings, "
                "and two barriers at all times."),
        ('ou3', "It's drilled from a floating rig, through a blowout preventer, with mud holding back "
                "the pressure of the rock."),
        ('ou4', "It's completed with a liner, perforations, tubing, a safety valve, "
                "and a christmas tree."),
        ('ou5', "And at the end of its life, it's sealed with permanent, rock-to-rock barriers, "
                "and removed without a trace."),
        ('ou6', "Decades of engineering, all for one hole in the ground. Thanks for watching."),
    ]),
]


def beats(scene):
    """Yield (beat_id, say, text) for a scene dict."""
    for b in scene['beats']:
        say = b[1]
        text = b[2] if len(b) > 2 else say
        yield b[0], say, text


def display_text(say):
    """Convert the speech spelling to on-screen British spelling."""
    rep = {'kilometers': 'kilometres', 'meters': 'metres', 'meter': 'metre',
           'Kilometers': 'Kilometres', 'defense': 'defence'}
    for a, b in rep.items():
        say = say.replace(a, b)
    return say
