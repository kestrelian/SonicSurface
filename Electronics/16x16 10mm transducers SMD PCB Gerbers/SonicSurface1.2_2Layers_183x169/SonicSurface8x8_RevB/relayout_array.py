"""Rev B array re-layout: deterministic placement and structured copper for the 8x8 array.

Loads authoring/placed.kicad_pcb (nets from build_revb.py), moves every array part to the
row-channel layout, authors the regular array copper as locked tracks, and writes
authoring/relayout.kicad_pcb. The interface strip is left for Freerouting (see route_array.py).
Authoring only; no ERC/DRC/manufacturing check is implied.

Layout summary (board mm, y down, transducer rows y_r = 14 + 10.3 r):
- Each TC4427 sits on the back between transducer rows, centred at (13.15 + 20.6 p, y_r - 5.15),
  rotated so inputs face the row above and outputs face its own row. Package bodies therefore clear
  every transducer lead, including a maximum-length 10.16 mm PDIP body.
- Every DIP row has an 8-track front-copper channel through the package interiors. HC595 Q outputs
  run left in that channel and rise directly into the TC4427 input pins: no vias, no crossings.
- Back copper carries per-row 16.8 V trunks, local decoupling, pulldowns, damping resistors and the
  HC595 control buses. Front copper is otherwise a ground pour.
"""
from pathlib import Path
import pcbnew as p

ROOT = Path(__file__).resolve().parent
FOLDER = ROOT / 'Array8x8_RevB'
SRC = FOLDER / 'authoring/placed.kicad_pcb'
OUT = FOLDER / 'authoring/relayout.kicad_pcb'

PITCH = 10.3
def row_y(r): return 14.0 + PITCH * r          # transducer row centre
def dip_y(r): return row_y(r) - 5.15             # TC4427 / HC595 row centre
def pair_x(k): return 13.15 + 20.6 * k           # TC4427 centre
HC_X0 = 91.0                                     # HC595 pin 1 x
LANE0, LANE_PITCH = -1.33, 0.38                  # front-copper channel, relative to dip_y
# HC595 output for each column. The channel geometry fixes this order (QA..QH -> 0,7,6,5,4,3,2,1).
COL_PIN = {0: '15', 7: '1', 6: '2', 5: '3', 4: '4', 3: '5', 2: '6', 1: '7'}
DATA_X = lambda r: 110.3 + 0.4 * (7 - r)        # front-copper DATA riser at the right edge
HANDOFF_Y = 91.0                                 # array copper ends here; interface is autorouted

W_SIG, W_BUS, W_3V3, W_TRUNK, W_FEED = 0.2, 0.25, 0.3, 0.5, 0.8
VIA_D, VIA_DRILL = 0.6, 0.3

board = p.LoadBoard(str(SRC))
FP = {f.GetReference(): f for f in board.GetFootprints()}
mm = p.FromMM
def V(x, y): return p.VECTOR2I(mm(x), mm(y))

def pad(ref, num):
    return next(q for q in FP[ref].Pads() if q.GetNumber() == num)

def xy(ref, num):
    q = pad(ref, num).GetPosition()
    return (p.ToMM(q.x), p.ToMM(q.y))

def place(ref, x, y, deg):
    """Place so the mean of the numbered pad centres lands on (x, y)."""
    f = FP[ref]
    f.SetOrientationDegrees(deg)
    pads = [q for q in f.Pads() if q.GetNumber()]
    cx = sum(q.GetPosition().x for q in pads) / len(pads)
    cy = sum(q.GetPosition().y for q in pads) / len(pads)
    pos = f.GetPosition()
    f.SetPosition(p.VECTOR2I(int(pos.x + mm(x) - cx), int(pos.y + mm(y) - cy)))

def set_pad_size(ref, d):
    for q in FP[ref].Pads():
        if q.GetNumber():
            q.SetShape(p.PADSTACK.ALL_LAYERS, p.PAD_SHAPE_CIRCLE)
            q.SetSize(p.PADSTACK.ALL_LAYERS, V(d, d))

def net(name):
    n = board.FindNet(name)
    if n is None:
        raise KeyError(name)
    return n

def track(netname, layer, pts, w):
    n = net(netname)
    for a, b in zip(pts, pts[1:]):
        t = p.PCB_TRACK(board)
        t.SetStart(V(*a)); t.SetEnd(V(*b)); t.SetWidth(mm(w))
        t.SetLayer(layer); t.SetNet(n); t.SetLocked(True)
        board.Add(t)

