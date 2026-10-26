from pathlib import Path
f=Path('SonicSurface8x8_RevB/import_routing.py');s=f.read_text()
s=s.replace("folder=root/name;board=p.LoadBoard(str(folder/'authoring/placed.kicad_pcb'))\n    if not p.ImportSpecctraSES(board,str(folder/'authoring/routed.ses')):raise RuntimeError('Session import failed')", "folder=root/name;work=folder/'authoring/work.kicad_pcb'\n    board=p.LoadBoard(str(work if work.exists() else folder/'authoring/placed.kicad_pcb'))\n    if not work.exists() and not p.ImportSpecctraSES(board,str(folder/'authoring/routed.ses')):raise RuntimeError('Session import failed')\n    board.GetDesignSettings().m_TrackMinWidth=p.FromMM(.15)\n    board.GetDesignSettings().m_MinThroughDrill=p.FromMM(.20)")
a=s.index('        # Via array directly');z=s.index('    p.ZONE_FILLER',a)
s=s[:a]+'''    # Place stitching/thermal vias only where authored pad and track geometry permits.
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
''' + s[z:]
s=s.replace("'authoring_status':'Session imported; see router.log and router_result.json'","'authoring_status':'Working copper imported; see authoring/finish_status.json and routing logs'")
f.write_text(s)
