from pathlib import Path
import pcbnew as p
f=Path('SonicSurface8x8_RevB/Array8x8_RevB/authoring/work.kicad_pcb');b=p.LoadBoard(str(f));b.BuildConnectivity();c=b.GetConnectivity();nets={}
for fp in b.GetFootprints():
 for q in fp.Pads():
  if q.GetNetCode():nets.setdefault(q.GetNetCode(),[]).append(q)
for n,pads in nets.items():
 groups={}
 for pad in pads:
  ids=sorted(o.m_Uuid.AsString() for o in c.GetConnectedItems(pad) if isinstance(o,p.PAD));key=ids[0] if ids else pad.m_Uuid.AsString();groups.setdefault(key,[]).append(pad.GetParentFootprint().GetReference()+'.'+pad.GetNumber())
 if len(groups)>1:print(b.FindNet(n).GetNetname(),list(groups.values()))
