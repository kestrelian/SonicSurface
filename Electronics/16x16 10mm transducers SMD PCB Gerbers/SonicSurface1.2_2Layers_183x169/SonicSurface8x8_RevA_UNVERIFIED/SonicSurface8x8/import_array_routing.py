"""Import the authored Specctra session and add ground pours; no final QA."""
from pathlib import Path
import json
import pcbnew as p
root=Path(__file__).resolve().parent/'Array8x8'
b=p.LoadBoard(str(root/'authoring/placed.kicad_pcb'))
if not p.ImportSpecctraSES(b,str(root/'authoring/routed.ses')):
    raise RuntimeError('Session import failed; no manufacturing export should be made.')
for layer in [p.F_Cu,p.B_Cu]:
    zone=p.ZONE(b);zone.SetLayer(layer);zone.SetNetCode(b.FindNet('GND').GetNetCode())
    zone.SetLocalClearance(p.FromMM(.25));zone.SetThermalReliefGap(p.FromMM(.25));zone.SetThermalReliefSpokeWidth(p.FromMM(.4));zone.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
    outline=zone.Outline();outline.NewOutline()
    for x,y in [(.8,.8),(159.2,.8),(159.2,123.2),(.8,123.2)]:outline.Append(p.FromMM(x),p.FromMM(y))
    b.Add(zone)
p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(root/'Array8x8.kicad_pcb'),b)
(root/'routing_status.json').write_text(json.dumps({'engine':'Freerouting 2.5.0 Java, local','session':'authoring/routed.ses','status':'Session imported; see authoring/router.log for router completion status','final_checks':'NOT EXECUTED','ground':'Explicit routed ground connections supplemented by copper pours'},indent=2))
print('Imported routing session and authored ground pours. No ERC/DRC or final Gerber review performed.')