def via(netname, x, y):
    v = p.PCB_VIA(board)
    v.SetPosition(V(x, y)); v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL))
    v.SetViaType(p.VIATYPE_THROUGH); v.SetLayerPair(p.F_Cu, p.B_Cu)
    v.SetNet(net(netname)); v.SetLocked(True)
    board.Add(v)

F, B = p.F_Cu, p.B_Cu

# Remove anything previously authored on the placement board.
for t in list(board.GetTracks()):
    board.Remove(t)
for z in list(board.Zones()):
    board.Remove(z)

# ---------------------------------------------------------------- HC595 output remap
# Pad nets follow the schematic; update_schematic_q_map() in this script edits the row sheets.
for r in range(8):
    u = f'U{r + 1}'
    for col, num in COL_PIN.items():
        pad(u, num).SetNet(net(f'Q{8 * r + col:02d}'))

# ---------------------------------------------------------------- placement
for r in range(8):
    yr, yd = row_y(r), dip_y(r)
    for c in range(8):
        # Pin 1 (drive) on the outer side of each driver pair; pin 2 (case/GND) inner.
        ref = f'T{8 * r + c + 1}'
        place(ref, 8.0 + PITCH * c, yr, 0 if c % 2 == 0 else 180)
        set_pad_size(ref, 1.6)
    for k in range(4):
        n = 4 * r + k; ch = 8 * r + 2 * k; xc = pair_x(k)
        u = f'U{101 + n}'
        place(u, xc, yd, 270)
        set_pad_size(u, 1.5)
        place(f'R{101 + ch + 1}', xc + 6.5, yd - 3.6, 0)      # Q_B pulldown: Q | GND
        place(f'R{101 + ch}', xc - 6.5, yd - 3.6, 180)        # Q_A pulldown: GND | Q
        place(f'R{201 + ch + 1}', xc + 6.5, yd + 3.6, 0)      # 22R B: OUT | DRV
        place(f'R{201 + ch}', xc - 6.5, yd + 3.6, 180)        # 22R A: DRV | OUT
        place(f'C{101 + n}', xc + 6.7, yd - 2.2, 180)         # 100 nF: GND | VDRV
        place(f'C{201 + n}', xc + 9.9, yd - 2.2, 0)           # 1 uF: VDRV | GND
    place(f'U{r + 1}', HC_X0 + 8.89, yd, 270)
    place(f'C{10 + r}', 88.9, yd + 1.2, 270)                  # +3V3 top, GND bottom

# Interface strip (back side). Autorouted afterwards.
INTERFACE = {
    # J1 signal row faces the board so every cable signal escapes straight up.
    'J1': (84.76, 114.6, 270), 'C2': (67.0, 108.0, 90),
    'U50': (86.0, 101.5, 0), 'C500': (91.0, 104.0, 90),
    'U51': (101.0, 101.5, 0), 'C510': (106.0, 104.0, 90), 'R32': (106.6, 99.0, 0),
    'U55': (96.0, 96.0, 0), 'C55': (93.5, 96.0, 90), 'R33': (96.5, 90.0, 0),
    'U54': (96.0, 92.8, 0), 'C54': (93.5, 92.8, 90),
    'U52': (40.0, 94.5, 0), 'C520': (40.0, 97.4, 0), 'R520': (43.6, 94.5, 90),
    'U53': (22.0, 94.5, 0), 'C530': (22.0, 97.4, 0), 'R530': (25.6, 94.5, 90),
    'R34': (15.0, 92.6, 0), 'R35': (15.0, 95.2, 0),
    'C1': (8.75, 96.5, 0), 'J2': (7.5, 108.2, 0), 'R1': (16.0, 103.0, 90),
    'TP1': (25.0, 116.0, 0), 'TP2': (30.0, 116.0, 0), 'TP3': (16.0, 113.0, 0),
    'TP7': (35.0, 116.0, 0),
    'TP6': (HC_X0 + 8.89, 92.6, 0), 'TP5': (HC_X0 + 11.43, 94.4, 0), 'TP4': (HC_X0 + 13.97, 92.6, 0),
    'TP8': (3.6, 11.6, 0), 'TP9': (pair_x(3) + 7.65, row_y(7) + 2.7, 0),
}
for ref, (x, y, deg) in INTERFACE.items():
    place(ref, x, y, deg)
