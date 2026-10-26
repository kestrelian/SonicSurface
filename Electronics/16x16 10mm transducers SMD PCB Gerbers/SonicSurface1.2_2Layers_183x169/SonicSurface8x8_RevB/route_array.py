"""Rev B array: prepare the Freerouting input for the interface strip, or import its session.

  python route_array.py prepare   relayout.kicad_pcb -> ground escapes -> authoring/interface.dsn
  python route_array.py import    interface.ses + ground pours -> Array8x8_RevB.kicad_pcb

The structured array copper from relayout_array.py is locked and exported as protected wiring.
GND is left out of the router input and completed by escapes, stitching vias and pours.
Authoring only; final DRC and review remain separate.
"""
from pathlib import Path
import math, re, sys, json
import pcbnew as p

ROOT = Path(__file__).resolve().parent
A = ROOT / 'Array8x8_RevB'
AUTH = A / 'authoring'
mm = p.FromMM
def V(x, y): return p.VECTOR2I(mm(x), mm(y))

def ground_escapes(board):
    """Give each surface-mount GND pad a short track and via in free space."""
    gnd = board.FindNet('GND')
    objs = [q for f in board.GetFootprints() for q in f.Pads()] + list(board.GetTracks())
    holes = [f for f in board.GetFootprints() if f.GetReference().startswith('H')]
    def free(shape, layers, clear):
        for o in objs:
            if o.GetNetCode() == gnd.GetNetCode():
                continue
            for layer in layers:
                if o.IsOnLayer(layer) and o.GetEffectiveShape(layer).Collide(shape, mm(clear)):
                    return False
        return True
    added = 0
    for f in board.GetFootprints():
        ref = f.GetReference()
        for q in f.Pads():
            if q.GetNetCode() != gnd.GetNetCode() or q.GetAttribute() != p.PAD_ATTRIB_SMD:
                continue
            pos = q.GetPosition(); x0, y0 = p.ToMM(pos.x), p.ToMM(pos.y)
            # Already escaped by the structured array copper?
            if any(t.GetNetCode() == gnd.GetNetCode() and (t.GetStart() == pos or t.GetEnd() == pos)
                   for t in board.GetTracks() if isinstance(t, p.PCB_TRACK) and not isinstance(t, p.PCB_VIA)):
                continue
            c = f.GetPosition(); cx, cy = p.ToMM(c.x), p.ToMM(c.y)
            out = math.atan2(y0 - cy, x0 - cx) if (x0, y0) != (cx, cy) else 0.0
            cands = []
            if len([1 for _ in f.Pads()]) > 5:                     # ICs: under the body first
                cands.append((cx, cy))
            for rad in (1.1, 1.4, 1.8, 2.3):
                for da in (0, 0.5, -0.5, 1.0, -1.0, 1.57, -1.57, 2.4, -2.4, 3.14):
                    cands.append((x0 + rad * math.cos(out + da), y0 + rad * math.sin(out + da)))
            for vx, vy in cands:
                vs = p.SHAPE_CIRCLE(V(vx, vy), mm(0.3))
                if not free(vs, [p.F_Cu, p.B_Cu], 0.2):
                    continue
                if any(math.hypot(vx - p.ToMM(h.GetPosition().x), vy - p.ToMM(h.GetPosition().y)) < 2.3 for h in holes):
                    continue
                if any(isinstance(t, p.PCB_VIA) and math.hypot(vx - p.ToMM(t.GetPosition().x), vy - p.ToMM(t.GetPosition().y)) < 0.9
                       for t in board.GetTracks()):
                    continue
                seg = p.SHAPE_SEGMENT(pos, V(vx, vy), mm(0.25))
                if not free(seg, [p.B_Cu], 0.2):
                    continue
                t = p.PCB_TRACK(board); t.SetStart(pos); t.SetEnd(V(vx, vy)); t.SetWidth(mm(0.25))
                t.SetLayer(p.B_Cu); t.SetNet(gnd); t.SetLocked(True); board.Add(t)
                v = p.PCB_VIA(board); v.SetPosition(V(vx, vy)); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
                v.SetViaType(p.VIATYPE_THROUGH); v.SetLayerPair(p.F_Cu, p.B_Cu); v.SetNet(gnd); v.SetLocked(True)
                board.Add(v); objs.extend([t, v]); added += 1
                break
            else:
                print('No ground escape found for', ref, q.GetNumber())
    print('Ground escapes added:', added)

