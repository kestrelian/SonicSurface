# Final Gerber, electrical and quality checklist

**Status of every item below: NOT EXECUTED.** Written at the user's request; do not interpret any design-file export, routing log or filled copper zone as a pass. Do not fabricate until the required items pass and deviations are reviewed. Record date, reviewer, tool/version, evidence, pass/fail and corrective action for each item when execution is authorized.

## 1. Design intent and source control

- [ ] Freeze the revision and archive native projects, local libraries, BOMs, cable map and exact Gerber/drill exports together. Generate a manifest and checksums at release.
- [ ] Confirm 64 MA40S4S, 32 TC4427 DIP-8 and 8 74HC595 DIP-16, complete ordering suffixes and actual purchased parts.
- [ ] Confirm the agreed 12 mm array pitch, 160 x 124 mm PCB, 38 x 65 mm adapter and changed acoustic geometry.
- [ ] Resolve any outstanding entries in `routing_status.json`; inspect both native boards, including ground connectivity. A zero routing-pair count is insufficient by itself.

## 2. Schematic and netlist

- [ ] Run KiCad ERC on both complete projects. Review every violation; do not blanket-suppress warnings. Add explicit external power-drive declarations where appropriate after reviewing supply direction.
- [ ] Independently compare each IC symbol's pin numbering, NC pins, power pins and footprint pad numbers with the manufacturer datasheet, including bottom-side orientation.
- [ ] Export the schematic netlist and compare it with the PCB connectivity; confirm all schematic-to-PCB links and exclude unintended extra nets or components.
- [ ] Confirm 8 row data lines, common shift/latch clocks, CLR_N and OE_N, one driver output per transducer, and no tied output pins.
- [ ] Confirm TC4427 non-inverting operation, 3.3 V logic margins at supply/temperature corners, HC595 output loading, and driver input pulldown strength.
- [ ] Confirm default-disabled operation and the output-latch initialization sequence. Analyze driver supply loss while logic remains powered; resolve the absence of an automatic interlock for the intended application.

## 3. PCB rules and connectivity

- [ ] Run KiCad DRC on each PCB with approved manufacturer constraints. Require zero unresolved shorts, unrouted nets, copper-clearance failures and drill/edge violations; document any accepted non-electrical exceptions.
- [ ] Refill zones and rerun DRC. Check isolated ground islands, thermal spokes, all ground pads and stitching vias. Confirm a continuous return path under cable clocks and driver currents.
- [ ] Review all routing widths against calculated average and peak current, temperature rise and copper thickness. Check ground thermal spokes and via bottlenecks, not only positive-supply tracks.
- [ ] Check trace-to-pad neckdowns, acute corners, copper slivers, via annular rings, copper-to-edge distance and pad-to-hole registration.
- [ ] Review decoupling loop area, ground bounce, long common clock branches and unintended coupling from 12 V outputs to logic.
- [ ] Inspect assembly courtyards and physical heights on both sides. Specifically check transducer leads against driver/shift-register pads, DIP bodies and optional sockets.

## 4. Gerber completeness and independent CAM review

- [ ] Export final Gerber X2 layers from the frozen native PCB: front/back copper, front/back mask, front/back silkscreen, outline and populated paste layers. Include drill files and a fabrication drawing with the approved stackup.
- [ ] Open exports in an independent Gerber viewer, not only KiCad PCB Editor. Overlay outline, copper, masks and drills using a common origin.
- [ ] Confirm board dimensions in millimetres, a single closed outline, no duplicated/stray contour segments, and no accidental scaling, rotation, mirroring or coordinate-offset mismatch.
- [ ] Inspect both copper layers at high zoom around DIP pads, transducer pads, dense routing, clock branches, ground thermal reliefs and power entries.
- [ ] Verify layer naming and polarity. Confirm bottom artwork is interpreted correctly without an extra manual mirror.
- [ ] Verify solder-mask openings, tented/exposed vias, minimum mask webs and pad clearances. Check paste only on SMD pads; no unintended paste on transducer, DIP or other through-hole contacts.
- [ ] Verify silkscreen is readable, clipped away from exposed copper, and contains useful pin-1/polarity, power, connector and revision identification. Review bottom-side legends from the correct viewing side.
- [ ] Cross-compare final Gerber geometry and fabrication netlist against the native board for missing pads, traces, pours, vias or layers. Generate an IPC-D-356 netlist for the manufacturer's electrical test if required.

