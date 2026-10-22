"""Local grid router used to author copper. Not a DRC or verification tool.
The final KiCad and manufacturing checks are intentionally deferred.
"""
from pathlib import Path
import math, heapq, time, json, sys
import numpy as np
import pcbnew as p
ROOT=Path(__file__).resolve().parent
STEP=.10
def xy(v):return (p.ToMM(v.x),p.ToMM(v.y))
def v(x,y):return p.VECTOR2I(p.FromMM(float(x)),p.FromMM(float(y)))

def route(name):
    path=ROOT/name/(name+'.kicad_pcb'); b=p.LoadBoard(str(ROOT/name/'authoring'/'placed.kicad_pcb'))
    w,h=(160,124) if name=='Array8x8' else (38,65)
    nx=int(w/STEP)+1;ny=int(h/STEP)+1;plane=nx*ny
    raw=np.zeros((2,ny,nx),dtype=np.int32)
    padlist={};edge=4
    raw[:,:edge,:]=-1;raw[:,-edge:,:]=-1;raw[:,:,:edge]=-1;raw[:,:,-edge:]=-1
    def rect(z,x0,y0,x1,y1,n):
        ax=max(0,int(math.ceil(x0/STEP)));bx=min(nx-1,int(math.floor(x1/STEP)))
        ay=max(0,int(math.ceil(y0/STEP)));by=min(ny-1,int(math.floor(y1/STEP)))
        # Retain foreign copper collisions as obstacles, never overwrite them.
        sl=raw[z,ay:by+1,ax:bx+1];sl[:]=np.where((sl!=0)&(sl!=n),-1,n)
    for f in b.GetFootprints():
        for pad in f.Pads():
            pos=xy(pad.GetPosition());box=pad.GetBoundingBox();a=xy(box.GetOrigin());zsize=xy(box.GetSize());n=pad.GetNetCode() or -1
            if pad.GetAttribute()==p.PAD_ATTRIB_NPTH:
                dia=xy(pad.GetDrillSize());a=(pos[0]-dia[0]/2-.25,pos[1]-dia[1]/2-.25);zsize=(dia[0]+.5,dia[1]+.5)
            layers=[z for z,layer in enumerate([p.F_Cu,p.B_Cu]) if pad.IsOnLayer(layer)]
            for z in layers:rect(z,*a,a[0]+zsize[0],a[1]+zsize[1],n)
            if n>0:
                gx=round(pos[0]/STEP);gy=round(pos[1]/STEP)
                padlist.setdefault(n,[]).append((gx,gy,layers,pos,pad))
    def dilate(arr,r):
        out=arr.copy()
        for dy in range(-r,r+1):
            for dx in range(-r,r+1):
                if dx*dx+dy*dy>r*r:continue
                sy=slice(max(0,-dy),min(ny,ny-dy));sx=slice(max(0,-dx),min(nx,nx-dx))
                ty=slice(max(0,dy),min(ny,ny+dy));tx=slice(max(0,dx),min(nx,nx+dx))
                out[:,ty,tx]|=arr[:,sy,sx]
        return out
    def track(a,c,z,n,width):
        if a==c:return
        t=p.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*c));t.SetLayer([p.F_Cu,p.B_Cu][z]);t.SetWidth(p.FromMM(width));t.SetNetCode(n);b.Add(t)
    def draw_path(nodes,n,width):
        decoded=[(s%nx,(s%plane)//nx,s//plane) for s in nodes]
        # Rasterize actual copper conservatively. Keep compact track segments.
        rad=width/2
        for x,y,z in decoded:rect(z,x*STEP-rad,y*STEP-rad,x*STEP+rad,y*STEP+rad,n)
        anchor=decoded[0];prev=anchor;direction=None
        for cur in decoded[1:]:
            dx=cur[0]-prev[0];dy=cur[1]-prev[1];dz=cur[2]-prev[2]
            if dz:
                track((anchor[0]*STEP,anchor[1]*STEP),(prev[0]*STEP,prev[1]*STEP),prev[2],n,width)
                via=p.PCB_VIA(b);via.SetPosition(v(cur[0]*STEP,cur[1]*STEP));via.SetWidth(p.FromMM(.7));via.SetDrill(p.FromMM(.3));via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNetCode(n);b.Add(via)
                for z in [0,1]:rect(z,cur[0]*STEP-.35,cur[1]*STEP-.35,cur[0]*STEP+.35,cur[1]*STEP+.35,n)
                anchor=cur;direction=None
            elif direction is not None and (dx,dy)!=direction:
                track((anchor[0]*STEP,anchor[1]*STEP),(prev[0]*STEP,prev[1]*STEP),prev[2],n,width);anchor=prev
            if not dz:direction=(dx,dy)
            prev=cur
        track((anchor[0]*STEP,anchor[1]*STEP),(prev[0]*STEP,prev[1]*STEP),prev[2],n,width)
        return decoded
    def find(start,end,bad,vbad,margin):
        ax,ay,azs,_,_=start;gx,gy,gzs,_,_=end
        xmin=max(edge,min(ax,gx)-margin);xmax=min(nx-edge-1,max(ax,gx)+margin)
        ymin=max(edge,min(ay,gy)-margin);ymax=min(ny-edge-1,max(ay,gy)+margin)
        goals={gx+gy*nx+z*plane for z in gzs};flat=bad.ravel();vf=vbad.ravel()
        heap=[];dist={};prev={}
        for z in azs:
            s=ax+ay*nx+z*plane
            if flat[s]:continue
            dist[s]=0;heapq.heappush(heap,(abs(ax-gx)+abs(ay-gy),0,s))
        pops=0
        while heap:
            _,cost,s=heapq.heappop(heap)
            if cost!=dist.get(s):continue
            if s in goals:
                nodes=[s]
                while s in prev:s=prev[s];nodes.append(s)
                return nodes[::-1]
            pops+=1
            if pops>600000:return None
            x=s%nx;y=(s%plane)//nx;z=s//plane
            moves=[]
            if x>xmin:moves.append((s-1,x-1,y,1))
            if x<xmax:moves.append((s+1,x+1,y,1))
            if y>ymin:moves.append((s-nx,x,y-1,1))
            if y<ymax:moves.append((s+nx,x,y+1,1))
            other=s+plane if z==0 else s-plane
            if not vf[s] and not vf[other]:moves.append((other,x,y,18))
            for ns,xx,yy,inc in moves:
                if flat[ns]:continue
                nc=cost+inc
                if nc<dist.get(ns,10**12):
                    dist[ns]=nc;prev[ns]=s;heur=abs(xx-gx)+abs(yy-gy)
                    heapq.heappush(heap,(nc+heur,nc,ns))
        return None
    def mst(pads):
        done=[0];todo=set(range(1,len(pads)));pairs=[]
        while todo:
            _,a,c=min((abs(pads[a][0]-pads[c][0])+abs(pads[a][1]-pads[c][1]),a,c) for a in done for c in todo)
            pairs.append((pads[a],pads[c]));done.append(c);todo.remove(c)
        return pairs
    netnames={n:b.FindNet(n).GetNetname() for n in padlist}
    ordering=[]
    for n,pads in padlist.items():
        if netnames[n]=='GND':continue
        pairs=mst(pads);length=sum(abs(a[0]-c[0])+abs(a[1]-c[1]) for a,c in pairs)
        nm=netnames[n]
        priority=0 if nm in ['VIN','VFUSED','+12V','+3V3'] else 2 if nm in ['SCLK','LATCH','OE_N','CLR_N'] else 1 if nm.startswith('DATA') else 3 if nm.startswith('Q') else 4
        ordering.append((priority,length if priority==0 else -length,n,pairs))
    unresolved=[];finished=0;starttime=time.time()
    for _,_,n,pairs in sorted(ordering):
        width=.8 if netnames[n] in ['VIN','VFUSED','+12V'] else .25
        for a,c in pairs:
            foreign=(raw!=0)&(raw!=n);bad=dilate(foreign,math.ceil((width/2+.20)/STEP));vbad=dilate(foreign,math.ceil((.35+.2)/STEP))
            nodes=None
            for margin in [50,150,max(nx,ny)]:
                nodes=find(a,c,bad,vbad,margin)
                if nodes:break
            if nodes:
                seq=draw_path(nodes,n,width)
                track(a[3],(a[0]*STEP,a[1]*STEP),seq[0][2],n,width)
                track(c[3],(c[0]*STEP,c[1]*STEP),seq[-1][2],n,width)
                finished+=1
            else:unresolved.append({'net':netnames[n],'from':a[4].GetParentFootprint().GetReference()+'.'+a[4].GetNumber(),'to':c[4].GetParentFootprint().GetReference()+'.'+c[4].GetNumber()})
        print(name,netnames[n],finished,'paths;',len(unresolved),'pending;',round(time.time()-starttime,1),'sec',flush=True)
    # Stitch the two ground pours in unobstructed locations.
    gnd=b.FindNet('GND').GetNetCode()
    foreign=(raw!=0)&(raw!=gnd);blocked=dilate(foreign,math.ceil((.35+.25)/STEP))
    for xx in np.arange(5,w-3,10):
        for yy in np.arange(5,h-3,10):
            ix=round(xx/STEP);iy=round(yy/STEP)
            if blocked[0,iy,ix] or blocked[1,iy,ix]:continue
            via=p.PCB_VIA(b);via.SetPosition(v(xx,yy));via.SetWidth(p.FromMM(.7));via.SetDrill(p.FromMM(.3));via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNetCode(gnd);b.Add(via)
    # Ground planes are part of copper authoring; not a completed-net assertion.
    for layer in [p.F_Cu,p.B_Cu]:
        zone=p.ZONE(b);zone.SetLayer(layer);zone.SetNetCode(b.FindNet('GND').GetNetCode());zone.SetLocalClearance(p.FromMM(.25));zone.SetThermalReliefGap(p.FromMM(.25));zone.SetThermalReliefSpokeWidth(p.FromMM(.3));zone.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
        outline=zone.Outline();outline.NewOutline()
        for x,y in [(.8,.8),(w-.8,.8),(w-.8,h-.8),(.8,h-.8)]:outline.Append(p.FromMM(x),p.FromMM(y))
        b.Add(zone)
    p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
    (ROOT/name/'routing_status.json').write_text(json.dumps({'authoring_paths':finished,'unrouted_pairs':unresolved,'final_checks':'NOT EXECUTED'},indent=2))
    print('SAVED',name,'unrouted',len(unresolved),flush=True)

if __name__=='__main__':
    route(sys.argv[1] if len(sys.argv)>1 else 'Array8x8')

