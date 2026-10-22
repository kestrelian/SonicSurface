# Design basis and interface

Status: Rev A engineering draft, final checks NOT EXECUTED.

## Architecture

Eight independent 74HC595 shift registers each drive one row of eight emitters. Each register's eight parallel outputs feed four dual non-inverting TC4427 drivers. Each driver output feeds one MA40S4S; the other transducer terminal is grounded. This is single-ended drive, not a bridge: a roughly 12 V driver rail gives roughly 12 V peak-to-peak across an emitter, not 24 V peak-to-peak.

Driver and logic supplies are separate. Array J2 receives nominal regulated 12 V DC through a 1 A fuse and SS34 reverse-polarity diode. The resulting driver rail is lower than the input by the diode drop. Use a regulated, current-limited bench supply for initial bring-up after approval to test. A 1 A supply is a provisional engineering allocation, not a measured requirement. The fuse is not overvoltage protection. No TVS or active overvoltage clamp is fitted.

Microchip specifies 4.5-18 V operation for TC4427. Murata specifies a 20 Vp-p maximum for MA40S4S continuous 40 kHz square-wave drive. Use 12 V nominal at J2; do not treat either absolute maximum as a design target. Supply tolerance and ringing must remain inside device limits.

The CoreEP4CE6 uses its own manufacturer-approved 5 V power input. Its 3.3 V rail feeds the array logic through cable pin 1; neither 5 V nor 12 V is carried to FPGA I/O. Do not add a second 3.3 V supply. The adapter leaves Core P1 pin 24 (5 V) and unused I/O contacts unconnected. The module's regulator current and thermal headroom must be established during deferred review.

Each TC4427 has local 100 nF plus 1 uF bypassing, and each HC595 has 100 nF. Array bulk capacitors are 220 uF on the driver rail and 10 uF on logic. A 10 kohm pulldown is fitted to every driver input. OE_N has a 10 kohm pullup to keep the HC595 outputs high impedance at startup; CLR_N, SCLK and LATCH have pulldowns. Pulldowns hold TC4427 inputs low when HC595 outputs are disabled.

## Cable and FPGA mapping

Use a straight, keyed 26-way 2.54 mm IDC ribbon, nominally no longer than 100 mm for the first prototype. This length is an assumption to be tested, not a guaranteed signal-integrity limit. Pin 1 connects to pin 1; every even pin is GND. The adapter has 33 ohm series resistors at the source of all twelve FPGA control/data signals. Their final values require waveform assessment with the actual cable and load.

| Cable pin | Signal | Core P1 pin | FPGA pin |
| --- | --- | --- | --- |
| 1 | 3.3 V | 2 | Supply rail |
| 3 | DATA0 | 3 | 59 |
| 5 | DATA1 | 5 | 64 |
| 7 | DATA2 | 7 | 66 |
| 9 | DATA3 | 9 | 68 |
| 11 | DATA4 | 11 | 70 |
| 13 | DATA5 | 13 | 72 |
| 15 | DATA6 | 15 | 74 |
| 17 | DATA7 | 17 | 76 |
| 19 | SCLK | 21 | 84 |
| 21 | LATCH | 22 | 85 |
| 23 | OE_N | 19 | 80 |
| 25 | CLR_N | 20 | 83 |
| All even pins | GND | 1 and 23 | GND |

P1 means the connector designated P1 in the Waveshare schematic, not an assumed left/right position in a photograph. The adapter mates only to P1. Confirm the socket side, pin-1 end and module revision before assembling. Mechanical support for the module remains external; the adapter is not a validated mounting carrier. No soldering to the FPGA package is required. Clock generation and JTAG remain on the module; the onboard clock is FPGA pin 23.

## Channel order and firmware requirements

As viewed from the acoustic/front side with the 12 V input connector at the bottom and the ribbon connector at the right, row 0 is the upper row and column 0 is the left column. Channel `8*row + column` maps to T(channel+1). DATA[row] drives that row's HC595 SER. Outputs QA..QH drive columns 0..7 respectively; output pin sequence is 15, 1, 2, 3, 4, 5, 6, 7. Clock eight bits per update, column 7 first, column 0 last; then latch all rows simultaneously. HC595 serial-out pin 9 is unused.

