# Power design basis — Rev B

These are component-selection and sizing calculations, not executed final QA or prototype results. The complete rail transient response, thermal performance and transducer waveform are unverified.

## Selected architecture

The 17–20 V source connects only to adapter J4. F1 is a 2 A, 125 V Littelfuse 451-series fuse. TPS26600 provides reverse-input protection, input UV/OV cutoff, controlled startup and nominal 1.49 A active current limiting. Its RTN and exposed pad are on an isolated IN_RTN island, not GND. The following regulator feeds two identical arrays through a common precision output cutoff and individual 750 mA, 125 V 451-series fuses.

Driver generation: LTC3115IFE-1 buck-boost, 15 µH inductor, approximately 750 kHz forced PWM, 158 kΩ/10 kΩ feedback divider, nominal 16.8 V. It can regulate near the input voltage after input protection losses. No series-diode-drop regulation is used.

Output cutoff: LTC4365ITS8 and Si9945CDY back-to-back MOSFETs, nominal 15.0 V undervoltage and 17.5 V overvoltage thresholds. The output has 470 µF bulk capacitance before branch fuses. A second 470 µF capacitor sits on the regulator side. A 47 nF gate-to-common-source capacitor slows connection of the array bulk capacitance. The input eFuse remains the active current limiter; output fuses are branch backup protection, not precision current regulators.

## Static voltage budget

The feedback equation gives `1.000 × (1 + 158/10) = 16.8 V`. With the LTC3115-1's specified 0.977–1.017 V feedback range and opposing 0.1% divider tolerances, the resistor/reference-only range is approximately **16.38–17.12 V**. Add allowance for feedback bias, line regulation, ripple and wiring loss; static arithmetic is not a transient guarantee.

The LTC4365 output OV divider is 340 kΩ/10 kΩ, **0.01%**, selected for threshold margin. With its 0.4925–0.5075 V threshold range, the resistor/reference-only cutoff range is approximately **17.23–17.77 V**. Input leakage and resistor temperature coefficients also enter the release calculation. Select low-drift precision resistors; substituting 1% parts invalidates the margin.

The highest static cutoff leaves approximately 0.23 V below the TC4427's 18 V operating ceiling. That remaining budget must cover cutoff response and parasitic overshoot. The 470 µF protected bulk capacitor is intentional: at its -20% tolerance, a 3.7 A excess for 20 µs would raise it approximately `3.7 × 20 µs / 376 µF = 0.197 V`. This is a conditional sizing estimate, not a proof of a 20 µs cutoff or a bound on every possible fault. Measure the complete response with actual source impedance, gate charge, temperature and wiring before release. If margin is inadequate, reduce the rail/OV setpoints or redesign cutoff speed; do not raise the threshold.

For MA40S4S, the maximum continuous 40 kHz square-wave input is 20 Vp-p. The design uses single-ended drive and 22 Ω output damping, leaving roughly 3 V of nominal waveform headroom. Overshoot/undershoot must be measured across the transducer itself. The 22 Ω starting value is not a certified ringing limit.

## Input thresholds and startup

TPS26600 dividers: UV 121 kΩ/10 kΩ gives about 15.59 V rising; OV 178 kΩ/10 kΩ gives about 22.37 V rising. Device and resistor tolerances apply. These thresholds accept a nominal 17–20 V source and protect the 28 V maximum input of the logic regulator against sustained excess voltage. Source surges still require later validation.

The 8.06 kΩ ILIM resistor gives approximately `12 / 8.06 = 1.489 A`. The 100 nF dV/dt capacitor gives a nominal output ramp of approximately `24.6 × 4.7 µA / 100 nF = 1.16 V/ms`. Converter soft-start and output-switch turn-on occur downstream; total inrush must be assessed as a sequence, not by adding fuse ratings.

The 47 nF output gate capacitor limits nominal gate slew to roughly 0.43 V/ms at 20 µA. MOSFET transfer characteristics make actual output slew load-dependent. The input current limiter bounds overload response; startup, SOA and fault coordination remain deferred checks.

## Load, copper and connector budgets

MA40S4S capacitance is nominally 2.55 nF ±20% at 1 kHz. A first-order capacitive charging estimate at 3.06 nF, 17.2 V and 40 kHz is `64 C V f ≈ 0.135 A` per array. This omits the acoustic motional branch. A conservative all-high driver-current allowance using 8 mA per dual IC adds 0.256 A, and the 2.2 kΩ bleeder adds about 8 mA. Allocate **0.45 A per array** and **0.9 A total** as a provisional engineering budget, pending measurement. It is not a measured maximum; do not treat the nominal-capacitance estimate as the complete resonant load model.

At 16.8 V/0.9 A and an assumed 85% conversion efficiency, input demand at 17 V is approximately 1.05 A, plus the separate logic supply. This is below nominal eFuse limiting but leaves limited startup/temperature margin. Select an external current-limited 17–20 V source capable of at least 1.5 A; a 2 A source provides operating headroom without changing on-board protection settings.

