# Assembly and fabrication notes — Rev B

Engineering draft; final checks are unexecuted. Use two copies of the array and one controller adapter. Keep these files together with POWER_DESIGN.md, HARDWARE_INTERFACE.md and QA_CHECKLIST.md.

## Proposed stack and mechanics

Two copper layers, nominal 1.6 mm FR-4, nominal 35 micrometre finished copper, solder mask both sides. Final laminate, finish and manufacturing tolerances require vendor agreement. Array: 114 × 120 mm. Adapter: 120 × 140 mm. Do not mirror exported bottom Gerbers manually. Assembly SVGs use the board's top-view coordinate convention; bottom-side parts must be interpreted from the indicated layer.

MA40S4S bodies face the front; array DIP drivers, shift registers, interface circuitry and connectors mount on the back. Use the local footprints supplied with the project. DIP pad shapes were deliberately changed for the 10.3 mm pitch. Each TC4427 sits between two transducer rows, rotated so its inputs face the row above and its outputs face its own row; this keeps even a maximum-length 10.16 mm PDIP body clear of every transducer lead. Transducers alternate 180° in each driver pair so pin 1 (drive) is always the outer pin. Polarity follows pin 1, not the body orientation. Optional DIP sockets have not been allocated extra courtyard or height and are not approved by this draft. Trim and insulate protruding leads as required by the later physical-fit review. Do not force transducer leads into holes.

Silkscreen and fabrication graphics identify pin 1 even where copper pads are round. Verify bottom-side pin numbering before assembly. Keep transducer polarity consistent, then establish acoustic phase/polarity in the external calibration project. Coordinates and channel numbers are in CHANNEL_MAP.csv; origin is the PCB drawing origin, not the acoustic centre.

## Procurement

The grouped BOM includes quantity per PCB and quantity for the full two-array system. Passive values include minimum electrical requirements, not an approval of arbitrary substitute parts. Select exact capacitor ordering codes against DC-bias capacitance, ripple, ESR, case dimensions and temperature. The precision cutoff-divider values require the stated tolerance. Do not replace the 0.01% output-overvoltage divider with ordinary 1% resistors.

External items: one actual CoreEP4CE6 module matching the documented P1 assignment; two straight keyed IDC26 cable assemblies no longer than 100 mm, with strain-relief covers; three separate keyed power cable assemblies (external input and two array branches); an isolated regulated 17–20 V external DC source with the stated current capacity; mechanical standoffs and enclosure cable supports. Confirm mating housings/contact suffixes and wire gauges against manufacturer drawings.

Core power remains separate. Its 3.3 V pin is a sense/bias connection, not the array logic supply. Connect the external 17–20 V source only to adapter J4. Array J2 receives only the adapter's protected approximately 16.8 V output. The common ground is intentional; this design provides no galvanic isolation between module and arrays.

## Power-layout release conditions

The regulator's switching loop, feedback loop, thermal ground, narrow pad escapes and cutoff charging/discharging currents require explicit layout and prototype approval before manufacturing release. Authoring routes and filled zones do not establish loop stability or transient safety. Dense SMD escapes include 0.50 mm vias with 0.20 mm drills (0.15 mm nominal annular ring), and local 0.15 mm trace neckdowns. Confirm these capabilities with the fabricator. These escapes use smaller vias and narrow traces; assess plating, thermal capacity and any via touching a solderable pad. If via-in-pad fabrication is required, specify filled/capped vias or relocate the vias before release. Standard open vias must not be silently substituted in solderable pads.

Keep the eFuse RTN exposed-pad island separate from the main ground. Ground stitching must not join it to GND. The LTC3115 ground exposed pad requires a suitable thermal path to ground copper. These are different electrical nodes despite similar exposed-pad packages.

## Files

Open the .kicad_pro file in each project. Symbols and footprints are local. Schematic XML netlists and connectivity tables are exported design data, not independently reconciled test reports. PLACEMENT.csv uses millimetres. TEST_POINTS.csv identifies probe locations. ASSEMBLY_F.svg and ASSEMBLY_B.svg are placement drawings. Manufacturing exports are explicitly marked UNVERIFIED.

No final ERC, DRC, CAM, DFM, bench or acoustic checks have been performed. Firmware, bitstream generation and host software are separate projects. No files were pushed, ordered or published.