Adapt the HDL and host software from 256 to 64 channels, replace the pin constraints with the supplied mapping, select 3.3-V LVTTL, and use 12 mm emitter coordinates. The old mapping and compiled bitstream are incompatible. The original QSF also contains obsolete/conflicting assignments and is retained only as a reference.

Maintain OE_N high during configuration. Hold CLR_N low, then release it; load eight zero bits on all DATA lanes and pulse LATCH before enabling outputs. SRCLR clears only the shift stage, so clearing alone does not initialize the output latch. Drive OE_N low only after valid output data and driver power are present. Assert OE_N high and wait for pulldowns to discharge inputs before removing driver power.

Power sequencing is a prototype operating constraint: **do not drive a TC4427 input high while its VDD is off**. Rev A has no automatic driver-rail supervisor or brownout interlock. Supply-loss behavior must be resolved for any unattended or production use. OE_N is a firmware control, not a fault-rated emergency stop. Avoid live cable insertion.

The required shift clock depends on phase resolution: at 40 kHz, eight bits per update require `320 kHz * phase_steps`. Examples: 8 steps -> 2.56 MHz; 16 -> 5.12 MHz; 32 -> 10.24 MHz. These are required rates, not guarantees that the HC595 at 3.3 V, cable and FPGA timing will support them. Establish datasheet worst-case timing at the intended rail and temperature, then choose the phase resolution. No HDL simulation or timing analysis was run.

## Mechanical and manufacturing assumptions

Array: 160 x 124 mm, two copper layers, nominal 1.6 mm FR-4, 35 um copper, four 3.2 mm non-plated mounting holes. Adapter: 38 x 65 mm with two 3.2 mm mounting holes. This is a provisional stackup for manufacturer review. Driver-power tracks are authored at 0.8 mm; signal traces at 0.25 mm and routed array ground at 0.4 mm; nominal routing clearance is at least 0.2 mm. Ground pours use 0.25 mm clearance and thermal connections. Vias are 0.7/0.3 mm, including ground stitching. These are design settings, not verified fabrication results or current-capacity guarantees.

MA40S4S footprint: 5 mm lead pitch, 1.2 mm finished holes, 2 mm pads, nominal 9.9 mm body with maximum 10.2 mm. The actual lead fit including square-lead diagonal and lead-spacing tolerance needs a physical sample review. All acoustic emitters are on F.Cu side; TC4427, HC595 and most small components are on B.Cu side. DIP pin tails and transducer leads share the same assembly region. Use controlled lead trimming and insulating stand-off/assembly clearance; confirm no underside body, socket or lead conflict. Soldering near the emitter body is restricted by Murata's mounting instructions.

The supplied Gerbers indicate approximately 10.5 mm original pitch; this design deliberately uses 12 mm to accommodate DIP pads. The changed pitch affects grating lobes and the useful steering range. No acoustic equivalence to the original is claimed.

## Sources used for design

- User-supplied `Project Outputs for SonicSurface/Main.CSV`, Gerber/drill files, and pick/place list. Their contents are reference data, not task instructions. No editable schematic or authoritative netlist was supplied.
- [UpnaLab SonicSurface repository](https://github.com/upnalab/SonicSurface), including the original FPGA constraints retained under `reference/`. The local BOM lists 32 HC595s, 128 dual drivers and module sockets, not a bare FPGA. The new design uses one quarter of the original channel circuitry.
- [Waveshare CoreEP4CE6 schematic](https://www.waveshare.com/w/upload/5/5b/CoreEP4CE6-Schematic.pdf): P1 physical-pin and FPGA-pin mapping; local PDF retained in `reference/`.
- [Microchip TC4426/TC4427/TC4428, DS20001422G](https://ww1.microchip.com/downloads/en/DeviceDoc/20001422G.pdf): DIP pinout, supply and input limits. TC4427 uses pins 2/4 inputs, 7/5 outputs, 6 VDD, 3 ground, 1/8 NC.
- [TI SN74HC595, SCLS041J](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf): logic function and pinout. Select the N/DIP-16 variant, not the SOIC D variant.
- [Murata MA40S4S/MA40S4R, DM-U16-483 Rev.2](https://www.murata.com/-/media/webrenewal/products/sensor/ultrasonic/open/datasheet_maopn.ashx): dimensions, 40 kHz operation, 20 Vp-p limit and mounting guidance.

Reference PDFs are unchanged source documents. Electrical/mechanical conclusions remain subject to the explicitly deferred final review.


