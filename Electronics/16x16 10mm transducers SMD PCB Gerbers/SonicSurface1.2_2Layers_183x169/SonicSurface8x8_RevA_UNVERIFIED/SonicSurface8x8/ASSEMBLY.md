# Assembly information - planning only

Rev A is not released for assembly or fabrication. These instructions describe intended construction after the deferred checklist is approved and completed; no physical assembly or test has been executed.

1. Use the separate BOM for each board. Confirm complete orderable part numbers before purchasing. The TC4427EPA footprint is DIP-8, 7.62 mm row spacing; 74HC595N is DIP-16, 7.62 mm row spacing. Do not substitute SOIC or TC4426/TC4428 without redesign.
2. All `T1..T64` go on the acoustic/front side. All `U1..U8` and `U101..U132` go on the back. Small resistor/capacitor populations are also predominantly on the back; consult the native board, not a mirrored screen capture, for pin 1.
3. Assemble the small SMD parts before the through-hole parts. Array J1/J2, F1/D1 and the bulk electrolytic are on the front margin. The adapter parts are on its front side.
4. Evaluate direct-soldered ICs versus low-profile DIP sockets with actual samples. Sockets are not in the BOM; they increase height and have not been mechanically qualified. Keep transducer pin tails away from DIP bodies and sockets on the opposite side. Avoid forcing transducer leads into holes or heating the prohibited lead region near the body.
5. Transducer schematic pin 1 is the electrical drive terminal, not a manufacturer-guaranteed acoustic polarity mark. Establish acoustic phase polarity and mark/orient each MA40S4S consistently, or compensate in firmware. Use the row/column channel map to record calibration.
6. Fit the Core adapter to the manufacturer's P1 header, with pin 1 identified from the actual board and the manufacturer schematic. Leave Core P2 unused. The adapter does not supply 5 V to the module.
7. Use a straight 26-way keyed IDC ribbon (pin 1 to pin 1); route it away from transducer outputs and the 12 V input. Support the external core board so insertion force and cable strain are not carried by loose leads.
8. Keep module 5 V and array 12 V supply wiring distinguishable. The grounds meet through the ribbon. Confirm the intended supply sequencing from DESIGN_NOTES.md before later powered testing.

Additional assembly items not represented as PCB components: CoreEP4CE6 module, IDC ribbon/socket pair, standoffs/fasteners, module support, regulated supplies, JTAG programmer, and optional IC sockets. F1's provisional 1 A rating and exact capacitor/connector selections require confirmation against the actual load and manufacturer capabilities.
