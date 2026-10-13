"""Narration script for "Well Integrity on the Norwegian Continental Shelf".

Each scene is a list of segments. A segment is (cue, text) or ("@pause", seconds).
Cue names are used by the animation to sync visuals to the voice.

Markup understood by the TTS front end (src/tts.py):
  word{VB}            force part-of-speech for homographs
  [word](/phonemes/)  explicit pronunciation
Words in tts.PRON (NORSOK, Havtil, MAASP, A-annulus ...) are handled automatically.

Facts and figures are referenced in SOURCES.md.
"""

SCENES = [
    # ------------------------------------------------------------------ 0
    dict(id="s00_open", chapter="", title="Cold open", segments=[
        ("@pause", 1.2),
        ("sea", "Two to four kilometers beneath the North Sea, oil and gas sit in porous rock at pressures of several hundred bar."),
        ("well", "A well is the only engineered path between that energy and the world above."),
        ("life", "For decades of production, and then, once it is plugged, for an eternity, that path must stay closed to everything except what we intend to let through."),
        ("title", "That is the job of well integrity."),
        ("@pause", 0.6),
        ("agenda", "In this film we look at how it is done on the Norwegian Continental Shelf: the regulations and standards, the barrier philosophy, how barriers are verified and monitored, how integrity is classified across a portfolio of wells, what goes wrong, and what the industry is learning as thousands of wells approach permanent plug and abandonment."),
        ("@pause", 1.0),
    ]),

    # ------------------------------------------------------------------ 1
    dict(id="s01_definition", chapter="1", title="What is well integrity?", segments=[
        ("@pause", 3.2),
        ("def", "NORSOK D-010, the Norwegian well integrity standard, defines well integrity as the application of technical, operational and organizational solutions to reduce the risk of uncontrolled release of formation fluids and well fluids, throughout the life cycle of a well."),
        ("technical", "Technical solutions are the hardware: casing, cement, packers, valves and wellheads, designed for the loads they will see."),
        ("operational", "Operational solutions are how the well is run: procedures, testing, monitoring, and operating limits that keep every component inside its design envelope."),
        ("organizational", "And organizational solutions are the people and the system around them: competence, clear responsibilities, management of change, and documentation that follows the well from one owner to the next."),
        ("@pause", 0.5),
        ("lifecycle", "The words life cycle matter. A well is designed, drilled and completed. It produces or injects, it is intervened on and worked over, it may be suspended, and finally it is permanently abandoned."),
        ("handover", "The international standard ISO sixteen five thirty frames this as life-cycle governance, and every handover between phases must carry a documented, verified barrier status."),
        ("why", "Why does this matter? Because a loss of integrity can mean a blowout, a release to sea or air, an underground flow between formations, or a slow leak that nobody sees until pressure appears where it should not."),
        ("@pause", 0.8),
    ]),

    # ------------------------------------------------------------------ 2
    dict(id="s02_framework", chapter="2", title="The Norwegian framework", segments=[
        ("@pause", 3.2),
        ("functional", "Norwegian petroleum regulation is largely functional. The regulations state what must be achieved, and the guidelines point to recognized standards that describe one way to achieve it."),
        ("havtil", "The regulator is Havtil, the Norwegian Ocean Industry Authority, which until 2024 was known as the Petroleum Safety Authority."),
        ("facilities", "The Facilities Regulations require that well barriers are designed so that well integrity is ensured and the barrier functions are safeguarded during the well's lifetime. Barrier performance must be verifiable."),
        ("abandon", "When a well is abandoned, its barriers must be designed for the longest period the well is expected to remain abandoned, and it must be possible to cut the casings safely when the well is finally plugged."),
        ("activities", "The Activities Regulations add the operational side. During drilling and well activities there shall be tested well barriers with sufficient independence. If a barrier fails, no other activities may be carried out in the well than those intended to restore it."),
        ("handover", "And when a well is handed over, its barrier status shall be tested, verified and documented."),
        ("management", "And above them all, the Management Regulations require that barriers are established and maintained, and that it is known which barriers exist, what function they serve, what performance is required of them, and whether they are working."),
        ("norsok", "For all of this, the guidelines point to NORSOK D-010, Well integrity in drilling and well operations. Revision five was published in 2021, and it is now issued in a consolidated edition with corrections from 2024."),
        ("rev5", "Revision five reorganized the standard and added a barrier requirements matrix, premises for using creeping formation and materials other than cement as barrier elements, accepted methods such as perforate, wash and cement, an expanded chapter on managed pressure drilling, and a formal route for qualifying new technology."),
        ("guidelines", "Around the standard sit the Offshore Norge guidelines: guideline one-seventeen on well integrity, covering classification, annulus pressure management and handovers, and guideline one-thirty-five on how well control and well integrity incidents are classified and reported."),
        ("forums", "Operators share experience through industry forums for well integrity and for plug and abandonment, so that a lesson learned on one field can protect wells on every other field."),
        ("@pause", 0.8),
    ]),

    # ------------------------------------------------------------------ 3
    dict(id="s03_barriers", chapter="3", title="Barrier philosophy", segments=[
        ("@pause", 3.2),
        ("barrier", "At the heart of NORSOK D-010 is the well barrier: an envelope of one or several well barrier elements that together prevent fluids from flowing unintentionally from a formation into the wellbore, into another formation, or to the external environment."),
        ("element", "A well barrier element, on its own, does not stop flow. A casing joint with no cement behind it, or a valve with no body around it, is just a component. Only the complete, closed envelope is a barrier."),
        ("two", "The core principle is two independent barriers. The primary well barrier is the first envelope that prevents flow from a source. The secondary well barrier is the one that takes over if the primary fails."),
        ("common", "Ideally the two envelopes share nothing. Where an element is part of both, a common well barrier element, the extra risk must be assessed and mitigated."),
        ("@pause", 0.6),
        ("drilling", "Look first at a well being drilled. Here the primary barrier is the drilling fluid itself. The weight of the mud column holds back the formation pressure."),
        ("hydro", "The physics is simple. Hydrostatic pressure equals density times gravity times true vertical depth. Mud with a specific gravity of one point three, at three thousand meters, exerts about three hundred and eighty bar, comfortably above a pore pressure of, say, three hundred and fifty."),
        ("secondary_drill", "Behind the fluid stands the secondary barrier: the formation at the last casing shoe, the casing cement, the casing, the wellhead, and the blowout preventer."),
        ("lot", "The formation at the casing shoe is a barrier element too, and its strength must be known. After each casing is set, a few meters of new hole are drilled and the well is pressured up in a formation integrity test or a leak-off test. The pressure at which the rock begins to take fluid sets the upper limit for the mud weight, and for the pressure the secondary barrier can hold."),
        ("kick", "If the fluid column fails, for example through losses to a weak formation or by swabbing while pulling pipe, formation fluid enters the well. Gas expands as it rises."),
        ("shutin", "The crew detects the influx and closes the blowout preventer. The secondary barrier now holds the pressure, while the primary barrier is restored by circulating out the influx and replacing the mud with a heavier kill fluid."),
        ("mpd", "In managed pressure drilling the fluid column is lighter, and a closed system adds back-pressure at surface. Revision five of D-010 expanded the requirements for exactly this kind of operation."),
        ("@pause", 0.6),
        ("production", "Now the same well, completed and producing. The fluid column is gone, so the envelopes are made of hardware."),
        ("primary_prod", "The primary barrier is drawn in blue: the casing and cement below the production packer, the production packer itself, the production tubing, and the downhole safety valve."),
        ("dhsv", "The downhole safety valve deserves a closer look. It is a fail-safe flapper valve, held open by hydraulic pressure from surface. If that pressure is lost, a spring closes it, shutting in the well even if everything above it is damaged."),
        ("secondary_prod", "The secondary barrier is drawn in red: the cap rock and casing cement above the reservoir, the production casing, the wellhead, the tubing hanger, the annulus valves, and the master valve on the Christmas tree."),
        ("wbs", "This drawing is a well barrier schematic. D-010 requires one for every well activity and phase, showing each element, its status, and the formation strength, so that anyone can see at a glance what is holding the well."),
        ("eac", "Each element type has an element acceptance table in the standard, stating its function, how it must be designed and selected, how it is tested and verified when installed, and how it must be monitored and maintained in use{NN}."),
        ("intervention", "And the envelopes change with every activity. During a wireline or coiled tubing intervention, the pressure control equipment rigged up on top of the tree becomes part of the barrier envelopes, and each change of configuration must be reflected in an updated schematic."),
        ("@pause", 0.8),
    ]),

    # ------------------------------------------------------------------ 4
    dict(id="s04_verify", chapter="4", title="Verification and testing", segments=[
        ("@pause", 3.2),
        ("assume", "A barrier that has not been verified is an assumption. Verification turns it into a fact, recorded for the life of the well."),
        ("ptest", "The most common verification is a pressure test in the direction of flow. D-010 calls for a low pressure test of fifteen to twenty bar for at least five minutes, before the high pressure test."),
        ("stable", "The static test pressure is then observed and recorded for at least ten minutes, with a stable reading. Unless the acceptance table for that element says otherwise, the acceptable leak rate is zero."),
        ("fail", "A falling curve that never flattens tells a different story: something is leaking, and the barrier is not accepted until the leak is found and fixed."),
        ("inflow", "Some elements are better tested from the other side. In an inflow test, the pressure above the barrier is reduced, simulating the load from below. If nothing flows and the pressure does not build up, the barrier is holding. D-010 calls for at least thirty minutes of stable reading."),
        ("macondo", "Interpretation is part of the barrier. In the Macondo disaster in the Gulf of Mexico in 2010, a negative pressure test was misread as a success, and the well blew out hours later."),
        ("valves", "Valves with an allowable leak rate, such as the downhole safety valve, are tested by closing the valve and bleeding off above it. The pressure build-up in the closed volume is converted to a leak rate. In the production phase, D-010 recommends a differential of seventy bar for these tests."),
        ("bop", "The blowout preventer is tested too: function tested and pressure tested when installed, and then at regular intervals. Revision five of D-010 kept the fourteen-day interval for the pressure test."),
        ("cement", "Cement is harder. We cannot see it, so we infer it: from the job itself, from volumes, pressures and returns, from a pressure test of the casing, from the formation strength at the shoe, and from logs."),
        ("cbl", "A cement bond log sends a sonic pulse along the casing. Free pipe rings like a bell, so the amplitude is high. Casing that is well bonded to cement is damped, so the amplitude is low."),
        ("ultra", "Ultrasonic tools go further. They spin a transducer to map the acoustic impedance behind the casing all the way around, and they can reveal a channel of mud that a bond log would average away."),
        ("lengths", "D-010 sets minimum lengths for cement in the annulus, longer when it is verified only by volumes, and shorter when bond is confirmed by logs. For permanent abandonment, the external cement must be verified over a defined interval before it can be credited as a barrier element."),
        ("doc", "Every test is recorded, signed off and linked to the well barrier schematic, so that whoever takes over the well knows not only what the barriers are, but how and when they were last proven."),
        ("@pause", 0.8),
    ]),

    # ------------------------------------------------------------------ 5
    dict(id="s05_annulus", chapter="5", title="Annulus pressure management", segments=[
        ("@pause", 3.2),
        ("annuli", "A producing well is a set of nested pressure vessels. Between the tubing and the production casing is the A-annulus. Between the production casing and the next string out is the B-annulus, and beyond that the C-annulus."),
        ("sources", "Pressure in an annulus can come from three places."),
        ("thermal", "Heat: when hot production fluid flows up the tubing, the trapped fluid in a sealed annulus expands, and pressure can rise by tens or even hundreds of bar."),
        ("apb", "In subsea wells, the outer annuli are often sealed and cannot be bled off at all. Trapped annular pressure must then be handled in the design, with stronger casing, burst disks, compressible foam or nitrogen cushions, or insulated tubing."),
        ("applied", "Applied pressure: for example lift gas injected into the A-annulus of a gas lifted well."),
        ("leak", "And leaks: a connection or packer leak that lets the tubing talk to the annulus, a casing leak, or gas migrating up through poor cement. Pressure that keeps coming back after it is bled off is called sustained casing pressure, and it is a warning sign."),
        ("maasp", "Every annulus has a limit, the maximum allowable annulus surface pressure, or MAASP. It is the highest pressure the annulus may contain, measured at the wellhead, without compromising any well barrier element in that annulus."),
        ("weakest", "MAASP is found from the weakest point: the burst rating of the outer casing, the collapse rating of the inner string, the rating of the packer, the tubing hanger, the wellhead and the valves, and, where the annulus is open to formation, the strength of the formation at the casing shoe."),
        ("plot", "Each limit is evaluated at depth, corrected for the fluids inside the annulus and behind it, and derated for temperature and design factors. Raise the surface pressure and the pressure profile moves to the right. The surface pressure at which it first touches a limit, anywhere along the well, is the MAASP for that annulus."),
        ("limits", "Below MAASP the operator sets operating limits and alarm levels, so that pressure is managed long before a limit is approached."),
        ("monitor", "Monitoring is continuous. Here is the A-annulus of a well starting up. The pressure rises with temperature, is bled down, and stabilizes. That is thermal behavior."),
        ("buildup", "Months later the pattern changes. After every bleed-off the pressure climbs back toward tubing pressure, and gas is returned. That is communication between tubing and annulus: the primary barrier has failed."),
        ("action", "The well is now relying on a single barrier. It is reclassified, risk-reducing measures are put in place, and the repair is planned."),
        ("gullfaks", "The cost of not watching is real. On Gullfaks C in 2010, pressure in the C-annulus had been rising for weeks without being noticed, before a hole in the casing led to a serious well control incident."),
        ("@pause", 0.8),
    ]),

    # ------------------------------------------------------------------ 6
    dict(id="s06_classify", chapter="6", title="Classifying well integrity", segments=[
        ("@pause", 3.2),
        ("intro", "With hundreds of wells on a field and thousands on the shelf, operators need a shared language for risk. Offshore Norge guideline one-seventeen provides one, using four colors."),
        ("green", "Green: a healthy well. The barrier philosophy is intact, with no or only minor issues."),
        ("yellow", "Yellow: one barrier is degraded, but the other is intact. The risk is increased, but within the regulations."),
        ("orange", "Orange: one barrier has failed while the other is intact, or a single further failure could lead to a leak to surface."),
        ("red", "Red: one barrier has failed and the other is degraded or not verified, or there is a leak to surface."),
        ("use", "The category drives priorities: which wells are repaired first, which are shut in, and what compensating measures are needed in the meantime."),
        ("rnnp", "Havtil also follows the industry over time through its annual survey of trends in risk level in the petroleum activity, known as RNNP, where well control incidents and well integrity are tracked as indicators."),
        ("@pause", 0.5),
        ("pilot", "How healthy is the shelf? In a pilot study for the Petroleum Safety Authority, published by Vignes and Aadnøy, four hundred and six production and injection wells on twelve facilities were reviewed. Eighteen percent had a well integrity failure, issue or uncertainty, and production tubing was the most common failing component."),
        ("ta", "Temporarily abandoned and inactive wells are a particular concern. In Havtil's 2024 survey, four hundred and eighty-eight such wells were reported, roughly double the 2022 survey, partly because inactive production wells were now included under the EU methane regulation."),
        ("tarules", "Even while temporarily abandoned, a well must have qualified, independent barriers, designed for the planned period. For subsea wells left for more than twelve months, integrity must be monitored."),
        ("tacount", "Three were classified red, thirty orange, one hundred and ninety-two yellow, and two hundred and sixty-three green. The number of red and orange wells rose from seventeen to thirty-three."),
        ("expect", "Havtil's expectation is clear: red wells are to be permanently plugged, and orange wells either brought back into use{NN} or permanently plugged."),
        ("@pause", 0.8),
    ]),

    # ------------------------------------------------------------------ 7
    dict(id="s07_failures", chapter="7", title="When barriers fail", segments=[
        ("@pause", 3.2),
        ("modes", "Barrier elements fail in recognizable ways."),
        ("tubing", "Tubing corrodes or leaks at its connections."),
        ("dhsv", "Safety valves fail to close, or close{VB} but leak."),
        ("casing", "Casing wears during drilling, corrodes in service, or is deformed by the rock around it."),
        ("cement", "Cement is placed with channels, or cracks and debonds under repeated pressure and temperature cycles, opening a micro-annulus."),
        ("seals", "Seals in the wellhead and hanger age."),
        ("compaction", "And the reservoir itself can move. In the chalk fields of the southern North Sea, compaction has lowered the seabed at Ekofisk by around nine meters, and casing deformation has been a long-standing challenge."),
        ("@pause", 0.5),
        ("snorre", "Three Norwegian incidents show what is at stake. On Snorre A, in November 2004, tubing and casing were being pulled from an injection well to prepare a sidetrack. The pulling drew gas from the reservoir into the well, and it escaped through a section of worn casing into the formation, and up to the seabed beneath the platform."),
        ("snorre2", "Production was shut down and most of the crew were evacuated by helicopter, while a small team brought the well under control with heavy mud. The gas could have ignited. Investigations pointed to inadequate planning and risk assessment, and to governing documents that were not followed."),
        ("gullfaks", "On Gullfaks C, in 2010, a hole in the thirteen and three-eighths inch casing during managed pressure drilling caused losses to the formation, and then an influx from the reservoir. The investigations found insufficient technical integrity in the casing, and it took more than two months to restore the barriers."),
        ("troll", "And in September 2025, on the Troll field, a well was being permanently plugged from the rig Deepsea Bollsta. When the thirteen and three-eighths inch casing was cut, gas from the reservoir that had accumulated behind it was released to the rig. Around nine hundred and thirty kilograms of gas were released, with one hundred and fourteen people on board."),
        ("troll2", "Havtil found a failure in the well's outer barrier, and a lack of barriers towards the reservoir during the cut. Technology and methods had been used that were not qualified for the purpose, and faulty calibration led to log data being misinterpreted, so the gas was not detected. Havtil described the incident as one with the potential to become a major accident."),
        ("common", "Twenty years apart, the common threads are the same: understand your barriers, verify them, plan for what could go wrong, and follow the plan."),
        ("@pause", 0.8),
    ]),

    # ------------------------------------------------------------------ 8
    dict(id="s08_pa", chapter="8", title="Plug and abandonment", segments=[
        ("@pause", 3.2),
        ("scale", "Every well that is drilled must one day be permanently plugged. On the Norwegian shelf, Havtil estimates that around two thousand two hundred and fifty wells will need permanent plug and abandonment sooner or later, and operators plan to plug around three hundred of them within the next five to seven years."),
        ("industrial", "The work is becoming industrial. Equinor, for example, has contracted a semi-submersible rig specially designed for well plugging, to permanently plug fifteen to twenty wells a year from 2026."),
        ("phases", "A permanent plug and abandonment is often described in three phases: reservoir abandonment, where the deep barriers are set; intermediate abandonment, where shallower sources are isolated and casing may be cut and pulled; and finally removal of the wellhead and conductor, cut below the seabed."),
        ("eternal", "The requirement is demanding. D-010 states that a permanently abandoned well shall be plugged with an eternal perspective. There will be no one monitoring it, so the barriers must last indefinitely, against the pressure the reservoir may build up again over geological time."),
        ("rock", "A permanent barrier must extend across the full cross section of the well, including every annulus, from rock to rock. And its base must sit where the formation is strong enough to withstand the potential pressure below. Place a plug too shallow, and the reservoir could fracture the rock beneath it."),
        ("envelopes", "For each source of inflow there is a primary and a secondary barrier, and near the surface a final barrier isolates the shallow formations from the seabed."),
        ("lengths", "For cement plugs, D-010 revision five requires one hundred meters in open hole, with at least fifty meters above any source of inflow. In cased hole, fifty meters is accepted when the plug sits on a mechanical or cement foundation, otherwise one hundred meters."),
        ("material", "The material must be impermeable, non-shrinking, able to withstand mechanical loads, resistant to chemicals such as hydrogen sulfide, carbon dioxide and hydrocarbons, and able to bond to steel and rock."),
        ("verify", "And every plug is verified: tagged, to confirm that it is where it should be, and in cased hole, pressure tested. The barrier behind the casing must be verified too, usually by logging."),
        ("@pause", 0.5),
        ("annulus", "The hard part is usually the annulus. A cement plug inside the casing does nothing if the cement outside the casing is missing. When logs show poor annular cement, there are three main options."),
        ("milling", "Section milling grinds away a length of casing, exposing the rock, so that a new plug can be set from formation to formation. It works, but it is slow and generates large volumes of steel swarf."),
        ("pwc", "Perforate, wash and cement shoots holes in the casing, jets the annulus clean through them, and then squeezes cement behind the pipe in a single trip. Revision five of D-010 recognizes the method, with defined premises and a best practice for verification."),
        ("cutpull", "Or the casing is cut and pulled, which is exactly where the Troll incident shows the need to keep well control barriers in place and to know what is behind the pipe before you cut."),
        ("@pause", 0.5),
        ("shale", "Sometimes the formation does the work. Certain shales, rich in clay minerals such as smectite, are ductile and creep under stress until they close{VB} the annulus and grip the casing. Creeping shale has been used as a barrier element on the Norwegian shelf since 2006."),
        ("shale2", "It is verified by logging, and D-010 sets out its acceptance criteria. In 2025 Havtil published a knowledge study on creeping shale, describing it as potentially an efficient and cost-effective way to establish a barrier behind casing, and pointing to the need for further research and more specific requirements."),
        ("newtech", "New materials and methods are being qualified as well. Bismuth alloys are melted in place and expand slightly as they solidify; Aker BP has set dozens of bismuth plugs on Valhall. Thermite-based tools that melt casing, cement and rock into a single seal have been tested at full scale in Norway. And logging through tubing, and through two casing strings at once, may let more wells be plugged without a rig."),
        ("qualify", "For every new technology, the principle is the same. It must be qualified for its purpose before it can be credited as a permanent barrier element."),
        ("@pause", 0.8),
    ]),

    # ------------------------------------------------------------------ 9
    dict(id="s09_ccs", chapter="9", title="A new chapter: CO₂ storage", segments=[
        ("@pause", 3.2),
        ("northern", "Well integrity is now protecting something new. In August 2025, Northern Lights began injecting carbon dioxide into the Aurora storage site, around two and a half kilometers below the seabed, south of the Troll field. Norway has stored carbon dioxide offshore since 1996, first at Sleipner and later at Snøhvit."),
        ("co2", "Carbon dioxide changes the load case. Mixed with water it forms carbonic acid, which attacks carbon steel and can degrade conventional cement."),
        ("impurities", "Impurities in captured carbon dioxide, such as water, oxygen and sulfur compounds, can make it even more aggressive, so corrosion resistant alloys and carbon dioxide resistant cement systems are used where it matters."),
        ("cycles", "Injection from ships can be intermittent, so the well sees repeated cooling and pressure cycles that can open micro-annuli."),
        ("legacy", "And every old well that penetrates the storage complex, including plugged ones, becomes a potential leak path that must be assessed."),
        ("sintef", "A 2024 study by SINTEF for Standards Norway concluded that CO2 wells are built much like petroleum wells, but that the fluid, the load pattern and the longer lifetime give a different risk picture, and that this should be addressed in the revision of D-010."),
        ("@pause", 0.8),
    ]),

    # ------------------------------------------------------------------ 10
    dict(id="s10_future", chapter="10", title="Digital well integrity and key lessons", segments=[
        ("@pause", 3.2),
        ("digital", "Well integrity is also becoming digital. Annulus pressures, valve tests and barrier status are streamed into integrity management systems, where automated analysis flags abnormal build-up long before a person would spot it."),
        ("twin", "Digital barrier schematics keep the status of every element current, and data from logs, tests and incidents are shared across the industry."),
        ("wims", "Behind the software sits a well integrity management system: a register of every well and barrier element, test intervals based on risk, procedures for handling deviations, competence requirements, and regular audits."),
        ("caution", "But the tools are only as good as their calibration and the people interpreting them. The Troll incident is a reminder that a log can look convincing and still be wrong."),
        ("@pause", 0.6),
        ("lessons", "So, to sum up."),
        ("l1", "Two independent, tested barriers. Always know your envelopes, and draw them."),
        ("l2", "A barrier that is not verified is an assumption. Test, log and document{VB}."),
        ("l3", "Respect the limits. Know the MAASP of every annulus and watch the trends."),
        ("l4", "Classify honestly, and act on degradation early, before a yellow well becomes red."),
        ("l5", "Plug for eternity: rock to rock, with qualified materials, verified in place."),
        ("l6", "And remember that most failures begin in planning, risk assessment and communication, long before the steel or the cement gives way."),
        ("@pause", 0.6),
        ("close", "A well is a promise to the future: that what we opened, we can keep closed."),
        ("@pause", 2.5),
    ]),
]
