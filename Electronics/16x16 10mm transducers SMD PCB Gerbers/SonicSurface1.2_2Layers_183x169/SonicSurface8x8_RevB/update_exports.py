from pathlib import Path
import json
root=Path('SonicSurface8x8_RevB')
for name in ['Array8x8_RevB','DualArray_Controller_RevB']:
 f=root/name/(name+'.kicad_pro');d=json.loads(f.read_text());r=d.setdefault('board',{}).setdefault('design_settings',{}).setdefault('rules',{});r['min_track_width']=.15;r['min_through_hole_diameter']=.2;r['min_via_diameter']=.5;r['min_via_annular_width']=.15;f.write_text(json.dumps(d,indent=2))
f=root/'README.md';s=f.read_text().replace('25 October 2026','26 October 2026').replace('These changes permit nominal 0.15 mm clearance routing','These changes permit nominal 0.15 mm clearance routing, with local 0.15 mm trace escapes and some 0.50/0.20 mm diameter/drill vias');f.write_text(s)
f=root/'ASSEMBLY_NOTES.md';s=f.read_text().replace('Dense SMD escapes may use smaller vias and narrow traces','Dense SMD escapes include 0.50 mm vias with 0.20 mm drills (0.15 mm nominal annular ring), and local 0.15 mm trace neckdowns. Confirm these capabilities with the fabricator. These escapes use smaller vias and narrow traces');f.write_text(s)