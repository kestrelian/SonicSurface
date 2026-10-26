from pathlib import Path
import csv,json,collections
root=Path(__file__).resolve().parent
q=(root.parent/'SonicSurface8x8/QA_CHECKLIST.md').read_text()
q=q.replace('12 mm','10.3 mm').replace('160 x 124 mm','114 x 120 mm').replace('38 x 65 mm','120 x 140 mm').replace('12 V','16.8 V').replace('+12V','VDRV').replace('resolve the absence of an automatic interlock for the intended application','verify both supervisors, the OE gating and input pulldowns under all supply sequences')
q=q.replace('module regulator temperature','dedicated adapter regulator temperature')
q=q.replace('## 8. Acoustic and release review', '''## 8. Rev B power and dual-array release gates

- [ ] Independently review the 16.8 V setpoint tolerance, the 17.5 V nominal cutoff tolerance, propagation delay, MOSFET gate discharge and regulator fault slew. Demonstrate less than 18 V at every TC4427 supply pin including ringing; the conditional capacitor estimate is not proof.
- [ ] Test regulator startup, load steps, input steps from 17 to 20 V, reverse input, brownout and current limit with appropriate protected test equipment. Validate compensation with measured loop response across input, load, capacitance/ESR and temperature corners.
- [ ] Review the switching-loop placement/routing and exposed-pad thermal path against LTC3115-1 layout guidance. Resolve long switch paths, thin power neckdowns and feedback coupling before release.
- [ ] Verify TPS26600 RTN remains isolated from GND as required by its reverse-input architecture, including the exposed pad and thermal vias.
- [ ] Coordinate the input eFuse, 2 A fuse, branch 750 mA fuses, wiring and connector fault ratings. Verify short-circuit recovery, inrush and output-capacitor energy.
- [ ] Establish effective MLCC capacitance at operating voltage, ripple current, ESR, temperature and bulk capacitor lifetime from exact purchased part numbers.
- [ ] Test 3.3 V load/headroom for two arrays. Confirm Core P1.2 never ties to the adapter regulator output, including cable mistakes, supply-off states and instrumentation grounds.
- [ ] Verify per-board OE independence and simultaneous A/B data transfer with both cables attached. Measure the 100 mm / 4 MHz provisional interface at the worst receiver.
- [ ] Test an unpowered Core, unpowered adapter, either unpowered array and abrupt driver-rail loss. Confirm no unintended transducer pulses or excessive input injection.
- [ ] Measure voltage directly across MA40S4S at all switching patterns; keep the complete continuous waveform within 20 Vp-p. Confirm 22 ohm damping with measured ringing, dissipation and acoustic output.
- [ ] Measure rail discharge with both boards, one board and no boards connected; document the actual safe handling delay.
- [ ] Inspect 10.3 mm pitch with maximum body diameter and positional tolerances. Fit actual DIP parts and transducers on both sides; assess protruding lead clearance and solder access.
- [ ] Reconcile test points, channel CSV, FPGA P1 map, keyed cable pin numbering and actual Core board revision. Firmware qualification remains a separate project.

## 9. Acoustic and release review''')
(root/'QA_CHECKLIST.md').write_text(q)
with (root/'CABLE_PIN_MAP.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Pin','Array J1 function','Adapter J2 bank A','Adapter J3 bank B','Wire requirement'])
 funcs={1:'+3V3',**{3+2*i:f'DATA{i}' for i in range(8)},19:'SCLK',21:'LATCH',23:'OE_N',25:'CLR_N'}
 for pin in range(1,27):
  s=funcs.get(pin,'GND');w.writerow([pin,s,s if s in ['GND','+3V3'] else 'A_'+s,s if s in ['GND','+3V3'] else 'B_'+s,'Straight keyed IDC26; <=100 mm'])
with (root/'CHANNEL_MAP.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Local channel','Row zero based','Column zero based','Transducer','Shift register','Output pin','Driver','Driver output pin','X mm','Y mm','A system channel','B system channel'])
 for n in range(64):
  r,c=divmod(n,8);w.writerow([n,r,c,f'T{n+1}',f'U{r+1}',[15,1,2,3,4,5,6,7][c],f'U{101+n//2}',7 if n%2==0 else 5,round(8+10.3*c,2),round(8+10.3*r,2),n,64+n])
for name in ['Array8x8_RevB','DualArray_Controller_RevB']:
 folder=root/name
 data=list(csv.DictReader((folder/'BOM.csv').open()));groups=collections.defaultdict(list)
 for row in data:groups[(row['Value / part'],row['Footprint'])].append(row['Reference'])
 with (folder/'BOM_grouped.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['References','Value / part','Footprint','Per PCB quantity','System quantity','Status'])
  for (val,fp),refs in groups.items():w.writerow([' '.join(refs),val,fp,len(refs),len(refs)*(2 if name.startswith('Array') else 1),'Engineering selection; procurement/release review pending'])
 pro=json.loads((folder/(name+'.kicad_pro')).read_text());pro['net_settings']['classes'][1]['track_width']=.5 if name.startswith('Dual') else 1.
 (folder/(name+'.kicad_pro')).write_text(json.dumps(pro,indent=2))
s=(root/'build_revb.py').read_text().replace('track_width=1.0)','track_width=.5 if self.name.startswith(\'Dual\') else 1.0)')
(root/'build_revb.py').write_text(s)
s=(root/'export_fabrication.py').read_text().replace("['Array8x8','CoreEP4CE6_Adapter']","['Array8x8_RevB','DualArray_Controller_RevB']").replace('REV A','REV B').replace('../../DESIGN_NOTES.md','../../POWER_DESIGN.md')
(root/'export_fabrication.py').write_text(s)
print('Rev B checklists, interface maps, grouped BOMs and project rules written; no final checks executed.')