# Cable pulldowns sit beside their J1 pins, clear of the straight pin escapes.
RX = [f'DATA{i}_RX' for i in range(8)] + ['SCLK_RX', 'LATCH_RX', 'OE_N_RX', 'CLR_N_RX']
RX_REF = [f'R{20 + i}' for i in range(8)] + ['R28', 'R29', 'R31', 'R30']
for i, (sig, ref) in enumerate(zip(RX, RX_REF)):
    x = xy('J1', str(3 + 2 * i))[0] + 1.27
    place(ref, x, 107.6, 90)

for ref, xyz in {'H1': (3, 3), 'H2': (111, 3), 'H3': (3, 117), 'H4': (111, 117)}.items():
    FP[ref].SetPosition(V(*xyz))

# ---------------------------------------------------------------- array copper
def lane(col, yd): return yd + LANE0 + LANE_PITCH * (7 - col)

for r in range(8):
    yd = dip_y(r); yr = row_y(r)
    for k in range(4):
        n = 4 * r + k; ch = 8 * r + 2 * k; xc = pair_x(k)
        u = f'U{101 + n}'
        qa, qb = f'Q{ch:02d}', f'Q{ch + 1:02d}'
        oa, ob = f'OUT{ch:02d}', f'OUT{ch + 1:02d}'
        da, db = f'DRV{ch:02d}', f'DRV{ch + 1:02d}'
        p2, p3, p4 = xy(u, '2'), xy(u, '3'), xy(u, '4')
        p5, p6, p7 = xy(u, '5'), xy(u, '6'), xy(u, '7')
        # Q_B (pin 4) and Q_A (pin 2) leave on back copper to their pulldowns.
        track(qb, B, [p4, xy(f'R{101 + ch + 1}', '1')], W_SIG)
        rq = xy(f'R{101 + ch}', '1')
        track(qa, B, [p2, (xc - 2.4, yd - 2.68), (xc - 4.9, yd - 2.68), (rq[0], yd - 3.455), rq], W_SIG)
        for ref, side in [(f'R{101 + ch + 1}', 1), (f'R{101 + ch}', -1)]:
            g = xy(ref, '2'); track('GND', B, [g, (xc + side * 8.4, g[1])], W_SIG); via('GND', xc + side * 8.4, g[1])
        # Outputs through the 22R damping resistors to the outer transducer pins.
        track(ob, B, [p5, xy(f'R{201 + ch + 1}', '1')], W_SIG)
        track(db, B, [xy(f'R{201 + ch + 1}', '2'), xy(f'T{ch + 2}', '1')], W_SIG)
        ro = xy(f'R{201 + ch}', '1')
        track(oa, B, [p7, (xc - 2.4, yd + 2.68), (xc - 4.9, yd + 2.68), (ro[0], yd + 3.455), ro], W_SIG)
        track(da, B, [xy(f'R{201 + ch}', '2'), xy(f'T{ch + 1}', '1')], W_SIG)
        # Supply: pin 6 to the row trunk; 100 nF + 1 uF return directly to pin 3.
        c1v, c1g = xy(f'C{101 + n}', '1'), xy(f'C{101 + n}', '2')
        c2v, c2g = xy(f'C{201 + n}', '1'), xy(f'C{201 + n}', '2')
        track('VDRV', B, [p6, (p6[0], yd)], 0.4)
        track('VDRV', B, [c1v, (c1v[0], yd)], 0.4)
        track('VDRV', B, [c1v, c2v], 0.4)
        track('GND', B, [p3, (xc + 2.4, yd - 2.68), (xc + 4.9, yd - 2.68), c1g], 0.3)
        track('GND', B, [c2g, (c2g[0], yd - 3.45)], 0.3); via('GND', c2g[0], yd - 3.45)
        # Front channel: Q_B rises at pin 4, Q_A at pin 2 (both fed from the HC595 on the right).
        track(qb, F, [(p4[0], lane(2 * k + 1, yd)), p4], W_SIG)
        track(qa, F, [(p2[0], lane(2 * k, yd)), p2], W_SIG)
    # Row 16.8 V trunk under the DIP bodies, from the left feeder to pair 3's capacitors.
    track('VDRV', B, [(2.0, yd), (pair_x(3) + 7.48, yd)], W_TRUNK)

    # HC595 outputs into the channel.
    u = f'U{r + 1}'
    for col, num in COL_PIN.items():
        q = f'Q{8 * r + col:02d}'; px, py = xy(u, num)
        k = col // 2; tx = xy(f'U{101 + 4 * r + k}', '4' if col % 2 else '2')[0]
        ly = lane(col, yd)
        track(q, F, [(px, py), (px, ly), (tx, ly)], W_SIG)
    # HC595 decoupling to the +3V3 bus.
    cv, cg = xy(f'C{10 + r}', '1'), xy(f'C{10 + r}', '2')
    track('GND', B, [cg, (cg[0], yd + 3.0)], 0.3); via('GND', cg[0], yd + 3.0)
    track('+3V3', B, [cv, (HC_X0 - 1.27, cv[1])], W_3V3)
    # Control buses: vertical on back copper, jogging through the gaps of each top pin row.
    for netname, num, dx, w in [('+3V3', '16', -1.27, W_3V3), ('OE_LOCAL_N', '13', 1.27, W_BUS),
                                ('LATCH', '12', 1.27, W_BUS), ('SCLK', '11', 1.27, W_BUS),
                                ('CLR_N', '10', 1.27, W_BUS)]:
        px, py = xy(u, num); gx = px + dx
        top = (gx, cv[1]) if (r == 0 and netname == '+3V3') else None
        if r > 0:
            top = (gx, dip_y(r - 1) + 5.08)
        pts = ([top, (gx, py - 1.27)] if top else []) + [(px, py), (gx, py + 1.27)]
        if r == 7:
            pts.append((gx, HANDOFF_Y))
        track(netname, B, pts, w)
    # DATA riser on the right edge, then left between HC595 rows into SER (pin 14).
    sx, sy = xy(u, '14'); dx_ = DATA_X(r)
    track(f'DATA{r}', F, [(dx_, HANDOFF_Y), (dx_, yd + 5.15), (sx, yd + 5.15), (sx, sy)], W_SIG)