def block(s, start):
    d = 0
    for i in range(start, len(s)):
        if s[i] == '(':
            d += 1
        elif s[i] == ')':
            d -= 1
            if not d:
                return s[start:i + 1]

def prepare():
    board = p.LoadBoard(str(AUTH / 'relayout.kicad_pcb'))
    ground_escapes(board)
    p.SaveBoard(str(AUTH / 'pre_route.kicad_pcb'), board)
    dsn = AUTH / 'interface.dsn'
    assert p.ExportSpecctraDSN(board, str(dsn))
    s = dsn.read_text()
    # Ground is completed by pours. Keep one GND pin so the fixed GND wiring stays an obstacle,
    # but give the router nothing to connect.
    m = re.search(r'\(net GND\s', s); v = block(s, m.start())
    first = re.search(r'\(pins\s+(\S+)', v).group(1)
    s = s[:m.start()] + f'(net GND (pins {first}))' + s[m.start() + len(v):]
    start = s.index('(class kicad_default'); old = block(s, start)
    nets = old[len('(class kicad_default'):old.index('(circuit')].split()
    for m in re.finditer(r'\(class (?!kicad_default)', s):
        nets += block(s, m.start())[len('(class '):].split('(circuit')[0].split()[1:]
    for m in list(re.finditer(r'\(class ', s))[::-1]:
        v = block(s, m.start()); s = s[:m.start()] + s[m.start() + len(v):]
    nets = list(dict.fromkeys(nets))
    def cls(name, ns, w, clear):
        return (f'(class {name} ' + ' '.join(ns) + ' (circuit (use_via "Via[0-1]_600:300_um")) '
                f'(rule (width {w}) (clearance {clear})))')
    drv = [n for n in nets if n == 'VDRV']
    logic = [n for n in nets if n in ('"+3V3"', '+3V3')]
    classes = '\n'.join([cls('Signals', [n for n in nets if n not in drv + logic], 200, 160),
                         cls('Driver', drv, 600, 210), cls('Logic', logic, 300, 210)])
    idx = s.index('(network') + len('(network')
    s = s[:idx] + '\n' + classes + s[idx:]
    if '(padstack "Via[0-1]_600:300_um"' not in s:
        pos = s.index('(library') + len('(library')
        s = s[:pos] + '\n(padstack "Via[0-1]_600:300_um" (shape (circle F.Cu 600)) (shape (circle B.Cu 600)) (attach off))\n' + s[pos:]
    s = re.sub(r'\(via "[^)]*"\)', '(via "Via[0-1]_600:300_um")', s, count=1)
    s = re.sub(r'\(clearance \d+(\.\d+)?\)', '(clearance 160)', s)
    # The array above the interface strip is complete: keep the router out of it so nets join
    # the planned hand-off ends (bus ends, DATA risers, feeder) instead of the array pins.
    pos = s.index('(structure') + len('(structure')
    s = s[:pos] + ''.join(f'\n    (keepout "array" (rect {layer} 0 -87600 114000 0))' for layer in ('F.Cu', 'B.Cu')) + s[pos:]
    dsn.write_text(s)
    print('Router input written:', dsn, '| protected wires:', s.count('(type protect)'))

def zone(board, layer, pts, priority=0):
    z = p.ZONE(board); z.SetLayer(layer); z.SetNet(board.FindNet('GND'))
    z.SetLocalClearance(mm(0.2)); z.SetMinThickness(mm(0.2))
    z.SetThermalReliefGap(mm(0.25)); z.SetThermalReliefSpokeWidth(mm(0.3))
    z.SetPadConnection(p.ZONE_CONNECTION_THERMAL); z.SetAssignedPriority(priority)
    z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    poly = z.Outline(); poly.NewOutline()
    for x, y in pts:
        poly.Append(mm(x), mm(y))
    board.Add(z)

