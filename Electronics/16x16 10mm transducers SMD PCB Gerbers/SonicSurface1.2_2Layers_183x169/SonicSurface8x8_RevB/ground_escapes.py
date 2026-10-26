from pathlib import Path
f=Path('SonicSurface8x8_RevB/import_routing.py');s=f.read_text();at=s.index('    p.ZONE_FILLER')
s=s[:at]+'''    if name.startswith('Array'):
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
''' + s[at:];f.write_text(s)