# Left 16.8 V feeder to C1 and J2.
track('VDRV', B, [(2.0, dip_y(0)), (2.0, xy('C1', '1')[1]), xy('C1', '1')], W_FEED)
track('VDRV', B, [(2.0, xy('C1', '1')[1]), (2.0, xy('J2', '1')[1] - 3.0), xy('J2', '1')], W_FEED)
# Representative output test pads beside their transducers.
track('DRV00', B, [xy('TP8', '1'), xy('R201', '2')], W_SIG)
track('DRV63', B, [xy('T64', '1'), xy('TP9', '1')], W_SIG)
# Bus test pads on the bus ends.
for tp, netname, num in [('TP6', 'OE_LOCAL_N', '13'), ('TP5', 'LATCH', '12'), ('TP4', 'SCLK', '11')]:
    gx = xy('U8', num)[0] + 1.27
    track(netname, B, [(gx, HANDOFF_Y), xy(tp, '1')], W_BUS)

# Silkscreen labels clear of the new connector positions.
for d in board.GetDrawings():
    if isinstance(d, p.PCB_TEXT):
        t = d.GetText()
        if t.startswith('8x8 REV B'): d.SetPosition(V(45, 119.0))
        elif t.startswith('J1 PIN1'): d.SetPosition(V(98.0, 108.3))
        elif t.startswith('J2 '): d.SetPosition(V(7.5, 104.0))

p.SaveBoard(str(OUT), board)
print('Relayout written:', OUT)


def update_schematic_q_map():
    """Rename the HC595 output labels on each row sheet to match COL_PIN."""
    import re
    order = ['15', '1', '2', '3', '4', '5', '6', '7']   # QA..QH symbol order on the sheet
    col_of = {num: col for col, num in COL_PIN.items()}
    for r in range(8):
        f = FOLDER / f'Row{r + 1:02d}_01.kicad_sch'
        s = f.read_text()
        labels = list(re.finditer(r'\(global_label "Q(\d\d)" \(shape passive\) \(at 77\.78 ([\d.]+) 180\)', s))
        assert len(labels) == 8, (f, len(labels))
        for m, num in zip(sorted(labels, key=lambda m: float(m.group(2))), order):
            new = f'{8 * r + col_of[num]:02d}'
            s = s[:m.start(1)] + new + s[m.end(1):]
        f.write_text(s)
    print('Row sheets updated with the HC595 column map.')

if __name__ == '__main__':
    import sys
    if '--schematic' in sys.argv:
        update_schematic_q_map()
