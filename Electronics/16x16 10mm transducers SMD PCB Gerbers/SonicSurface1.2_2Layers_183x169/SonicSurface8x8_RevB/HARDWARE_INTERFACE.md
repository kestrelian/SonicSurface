# Interface contract — Rev B

This is a hardware interface specification for the external firmware and software projects. No implementation of either project is supplied.

## Signal cables

Two identical, straight, keyed 2×13 IDC cable assemblies, 2.54 mm connector pitch / 1.27 mm ribbon pitch, maximum 100 mm each. Use factory strain-relief covers on the mating IDC sockets; support the cable at the enclosure so insertion force does not load the Core module socket. Do not use reversed or twisted pin-number mappings. Interleaved grounds occupy every even pin.

| Odd pin | Function |
|---|---|
| 1 | Adapter-regulated +3V3 |
| 3, 5, 7, 9, 11, 13, 15, 17 | DATA0 through DATA7 |
| 19 | SCLK |
| 21 | LATCH |
| 23 | OE_N, high disables that array |
| 25 | CLR_N, low clears shift stages |

All even pins are GND. There is no driver power on this cable.

The 100 mm / 4 MHz limit is set for single-ended LVC signalling with 33 Ω source resistors. Substantially longer cables need differential signalling (for example RS-485/LVDS drivers on the adapter and receivers on each array) with its own connector and termination design; that is a larger interface change and is not part of Rev B. Rev B uses the same basic signal pinout as Rev A but changes the power source and adds receive buffering; do not mix power systems without reviewing their supply connections.

Adapter J2 goes to array A J1; adapter J3 goes to array B J1. Shared FPGA SCLK and LATCH inputs drive separate buffer channels and separate 33 Ω source resistors for A and B. Each array has independent FPGA OE_N and CLR_N. Sixteen DATA outputs are independent. No passive Y splitter is used.

Core P1 pins 1/23 provide the common ground. Pin 2 only senses Core 3.3 V and biases its own input-side enable pullups; it is not tied to adapter +3V3. Pin 24 (5 V) is NC. The exact P1 and FPGA package assignments are in `FPGA_INTERFACE.csv`. They were taken from the locally retained Waveshare schematic; pins used for JTAG, configuration, the oscillator and power are excluded from data/control assignments.

## Timing and ordering

Provisional maximum SCLK: 4 MHz, with high and low times of at least 125 ns at the array receiver. Keep DATA stable at least 125 ns before SCLK rising and at least 25 ns afterward. Allow at least 250 ns between the last SCLK rising edge and LATCH rising. LATCH high and low widths must each be at least 125 ns. All limits are hardware design requirements pending waveform measurement; component, cable and routing skew remain to be established.

Each DATA lane loads one row. The array routing channel fixes the shift-register output order: QA drives column 0, then QB through QH drive columns 7, 6, 5, 4, 3, 2 and 1. The first bit shifted ends in QH, so shift columns 1, 2, 3, 4, 5, 6 and 7, then column 0 last, then latch. `CHANNEL_MAP.csv` lists the output pin for every channel. Eight SCLK edges transfer a complete 64-channel state on each board, concurrently. Grounded MA40S4S return terminals mean single-ended drive, approximately 16.8 Vp-p before losses, not bridge drive.

At the provisional interface rate, the external firmware must budget latch overhead as well as eight shift cycles per update. High phase-resolution operation may require a separately qualified faster interface or an alternative waveform schedule. A 4 MHz ceiling does not promise 32 or 64 uniform phase steps at 40 kHz.

## Startup and power loss

Keep OE_N high during FPGA configuration and power transitions. The adapter tri-states its cable buffers while the Core rail is below approximately 3.03 V. Cable-side OE pullups and array-side pullups default to disabled.

Array `OE_LOCAL_N = OE_CMD_N OR NOT(RAILS_OK)`. The logic supervisor requires approximately 3.07 V. Its reset drives the driver supervisor's manual-reset input; the driver supervisor requires approximately 15.55 V. Each supervisor has its open-CT startup delay, nominally 20 ms. Hardware prevents output enabling before both rails qualify, independent of the FPGA command.

After supplies qualify: assert clear, release clear, clock zeros, pulse latch, then enable. Clear does not clear the output storage latch. Before deliberate shutdown, disable outputs first. Supervisors respond after finite delay; abrupt short-circuit behavior and input voltage relative to TC4427 VDD remain mandatory prototype checks.

SN74LVC244A input buffers prevent the powered FPGA from feeding the unpowered array logic through ordinary input clamps. They do not constitute hot-plug, ESD or galvanic-isolation certification. No 5 V signaling is permitted.

## Separate driver-power wiring

Adapter J4 accepts regulated external 17–20 V DC. J5 supplies array A J2; J6 supplies array B J2. All power connectors use pin 1 positive and pin 2 GND. Use matching keyed Molex 43650-0215 headers, 43645 two-position housings and manufacturer-approved contacts for the chosen wire gauge; choose 22 AWG copper or larger for the short power leads. Verify mating part suffixes during procurement. Never connect the raw external supply directly to array J2.

Power cables must carry the full driver return current. Signal-cable grounds provide reference and signal returns, not the sole power return. The regulated power outputs share a regulator and cutoff stage, with individual fuses; a severe fault may interrupt both boards. There is no independent power switching command.

## Test access and geometry

Array pads expose GND, +3V3, VDRV, SCLK, LATCH, OE_LOCAL_N, RAILS_OK, DRV00 and DRV63. DRV00 (TP8) sits beside T1 and DRV63 (TP9) beside T64; SCLK, LATCH and OE_LOCAL_N pads sit on their bus ends below the shift registers. Adapter pads expose raw/protected/regulator/output rails, Core-good and both clock/enable branches. Use short probe ground connections for edge measurements.

`CHANNEL_MAP.csv` gives local coordinates at 10.3 mm pitch. Board A/B placement, rotation, separation and acoustic polarity calibration belong to the external system configuration, not hardcoded assumptions here.