## 5. Drill and mechanical review

- [ ] Load plated and non-plated Excellon files separately with the Gerbers. Confirm metric units, zero suppression, origin and tool table.
- [ ] Confirm 1.2 mm finished transducer holes fit the square leads and worst-case lead-spacing tolerance without force; revise the footprint if necessary.
- [ ] Check DIP lead holes, IDC/socket holes and mounting-hole sizes against actual components and the fabricator's finished-hole tolerance.
- [ ] Confirm mounting holes are non-plated, electrically isolated and mechanically clear of traces and component bodies.
- [ ] Compare a 1:1 footprint print and actual parts; assess front/back lead trimming, stand-off and soldering-tool access.
- [ ] Confirm adapter socket orientation, Core P1 pin-1 end, module revision, adjacent P2 clearance, cable polarization and mechanical support.

## 6. Fabricator and assembly readiness

- [ ] Obtain fabricator DFM feedback for the agreed two-layer, nominal 1.6 mm FR-4 / 35 um copper stackup and surface finish. Resolve all manufacturer questions before release.
- [ ] Review minimum spacing, annular rings, soldermask web, edge clearance, drill aspect ratio and silkscreen capability against the actual vendor's specifications.
- [ ] Confirm capacitor voltage ratings, temperature characteristics/DC-bias derating, bulk-cap ESR, fuse rating and diode dissipation.
- [ ] Review BOM/placement orientation, all through-hole versus SMD assembly operations, polarized parts and DNI/NC handling. Include external cable, core board and mounting hardware in procurement planning.
- [ ] Ask for bare-board electrical continuity/short testing. Approve the manufacturer's final CAM preview and revision before ordering.

## 7. Prototype electrical tests - only after later authorization

- [ ] Inspect the bare PCB for copper defects, hole quality and correct dimensions. Inspect the assembled board for solder bridges, cold joints and orientation errors.
- [ ] With power disconnected, measure isolation between VIN, +12V, +3V3 and GND; check cable continuity and no accidental connection to Core P1 pin 24 (5 V).
- [ ] Bring up supplies with current limits and outputs disabled. Measure logic and driver rails, module regulator temperature and quiescent current.
- [ ] Validate startup, reset, reconfiguration, shutdown and separate supply-loss behavior without unintended pulses or back-powering.
- [ ] Scope SCLK, LATCH, DATA and OE_N at the furthest receiver with the actual cable. Check overshoot/undershoot, edge monotonicity, setup/hold and shift/latch timing over voltage and temperature. Tune source resistors if necessary.
- [ ] Walk a single enabled channel through all 64 outputs and compare with the channel map. Confirm inactive outputs stay low and no rows/columns are swapped.
- [ ] Measure loaded drive amplitude, frequency, duty cycle and ringing directly across a transducer. Keep worst-case voltage inside TC4427 and MA40S4S limits.
- [ ] Measure power draw, thermal rise, supply droop and ground bounce with worst-case simultaneous and phase-pattern switching. Confirm the fuse, traces, connectors and thermal design are adequate.

## 8. Acoustic and release review

- [ ] Establish transducer acoustic polarity and phase calibration for all channels; record calibration tied to serial number and channel map.
- [ ] Update software coordinates to the 12 mm pitch; evaluate steering limits, grating lobes, amplitude uniformity and intended focal patterns at the actual 40 kHz operating point.
- [ ] Review ultrasonic operating conditions for the intended use and document operating limits based on measurements.
- [ ] Close defects, regenerate all manufacturing files after changes, repeat affected checks, and have an independent reviewer sign off the fabrication release.

No pass/fail results are included because none of these final checks has been executed.

