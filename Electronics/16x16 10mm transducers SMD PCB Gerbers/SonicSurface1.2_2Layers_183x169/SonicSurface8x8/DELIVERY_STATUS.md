# Delivery status

22 October 2026 — Rev A engineering draft, UNVERIFIED.

- Created editable KiCad 10 array and CoreEP4CE6 cable-adapter projects with local symbol and footprint libraries.
- Array: 64 MA40S4S, 32 TC4427 DIP-8, eight 74HC595 DIP-16; two layers, 160 × 124 mm, 12 mm transducer pitch.
- Array router completed and saved its session, reporting zero unrouted connections. Imported that session into the native PCB and authored ground pours. This is not an independent connectivity or DRC result.
- Exported Gerbers, plated/non-plated drills, schematic SVGs, netlists, BOMs and component positions. Included cable/channel maps and a Quartus pin-assignment fragment.
- FPGA firmware/bitstream development is not included. The existing 256-channel firmware needs adaptation.
- Final ERC, DRC, independent Gerber inspection, fit checks, electrical tests and acoustic tests were deliberately NOT EXECUTED. See QA_CHECKLIST.md for the pending procedures.
- Deliverable generation is complete. Fabrication release remains pending the deferred checks and resolution of any resulting defects.
- All changes remain local; nothing was committed, pushed, ordered or uploaded.
