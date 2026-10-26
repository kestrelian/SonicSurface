# SonicSurface dual 8x8 hardware — Revision B

26 October 2026. **Engineering draft. Final verification NOT EXECUTED. Not a fabrication release.**

This revision supersedes Rev A for the requested new hardware. Rev A files are preserved separately. Build two identical array PCBs and one controller/power adapter.

## Native KiCad projects

- `Array8x8_RevB/Array8x8_RevB.kicad_pro`: two-layer 114 × 120 mm array, 64 MA40S4S at 10.3 mm pitch, 32 TC4427EPA DIP-8 and eight SN74HC595N DIP-16. The front is acoustic; drivers and interface components are on the back.
- `DualArray_Controller_RevB/DualArray_Controller_RevB.kicad_pro`: two-layer 120 × 140 mm controller/power adapter. It mates with CoreEP4CE6 P1, has two separately buffered IDC26 signal outputs, a 17–20 V input and two protected driver-power outputs.
- Each project includes local symbols/footprints, schematic SVGs, BOMs, intended connectivity, placement exports and an `authoring` directory.
- `fabrication_UNVERIFIED` contains generated manufacturing files after routing import. These are not approved manufacturing releases.

## Electrical arrangement

External 17–20 V input → 2 A fuse → TPS26600 input protection → LTC3115-1 buck-boost set to 16.8 V → LTC4365 precision window cutoff and back-to-back MOSFETs → separate 750 mA fuses and power cables to the arrays.

The adapter's separate R-78E3.3-0.5 regulator supplies both arrays' logic. Core P1 pin 2 is used only for voltage sensing and source-side bias, not as a logic-power source. Core P1 pin 24 remains unconnected. Power the Core module through its own approved input.

Each array has input buffers with partial-power-down protection, logic and driver-rail supervisors, hardware gating of the HC595 output enable, input pulldowns, 22 Ω output damping resistors, a discharge resistor and test points. Two copies use identical connectors and circuitry; adapter port A/B selects the channel bank.

The actual driver rail is slightly below the 16.8 V regulator setpoint because of MOSFET, fuse, connector and cable losses. Neither connector is a raw 20 V driver input. See `POWER_DESIGN.md` for voltage margins and remaining transient evidence requirements.

## Files for external firmware/software projects

`HARDWARE_INTERFACE.md`, `FPGA_INTERFACE.csv`, `CABLE_PIN_MAP.csv`, `CHANNEL_MAP.csv` and `CoreEP4CE6_DualArray_pins.qsf` define the hardware contract. The QSF is a pin fragment only. No firmware, host software, Quartus build, timing simulation or bitstream is included.

Use two straight keyed IDC26 cables with integral strain-relief covers, each no longer than 100 mm. The provisional hardware interface ceiling is 4 MHz shift clock; it is a design requirement pending signal-integrity validation, not a measured capability. Driver power uses separate keyed Micro-Fit cables. No hot-plug qualification is claimed.

## Mechanical changes

Array area decreases from 19,840 mm² (160 × 124 mm) to 13,680 mm² (114 × 120 mm), about 31.0%. The transducer body envelope is 82.3 × 82.3 mm using maximum 10.2 mm diameter. A 10.3 mm pitch gives only 0.1 mm nominal gap at maximum body diameter. Positional tolerance and assembly fit are release gates.

Each TC4427 sits on the back between two transducer rows, rotated so its inputs face the row above and its outputs face its own row. This keeps even a maximum-length 10.16 mm PDIP body clear of the transducer leads and leaves an eight-track front-copper channel through every driver row. The HC595 outputs run left in that channel straight into the driver inputs. As a result, the shift-register output order is QA→column 0 and QB..QH→columns 7..1 (see `HARDWARE_INTERFACE.md`). Transducers alternate 180° in each driver pair so pin 1 (drive) is always the outer pin.

The 1.2 mm transducer holes use 1.6 mm round copper pads (0.20 mm nominal annular ring); TC4427 DIP pads are round 1.5 mm on 0.8 mm holes. Pin 1 is identified by graphics/reference documentation, not a square pad. The layout uses 0.15 mm minimum clearance, 0.2 mm signal tracks and 0.6/0.3 mm vias; it needs fabricator and physical-fit review. Do not substitute generic footprints without re-layout.

## Status and reproduction

Final ERC, DRC, independent CAM review, electrical tests and acoustic measurements remain deliberately unexecuted. See `QA_CHECKLIST.md`. Router counts and file-export success are authoring information only.

`build_revb.py` regenerates placed boards and schematics and overwrites generated edits. For the array, `relayout_array.py` then applies the row-channel placement and writes the structured array copper as locked tracks; `relayout_array.py --schematic` applies the matching HC595 output labels to the row sheets (run it once per rebuild). `route_array.py prepare` adds ground escapes and writes `authoring/interface.dsn`; route it with Freerouting 2.5.0 (fan-out and optimizer disabled) to `authoring/interface.ses`; `route_array.py import` imports the session and pours ground. The controller still uses `prepare_routing.py` / `import_routing.py`. `export_fabrication.py` creates fabrication exports. Copy the project before rebuilding.

Everything stays local. No push, order or upload is part of this work.