Routing targets: array driver rail 0.8 mm feeder down the left edge (whole-board 0.45 A) branching into one 0.5 mm back-copper trunk per driver row (four TC4427s, about 0.06 A), 0.4 mm driver and capacitor stubs; 0.5 mm adapter power routes, 0.5 mm logic supply and 0.4 mm routed ground, supplemented by copper pours. Nominal 35 µm copper is assumed. The legacy external-trace IPC-2221 estimate gives about 1.45 A at 10°C rise for a 0.5 mm track; this is only a preliminary sizing rule, not IPC-2152 or thermal signoff. At 1.1 A, 100 mm of 0.5 mm/35 µm copper has about 0.108 V drop and 0.119 W loss using 1.72e-8 Ωm resistivity. Neckdowns, actual lengths, return bottlenecks, copper tolerances and thermal environment must be checked on the finished layout.

Use short 22 AWG or larger copper power leads and rated Micro-Fit contacts/housings. The selected power header family is keyed and separate from logic IDC. Confirm contact derating for wire gauge, ambient temperature and assembled harness before procurement. A branch fuse's time-current curve, interrupting capacity and pulse I²t must coordinate with the chosen source and eFuse; the ratings alone do not prove coordination.

## Logic rail and inhibit

R-78E3.3-0.5 supplies up to 0.5 A nominally from the protected input. Design allocation: 100 mA per array plus 50 mA for adapter buffers/supervision and 10 mA minimum load, total 260 mA. This allocation includes allowance beyond the output pulldowns and logic switching estimates. Confirm current and regulator derating during deferred review. The 330 Ω preload draws 10 mA and dissipates 33 mW. Connected capacitance is well below the module's listed 220 µF limit.

Core P1 3.3 V supplies only its own source-side bias and the high-impedance Core-good divider. No adapter regulator output is joined to a Core power rail. Core reset/rail loss makes cable drivers high impedance. Each array separately qualifies its own 3.3 V and driver rail before permitting output enable.

Array driver undervoltage divider: 374 kΩ/10 kΩ into TPS3808G01 gives `0.405 × 38.4 = 15.552 V`; tolerances and hysteresis apply. The logic supervisor is TPS3808G33, nominal threshold 3.07 V. Hardware gating responds after finite delays; a shorted driver rail needs explicit input-clamp/back-power assessment. No fault-rated emergency-stop claim is made.

## Capacitors, damping and compensation

Driver bypassing remains 100 nF plus 1 µF per TC4427, rated 50 V. Use X7R and select actual orderable parts with retained capacitance at 17 V; aim for at least 0.5 µF effective local bulk per driver. Array bulk remains 220 µF/35 V low ESR. Adapter uses 470 µF/35 V on both sides of the output cutoff and two 22 µF/50 V ceramic regulator-output capacitors. Specify at least 1 A ripple capability for adapter bulk capacitors and confirm combined ripple sharing; capacitance and voltage rating alone are insufficient.

The regulator has Type III compensation: RFB 18 kΩ, CFB 8.2 nF, CPOLE 150 pF, RFF 2.67 kΩ and CFF 1 nF. These give zeros near 1.08 kHz and 0.99 kHz, and poles near 60 kHz. A preliminary lumped small-signal design calculation explored 0.4–1.8 mF effective output capacitance, 0–40 mΩ ESR and 0.35 Ω power-stage series resistance. It suggested a feasible loop; cable inductance, distributed capacitors, discontinuous conditions, exact effective capacitance and load steps were not represented. Closed-loop simulation/measurement and transient tuning remain required; no stability test result is supplied.

22 Ω series damping resistors dissipate only a fraction of `C V² f` under the simple capacitive model; use at least 0.1 W rated 0603 parts. Real waveform/ringing may require changes. The 2.2 kΩ/0.5 W array bleeder dissipates about 0.13 W at 16.8 V. With approximately 252 µF local capacitance, its nominal time constant is 0.55 s and decay from 16.8 V to 1 V takes about 1.6 s. The shared protected adapter bulk can lengthen system discharge to several seconds. Confirm residual voltage before handling.

## Primary references

- [TC4427](https://ww1.microchip.com/downloads/en/DeviceDoc/20001422G.pdf)
- [MA40S4S](https://www.murata.com/-/media/webrenewal/products/sensor/ultrasonic/open/datasheet_maopn.ashx)
- [LTC3115-1](https://www.analog.com/media/en/technical-documentation/data-sheets/31151fb.pdf)
- [TPS26600](https://www.ti.com/lit/ds/symlink/tps2660.pdf)
- [LTC4365](https://www.analog.com/media/en/technical-documentation/data-sheets/4365fa.pdf)
- [Si9945CDY](https://www.vishay.com/docs/61735/si9945cdy.pdf)
- [R-78E3.3-0.5](https://recom-power.com/pdf/Innoline/R-78E-0.5.pdf)
- [TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf)
- [SN74LVC244A](https://www.ti.com/lit/ds/symlink/sn74lvc244a.pdf)
- [Littelfuse 451/453](https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1)
