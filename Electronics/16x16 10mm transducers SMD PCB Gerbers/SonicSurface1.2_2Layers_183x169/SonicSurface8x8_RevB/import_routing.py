"""Import authored routes and construct copper zones; no final rule checks."""
from pathlib import Path
import json,sys
import pcbnew as p
root=Path(__file__).resolve().parent
def zone(board,net,layer,points,priority=0):
    z=p.ZONE(board);z.SetLayer(layer);z.SetNetCode(board.FindNet(net).GetNetCode())
    z.SetLocalClearance(p.FromMM(.20));z.SetThermalReliefGap(p.FromMM(.20));z.SetThermalReliefSpokeWidth(p.FromMM(.35))
    z.SetPadConnection(p.ZONE_CONNECTION_THERMAL);z.SetAssignedPriority(priority)
    poly=z.Outline();poly.NewOutline()
    for x,y in points:poly.Append(p.FromMM(x),p.FromMM(y))
    board.Add(z)
for name in (sys.argv[1:] or ['Array8x8_RevB','DualArray_Controller_RevB']):
    folder=root/name;work=folder/'authoring/work.kicad_pcb'
    board=p.LoadBoard(str(work if work.exists() else folder/'authoring/placed.kicad_pcb'))
    if not work.exists() and not p.ImportSpecctraSES(board,str(folder/'authoring/routed.ses')):raise RuntimeError('Session import failed')
    board.GetDesignSettings().m_TrackMinWidth=p.FromMM(.15)
    board.GetDesignSettings().m_MinThroughDrill=p.FromMM(.20)
    w,h=(114,120) if name.startswith('Array') else (120,140)
    for layer in [p.F_Cu,p.B_Cu]:zone(board,'GND',layer,[(.8,.8),(w-.8,.8),(w-.8,h-.8),(.8,h-.8)])
    if name.startswith('Dual'):
        # Preserve the eFuse's isolated RTN island; do not short RTN to GND.
        zone(board,'IN_RTN',p.B_Cu,[(25,94),(35,94),(35,106),(25,106)],1)
    # Place stitching/thermal vias only where authored pad and track geometry permits.
    gnd=board.FindNet('GND').GetNetCode()
    items=[pad for fp in board.GetFootprints() for pad in fp.Pads()]+list(board.GetTracks())
    foreign=[o for o in items if o.GetNetCode()!=gnd]
    def add_ground_via(x,y):
        shape=p.SHAPE_CIRCLE(p.VECTOR2I(p.FromMM(x),p.FromMM(y)),p.FromMM(.275))
        for o in foreign:
            for layer in [p.F_Cu,p.B_Cu]:
                if o.IsOnLayer(layer) and o.GetEffectiveShape(layer).Collide(shape,p.FromMM(.20)):return False
        v=p.PCB_VIA(board);v.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));v.SetWidth(p.FromMM(.55));v.SetDrill(p.FromMM(.25));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(gnd);board.Add(v)
        return True
    thermal=0
    if name.startswith('Dual'):
        for x in [58.2,59,59.8]:
            for y in [101.8,102.6,103.4,104.2]:thermal+=int(add_ground_via(x,y))
        print('Authored regulator thermal vias:',thermal)
    for x in range(6,w-4,10):
        for y in range(6,h-4,10):
            if name.startswith('Dual') and 24<x<36 and 93<y<107:continue
            add_ground_via(x,y)
    if name.startswith('Array'):
        connected=0
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if pad.GetNetCode()!=gnd or pad.GetAttribute()!=p.PAD_ATTRIB_SMD:continue
                layer=p.B_Cu if pad.IsOnLayer(p.B_Cu) else p.F_Cu
                pos=pad.GetPosition();x=p.ToMM(pos.x);y=p.ToMM(pos.y)
                found=False
                for radius in [.9,1.2,1.6]:
                    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(.707,.707),(-.707,.707),(.707,-.707),(-.707,-.707)]:
                        target=p.VECTOR2I(p.FromMM(x+radius*dx),p.FromMM(y+radius*dy))
                        shape=p.SHAPE_SEGMENT(pos,target,p.FromMM(.25))
                        if any(o.IsOnLayer(layer) and o.GetEffectiveShape(layer).Collide(shape,p.FromMM(.20)) for o in foreign):continue
                        if not add_ground_via(x+radius*dx,y+radius*dy):continue
                        t=p.PCB_TRACK(board);t.SetStart(pos);t.SetEnd(target);t.SetWidth(p.FromMM(.25));t.SetLayer(layer);t.SetNetCode(gnd);board.Add(t)
                        connected+=1;found=True;break
                    if found:break
        print('Authored local SMD ground escapes:',connected)
    p.ZONE_FILLER(board).Fill(board.Zones())
    p.SaveBoard(str(folder/(name+'.kicad_pcb')),board)
    (folder/'routing_status.json').write_text(json.dumps({'engine':'Freerouting 2.5.0 Java','session':'authoring/routed.ses','authoring_status':'Working copper imported; see authoring/finish_status.json and routing logs','final_checks':'NOT EXECUTED','release':'UNVERIFIED - NOT FOR FABRICATION'},indent=2))
    print('Imported and filled',name)
