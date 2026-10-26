"""Finish individual copper connections using obstacle-aware path authoring.
Not an ERC, DRC, schematic comparison or manufacturing release check.
"""
from pathlib import Path
import sys,math,heapq,json
import numpy as np
import pcbnew as p
root=Path(__file__).resolve().parent
name=sys.argv[1];folder=root/name
b=p.LoadBoard(str(folder/'authoring/work.kicad_pcb'))
S=.025;w,h=(114,120) if name.startswith('Array') else (120,140)
nx=int(w/S)+1;ny=int(h/S)+1;plane=nx*ny
raw=np.zeros((2,ny,nx),np.int32)
def xy(v):return p.ToMM(v.x),p.ToMM(v.y)
def vec(a):return p.VECTOR2I(p.FromMM(float(a[0])),p.FromMM(float(a[1])))
def uid(o):return o.m_Uuid.AsString()
def paint(z,x0,y0,x1,y1,n,mask=None):
 ax=max(0,int(math.ceil(x0/S)));bx=min(nx-1,int(math.floor(x1/S)));ay=max(0,int(math.ceil(y0/S)));by=min(ny-1,int(math.floor(y1/S)))
 if ax>bx or ay>by:return
 sub=raw[z,ay:by+1,ax:bx+1]
 if mask is None:sub[:]=np.where((sub!=0)&(sub!=n),-1,n)
 else:
  yy,xx=np.ogrid[ay:by+1,ax:bx+1];m=mask(xx*S,yy*S);sub[m]=np.where((sub[m]!=0)&(sub[m]!=n),-1,n)
def capsule(a,c,r,z,n):
 ax,ay=a;cx,cy=c;dx=cx-ax;dy=cy-ay;den=dx*dx+dy*dy
 def mask(x,y):
  t=np.clip(((x-ax)*dx+(y-ay)*dy)/den,0,1) if den else 0
  return (x-ax-t*dx)**2+(y-ay-t*dy)**2 <= (r+.018)**2
 paint(z,min(ax,cx)-r-.04,min(ay,cy)-r-.04,max(ax,cx)+r+.04,max(ay,cy)+r+.04,n,mask)
def stamp(o):
 n=o.GetNetCode() or -1
 if isinstance(o,p.PAD):
  a=xy(o.GetPosition());size=xy(o.GetSize())
  for z,layer in enumerate([p.F_Cu,p.B_Cu]):
   if not o.IsOnLayer(layer):continue
   if o.GetShape()==p.PAD_SHAPE_CIRCLE:capsule(a,a,size[0]/2,z,n)
   else:
    bb=o.GetBoundingBox();aa=xy(bb.GetOrigin());ss=xy(bb.GetSize());paint(z,aa[0],aa[1],aa[0]+ss[0],aa[1]+ss[1],n)
 elif isinstance(o,p.PCB_VIA):
  for z in [0,1]:capsule(xy(o.GetPosition()),xy(o.GetPosition()),p.ToMM(o.GetWidth(p.F_Cu))/2,z,n)
 else:capsule(xy(o.GetStart()),xy(o.GetEnd()),p.ToMM(o.GetWidth())/2,0 if o.GetLayer()==p.F_Cu else 1,n)
for f in b.GetFootprints():
 for pad in f.Pads():stamp(pad)
for t in b.GetTracks():stamp(t)
edge=10;raw[:,:edge,:]=-1;raw[:,-edge:,:]=-1;raw[:,:,:edge]=-1;raw[:,:,-edge:]=-1
def dilation(m,r):
 out=m.copy()
 for dy in range(-r,r+1):
  for dx in range(-r,r+1):
   if dx*dx+dy*dy>r*r:continue
   out[:,max(0,dy):min(ny,ny+dy),max(0,dx):min(nx,nx+dx)] |= m[:,max(0,-dy):min(ny,ny-dy),max(0,-dx):min(nx,nx-dx)]
 return out

def pending():
 b.BuildConnectivity();conn=b.GetConnectivity();nets={}
 for f in b.GetFootprints():
  for pad in f.Pads():
   if pad.GetNetCode():nets.setdefault(pad.GetNetCode(),[]).append(pad)
 pairs=[]
 for n,pads in nets.items():
  if len(pads)<2:continue
  groups={}
  for pad in pads:
   its=conn.GetConnectedItems(pad);ids=sorted(uid(o) for o in its if isinstance(o,p.PAD))
   key=ids[0] if ids else uid(pad);groups.setdefault(key,[]).append(pad)
  gs=list(groups.values())
  if len(gs)>1:
   dist,a,c=min((math.dist(xy(a.GetPosition()),xy(c.GetPosition())),a,c) for g in gs[1:] for a in gs[0] for c in g)
   pairs.append((dist,n,a,c,len(gs)))
 return sorted(pairs,key=lambda v:(b.FindNet(v[1]).GetNetname()=='GND',v[0]))
