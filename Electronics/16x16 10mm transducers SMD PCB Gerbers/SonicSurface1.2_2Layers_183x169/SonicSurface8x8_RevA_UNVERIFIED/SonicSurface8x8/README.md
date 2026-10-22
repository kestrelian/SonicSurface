# SonicSurface 8x8 - Rev A

Local engineering design package, 22 October 2026. **UNVERIFIED: NOT RELEASED FOR FABRICATION.**

This is a new circuit and PCB implementation informed by the supplied SonicSurface manufacturing files. Gerbers do not preserve an editable schematic or authoritative circuit netlist. This package is not a recovered original KiCad project.

## Open in KiCad 10

- `Array8x8/Array8x8.kicad_pro`: 160 x 124 mm, two-layer array PCB; root schematic and eight row sheets.
- `CoreEP4CE6_Adapter/CoreEP4CE6_Adapter.kicad_pro`: 38 x 65 mm, two-layer plug-in P1-to-IDC26 cable adapter.
- Each project contains its own symbols, footprints and library tables.
- Each `fabrication_UNVERIFIED/` directory contains Gerber and Excellon exports. Do not send these to a manufacturer until the deferred checks pass.
- `schematic_svg/` contains readable schematic exports; `BOM.csv` lists components individually; `connectivity.csv` records intended pin-to-net assignments.
- `CABLE_PIN_MAP.csv` and `CoreEP4CE6_8x8_pins.qsf` define the module interface. `CHANNEL_MAP.csv` supplies all 64 physical and acoustic coordinates.
- `DESIGN_NOTES.md`, `ASSEMBLY.md`, and `QA_CHECKLIST.md` explain design assumptions, assembly, and deferred verification.

## Implemented parts

64 Murata MA40S4S; 32 Microchip TC4427EPA DIP-8; 8 74HC595N DIP-16. The driver package supersedes the earlier SOIC suggestion. The CoreEP4CE6 is external and connects through a straight 26-way ribbon and the adapter. No bare FPGA is fitted to the array.

The transducer pitch is **12 mm**, enlarged from the original approximately 10.5 mm to make room for DIP through-hole pads. The active grid spans 84 mm between the first and last centres. The transducer body envelope is about 94.2 x 94.2 mm at maximum body diameter. Array board area is about 35.8% smaller than the supplied 183 x 169 mm board.

## Completion and verification are separate

The package contains native editable design files and manufacturing exports. Routing generation status is recorded in each project's `routing_status.json`; that is an authoring log, **not** a connectivity, clearance, signal integrity or manufacturing test result. The array has routed ground connections supplemented by copper pours; the adapter has ground pours and stitching vias. The final checklist is intentionally unexecuted at the user's request. Physical fit, all-net connectivity, component ratings under actual operation, cable timing, and acoustic performance remain unverified.

No FPGA bitstream is supplied. The QSF is a pin-assignment fragment, not a complete Quartus project. Firmware adaptation and compilation are needed before use. The old 256-channel bitstream must not be used unchanged.

Everything remains local. Nothing has been committed, pushed, uploaded to a PCB service, or ordered.

## Reproduction

Use the Python supplied with KiCad 10. `build_design.py` regenerates placed boards and schematics, **overwriting edits in the generated project files**. Do not rebuild over manual work; copy the package first.

For the array, `prepare_router_input.py` produces a Specctra DSN with explicit 0.25 mm signal / 0.8 mm power / 0.4 mm ground rules. Route that DSN with Freerouting 2.5.0 Java locally, then run `import_array_routing.py` to import `authoring/routed.ses` and add ground pours. The session is included, so it can be re-imported without rerunning the router. `route_design.py CoreEP4CE6_Adapter` reproduces the adapter's grid routing. The grid router is retained for provenance but did not complete the array routing; do not replace the array with that intermediate result. `export_fabrication.py` writes Gerbers/drills from the native boards.

No script in this package runs the final QA checklist. The native Freerouting executable was blocked by Windows; the official Java distribution was used with a portable Temurin 25 runtime instead. Downloads and router runtime files are local under `tools/` but are excluded from the delivery ZIP. No Windows security setting was changed. The official tool and runtime can be obtained from [Freerouting releases](https://github.com/freerouting/freerouting/releases/tag/v2.5.0) and [Eclipse Adoptium](https://adoptium.net/).

