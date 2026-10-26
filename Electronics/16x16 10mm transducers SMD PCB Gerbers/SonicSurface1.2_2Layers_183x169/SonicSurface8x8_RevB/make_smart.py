from pathlib import Path
f=Path('SonicSurface8x8_RevB/finish_copper.py');s=f.read_text()
s=s.replace('failed=set();done=[]', '''class Anchor:
 def __init__(self,pos,layers):self.pos=pos;self.layers=layers
 def GetPosition(self):return vec(self.pos)
 def IsOnLayer(self,l):return l in self.layers

def anchors(pad):
 items=b.GetConnectivity().GetConnectedItems(pad);out={}
 for o in items:
  layers=tuple(l for l in [p.F_Cu,p.B_Cu] if o.IsOnLayer(l))
  points=[xy(o.GetPosition())] if isinstance(o,(p.PAD,p.PCB_VIA)) else [xy(o.GetStart()),xy(o.GetEnd())]
  for pos in points:out[(pos,layers)]=Anchor(pos,layers)
 return list(out.values())
failed=set();done=[]''')
s=s.replace('a,c=c,a\n nodes=find(a,c,bad,vb)', '''key=(uid(a),uid(c))
 choices=sorted([(math.dist(x.pos,y.pos),x,y) for x in anchors(a) for y in anchors(c)],key=lambda v:v[0])
 nodes=None
 for _,aa,cc in choices[:24]:
  def usable(v):
   xx,yy=[round(q/S) for q in v.pos]
   return any(not bad[z,yy,xx] for z,l in enumerate([p.F_Cu,p.B_Cu]) if v.IsOnLayer(l))
  if not usable(aa) or not usable(cc):continue
  nodes=find(aa,cc,bad,vb)
  if nodes:a,c=aa,cc;break''').replace('failed.add((uid(c),uid(a)))','failed.add(key)').replace('pops>1000000','pops>250000')
(root:=f.parent).joinpath('finish_copper_smart.py').write_text(s)