def stitch(board, pitch=3.5):
    """Tie the two ground pours together wherever a via fits."""
    gnd = board.FindNet('GND')
    objs = [q for f in board.GetFootprints() for q in f.Pads()] + list(board.GetTracks())
    holes = [(p.ToMM(f.GetPosition().x), p.ToMM(f.GetPosition().y)) for f in board.GetFootprints()
             if f.GetReference().startswith('H')]
    vias = [(p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)) for t in board.GetTracks() if isinstance(t, p.PCB_VIA)]
    # Keep drilled holes apart: treat every through-hole pad like a via for spacing.
    vias += [(p.ToMM(q.GetPosition().x), p.ToMM(q.GetPosition().y)) for f in board.GetFootprints() for q in f.Pads()
             if q.GetDrillSize().x > 0]
    added = 0
    y = 2.0
    while y < 118.5:
        x = 2.0
        while x < 112.5:
            vs = p.SHAPE_CIRCLE(V(x, y), mm(0.3))
            ok = all(math.hypot(x - hx, y - hy) > 2.6 for hx, hy in holes) and \
                 all(math.hypot(x - vx, y - vy) > 1.6 for vx, vy in vias)
            if ok:
                for o in objs:
                    if o.GetNetCode() == gnd.GetNetCode():
                        continue
                    if any(o.IsOnLayer(l) and o.GetEffectiveShape(l).Collide(vs, mm(0.3)) for l in (p.F_Cu, p.B_Cu)):
                        ok = False; break
            if ok:
                v = p.PCB_VIA(board); v.SetPosition(V(x, y)); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
                v.SetViaType(p.VIATYPE_THROUGH); v.SetLayerPair(p.F_Cu, p.B_Cu); v.SetNet(gnd)
                board.Add(v); vias.append((x, y)); added += 1
            x += pitch
        y += pitch
    print('Stitching vias added:', added)

def write_rules():
    """SaveBoard rewrites the project file; restore the Rev B array design rules."""
    f = A / 'Array8x8_RevB.kicad_pro'; d = json.loads(f.read_text())
    ns = d['net_settings']; base = dict(ns['classes'][0])
    base.update(name='Default', clearance=0.15, track_width=0.2, via_diameter=0.6, via_drill=0.3)
    power = dict(base); power.update(name='Power', clearance=0.2, track_width=0.5, priority=0)
    ns['classes'] = [base, power]
    ns['netclass_patterns'] = [{'netclass': 'Power', 'pattern': n} for n in ('VDRV', '+3V3')]
    r = d.setdefault('board', {}).setdefault('design_settings', {}).setdefault('rules', {})
    r.update(min_clearance=0.15, min_track_width=0.15, min_via_diameter=0.6, min_through_hole_diameter=0.3,
             min_via_annular_width=0.15)
    f.write_text(json.dumps(d, indent=2))

def finish(drc_json):
    """Solid-connect pads whose thermal relief was starved by nearby copper, then refill."""
    d = json.loads(Path(drc_json).read_text())
    spots = [(i['pos']['x'], i['pos']['y']) for v in d['violations'] if v['type'] == 'starved_thermal'
             for i in v['items'] if 'Pad' in i['description'] or 'PTH' in i['description']]
    board = p.LoadBoard(str(A / 'Array8x8_RevB.kicad_pcb')); n = 0
    for f in board.GetFootprints():
        for q in f.Pads():
            x, y = p.ToMM(q.GetPosition().x), p.ToMM(q.GetPosition().y)
            if any(abs(x - a) < 0.02 and abs(y - b) < 0.02 for a, b in spots):
                q.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL); n += 1
    p.ZONE_FILLER(board).Fill(board.Zones())
    p.SaveBoard(str(A / 'Array8x8_RevB.kicad_pcb'), board)
    write_rules()
    print('Solid zone connection set on', n, 'pads')

def import_session():
    board = p.LoadBoard(str(AUTH / 'pre_route.kicad_pcb'))
    if not p.ImportSpecctraSES(board, str(AUTH / 'interface.ses')):
        raise RuntimeError('Session import failed')
    board.GetDesignSettings().m_TrackMinWidth = mm(0.15)
    stitch(board)
    for layer in (p.F_Cu, p.B_Cu):
        zone(board, layer, [(0.5, 0.5), (113.5, 0.5), (113.5, 119.5), (0.5, 119.5)])
    p.ZONE_FILLER(board).Fill(board.Zones())
    p.SaveBoard(str(A / 'Array8x8_RevB.kicad_pcb'), board)
    write_rules()
    (A / 'routing_status.json').write_text(json.dumps({
        'layout': 'relayout_array.py structured array copper (locked) + Freerouting 2.5.0 interface strip',
        'session': 'authoring/interface.ses',
        'final_checks': 'NOT EXECUTED', 'release': 'UNVERIFIED - NOT FOR FABRICATION'}, indent=2))
    print('Imported, poured and saved Array8x8_RevB.kicad_pcb')

if __name__ == '__main__':
    if sys.argv[1] == 'finish':
        finish(sys.argv[2])
    else:
        {'prepare': prepare, 'import': import_session}[sys.argv[1]]()
