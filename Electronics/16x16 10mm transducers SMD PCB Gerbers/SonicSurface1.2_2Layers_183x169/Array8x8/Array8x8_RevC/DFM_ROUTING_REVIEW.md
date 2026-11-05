# Array8x8_RevB — DFM and routing review (JLCPCB 2-layer, 0.18 mm floor)

2 November 2026. Reviewed the board that generated `fabrication_REVISED/` (Gerber X2 + Excellon, regenerated today), with:
- a review-only rule set: JLCPCB standard 2-layer limits, with every physical dimension floored at 0.18 mm;
- the project's own JLCPCB rules;
- geometry measurements;
- a direct read of the drill and outline files.

Every finding below already existed before today's changes (verified against `../Array8x8_RevB_backup_before_TP/`).

## Changes made today

- **17 new test pads, all on the back, each routed under a 0.2 mm via-to-track rule with no via in any pad:**
  - TP10–TP17: one per shift-register row, on the column-0 output (Q00, Q08 … Q56).
  - TP18–TP26: FPGA inputs at J1, DATA0_RX–DATA7_RX and CLR_N_RX. SCLK_RX, LATCH_RX and OE_N_RX already had TP4–TP6.
  - Schematic symbols are on sheet Test_02, now A2. TEST_POINTS.csv, the BOM and the placement file are updated.
- **Mounting hole H5** (3.2 mm, M3) at X 105, Y 158. One ground stitching via moved from (104, 159) to (107.4, 158).
- **Outline expanded 6.35 mm (0.25") on every side:** 114 × 120 mm → 126.7 × 132.7 mm. Ground pours follow the new edge. All parts, including holes H1–H4, are unchanged in position.
- **Checks after the changes:** no new DRC items against the project rules, and every net matches the schematic.

## Findings

| # | Severity | Item | Limit | Found | Where | Fix |
|---|---|---|---|---|---|---|
| 1 | **Fixed** | Pad-to-pad near-short | 0.18 mm floor, 0.10 mm solder-mask web | Was 0.033 mm in 5 places plus 6 solder-mask bridges; now clear | R113, R121, R129, R137, R161, R153 moved 0.25 mm away from T5, T13, T21, T29, T53, T45 | Done |
| 2 | **Fixed** | Driver decoupling not connected (VDRV open) | Must connect | Was 3 unconnected; now 0 | C224, C228, C232 pad 1 joined to the VDRV stubs (0.4 mm) | Done |
| 3 | **High** | Via annular ring | ≥ 0.18 mm (JLC absolute min 0.18, recommended 0.25) | 0.15 mm (22 vias 0.60/0.30), 0.175 mm (406 vias 0.65/0.30) | Whole board | Reduce drills: 0.60/0.20 and 0.65/0.25 give 0.20 mm rings; nothing else moves |
| 4 | **High** | Track-to-track spacing | ≥ 0.18 mm | 0.127 mm, 19 places (JLC nominal minimum) | DATA4_RX / DATA5_RX between J1 and the shift registers (~134–142, 130–139) | Re-space to ≥ 0.18 mm |
| 5 | **High** | Via to track | ≥ 0.20 mm | 0.155–0.20 mm, 30 places | J1 / signal fan-out, e.g. OE_N_RX–CLR_N_RX via at (149.8, 139.4) | Nudge vias or re-route |
| 6 | Medium | Track width | ≥ 0.18 mm | 0.15 mm, 14 segments | SCLK_RX near (146, 148) | Widen to 0.2 mm |
| 7 | Medium | Via to via, different nets | ≥ 0.18 mm | 0.175 mm | DATA1_RX / DATA0_RX vias at (141.0, 139.3) | Move one via 0.05 mm |
| 8 | Medium | Via in SMD pad | Avoid, or order filled and capped vias | 7 pads | R111, R113, R119, R28, C222, C227, C231 (GND pads) | Move the vias beside the pads, or order via-in-pad filling |
| 9 | Low | Acute track corners (etch traps) | ≥ 90° | 6 corners: one 0° overlapping segment, others 28–65° | DATA5_RX (134.1, 145.6) 0°; DATA0/2/7_RX near J1; Q08 (56.5, 57.3) | Re-draw the corners at 45° |
| 10 | Low | Silkscreen line width | ≥ 0.15 mm | 0.10 mm transducer outlines (front) | All 64 transducers | Set outline width to 0.15 mm |
| 11 | Low | Silkscreen to pad | ≥ 0.15 mm | 0.075 mm min, 10 places | Various | Fab clips silk from pads; cosmetic |
| 12 | Info | Assembly fit | — | 87 courtyard overlaps; 199 driver leads inside transducer outlines; H2 hole inside U1 courtyard | Array cells; H2 (160.5, 44.5) | Trim driver leads flush before fitting transducers; check H2 screw head against U1 |
| 13 | Pass | Plated-hole annular ring | ≥ 0.18 mm (JLC 0.20) | 0.20 mm (transducer 1.6 / 1.2 mm) | — | At JLC's limit; confirm drill registration |
| 14 | Pass | Holes and drills | 0.20–6.3 mm; gaps ≥ 0.5 mm (different nets) / 0.254 mm (same net) | 0.20–3.2 mm; min gap 0.269 mm (same net) | Excellon, metric | — |
| 15 | Pass | Solder-mask web, edge clearance, outline | ≥ 0.18 mm web; ≥ 0.3 mm edge | No SMD web under 0.18 mm; edges clear; 126.7 × 132.7 mm closed outline | Gerbers | — |
| 16 | Info | Footprints differ from library | — | 85 | Intentional pad and courtyard edits | None |

Items 1 and 2 were fixed on 2 November 2026. DRC afterwards shows 0 unconnected items, no new violations, and every net matching the schematic. `fabrication_REVISED/` was regenerated, and the pre-fix board is in `../Array8x8_RevB_backup_before_fix12/`. Items 3–8 still fail the 0.18 mm floor or JLCPCB's via limits and remain open.
