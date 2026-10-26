import pcbnew as p
b=p.LoadBoard('SonicSurface8x8_RevB/DualArray_Controller_RevB/authoring/work.kicad_pcb')
def xy(v):return round(p.ToMM(v.x),4),round(p.ToMM(v.y),4)
for f in b.GetFootprints():
 for q in f.Pads():
  x,y=xy(q.GetPosition())
  if 60<x<65 and 99<y<104:print('pad',f.GetReference(),q.GetNumber(),q.GetNetname(),xy(q.GetPosition()),xy(q.GetSize()))
for t in b.GetTracks():
 a=xy(t.GetStart());c=xy(t.GetEnd())
 if min(a[0],c[0])<64 and max(a[0],c[0])>60 and min(a[1],c[1])<103 and max(a[1],c[1])>100:
  print(type(t).__name__,t.GetNetname(),a,c,t.GetLayerName(),p.ToMM(t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth()))
