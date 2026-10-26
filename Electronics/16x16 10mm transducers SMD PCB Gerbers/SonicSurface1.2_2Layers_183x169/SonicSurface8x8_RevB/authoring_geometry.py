import pcbnew as p,math
b=p.LoadBoard('SonicSurface8x8_RevB/Array8x8_RevB/authoring/work.kicad_pcb');pad=next(q for f in b.GetFootprints() if f.GetReference()=='U7' for q in f.Pads() if q.GetNumber()=='10')
print('pad',p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y),p.ToMM(pad.GetSize().x),p.ToMM(pad.GetSize().y))
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA) and t.GetNetname()=='Q45':
  d=math.hypot(p.ToMM(t.GetPosition().x-pad.GetPosition().x),p.ToMM(t.GetPosition().y-pad.GetPosition().y))
  if d<5:print('via',p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y),'diam',p.ToMM(t.GetWidth(p.F_Cu)),'distance',d,'collision',t.GetEffectiveShape(p.F_Cu).Collide(pad.GetEffectiveShape(p.F_Cu),p.FromMM(.15)))