def find(a,c,bad,vbad):
 ax,ay=[round(v/S) for v in xy(a.GetPosition())];gx,gy=[round(v/S) for v in xy(c.GetPosition())]
 starts=[ax+ay*nx+z*plane for z,l in enumerate([p.F_Cu,p.B_Cu]) if a.IsOnLayer(l)]
 goals={gx+gy*nx+z*plane for z,l in enumerate([p.F_Cu,p.B_Cu]) if c.IsOnLayer(l)}
 flat=bad.ravel();vf=vbad.ravel();heap=[];cost={};prev={}
 print("Endpoints",[(i,bool(flat[i])) for i in starts],[(i,bool(flat[i])) for i in goals],flush=True)
 for s in starts:
  if not flat[s]:cost[s]=0;heapq.heappush(heap,(abs(ax-gx)+abs(ay-gy),0,s))
 pops=0
 while heap:
  _,d,s=heapq.heappop(heap)
  if d!=cost.get(s):continue
  if s in goals:
   out=[s]
   while s in prev:s=prev[s];out.append(s)
   return out[::-1]
  pops+=1
  if pops>1000000:
   print("Search limit",flush=True);return None
  x=s%nx;y=(s%plane)//nx;z=s//plane
  moves=[]
  if x>edge:moves.append((s-1,x-1,y,1))
  if x<nx-edge-1:moves.append((s+1,x+1,y,1))
  if y>edge:moves.append((s-nx,x,y-1,1))
  if y<ny-edge-1:moves.append((s+nx,x,y+1,1))
  other=s+plane if z==0 else s-plane
  if not vf[s] and not vf[other]:moves.append((other,x,y,30))
  for ns,xx,yy,inc in moves:
   if flat[ns]:continue
   nd=d+inc
   if nd<cost.get(ns,1e20):cost[ns]=nd;prev[ns]=s;heapq.heappush(heap,(nd+1.4*(abs(xx-gx)+abs(yy-gy)),nd,ns))
def line(a,c,z,n,width):
 if a==c:return
 t=p.PCB_TRACK(b);t.SetStart(vec(a));t.SetEnd(vec(c));t.SetWidth(p.FromMM(width));t.SetLayer([p.F_Cu,p.B_Cu][z]);t.SetNetCode(n);b.Add(t);stamp(t)
def draw(nodes,a,c,n,width):
 pts=[(s%nx*S,(s%plane)//nx*S,s//plane) for s in nodes];anchor=prev=pts[0];direction=None
 line(xy(a.GetPosition()),pts[0][:2],pts[0][2],n,width)
 for cur in pts[1:]:
  dd=tuple(round(cur[i]-prev[i],6) for i in range(3))
  if dd[2]:
   line(anchor[:2],prev[:2],prev[2],n,width)
   v=p.PCB_VIA(b);v.SetPosition(vec(cur[:2]));v.SetWidth(p.FromMM(.50));v.SetDrill(p.FromMM(.20));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(n);b.Add(v);stamp(v);anchor=cur;direction=None
  elif direction is not None and dd!=direction:line(anchor[:2],prev[:2],prev[2],n,width);anchor=prev
  if not dd[2]:direction=dd
  prev=cur
 line(anchor[:2],prev[:2],prev[2],n,width);line(prev[:2],xy(c.GetPosition()),prev[2],n,width)
failed=set();done=[]
for attempt in range(100):
 pairs=pending();candidates=[v for v in pairs if (uid(v[2]),uid(v[3])) not in failed]
 if not candidates:break
 dist,n,a,c,ng=candidates[0];nm=b.FindNet(n).GetNetname();label=f'{a.GetParentFootprint().GetReference()}.{a.GetNumber()} -> {c.GetParentFootprint().GetReference()}.{c.GetNumber()}'
 print('Authoring',nm,label,'clusters',ng,flush=True)
 width=.15 if name.startswith("Array") else .2
 foreign=(raw!=0)&(raw!=n);bad=dilation(foreign,math.ceil((width/2+.15)/S));vb=dilation(foreign,math.ceil((.250+.15)/S))
 a,c=c,a
 nodes=find(a,c,bad,vb)
 if nodes:draw(nodes,a,c,n,width);done.append([nm,label]);p.SaveBoard(str(folder/'authoring/work.kicad_pcb'),b);print('Saved connection',flush=True)
 else:failed.add((uid(c),uid(a)));print('No path in current geometry',flush=True)
left=[{'net':b.FindNet(n).GetNetname(),'clusters':ng} for _,n,a,c,ng in pending()]
(folder/'authoring/finish_status.json').write_text(json.dumps({'authored_connections':done,'remaining_clusters':left,'final_checks':'NOT EXECUTED'},indent=2))
print('Remaining authoring clusters',left,flush=True)

