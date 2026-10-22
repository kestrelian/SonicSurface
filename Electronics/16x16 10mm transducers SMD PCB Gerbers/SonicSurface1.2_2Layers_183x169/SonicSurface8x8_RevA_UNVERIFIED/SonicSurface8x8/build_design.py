"""Generate the editable Rev A design. Does not execute ERC, DRC or final QA.
Run with the Python distributed with KiCad 10.
"""
from pathlib import Path
import uuid, json, csv, shutil, math
import pcbnew as p

ROOT=Path(__file__).resolve().parent
LIB=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')
uid=lambda: str(uuid.uuid4())
mm=p.FromMM
pt=lambda x,y:p.VECTOR2I(mm(x),mm(y))
q=lambda s: '"'+str(s).replace('\\','/').replace('"','\\"')+'"'
RFP='Resistor_SMD:R_0805_2012Metric'
CFP='Capacitor_SMD:C_0805_2012Metric'
DIP8='Package_DIP:DIP-8_W7.62mm'
DIP16='Package_DIP:DIP-16_W7.62mm'
IDC='Connector_IDC:IDC-Header_2x13_P2.54mm_Vertical'
SOCKET='Connector_PinSocket_2.54mm:PinSocket_2x22_P2.54mm_Vertical'
TERM='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2_1x02_P5.00mm_Horizontal'
CAPB='Capacitor_THT:CP_Radial_D8.0mm_P3.50mm'

# Pin names, electrical type and side. Physical pin numbers are explicit.
DEFS={
 'PWR_FLAG':[('1','SUPPLY','power_out','L')],
 'HC595': [('14','SER','input','L'),('11','SRCLK','input','L'),('12','RCLK','input','L'),('13','~{OE}','input','L'),('10','~{SRCLR}','input','L'),('16','VCC','power_in','L'),('8','GND','power_in','L')]+[(str(n),'Q'+str(i),'tri_state','R') for i,n in enumerate([15,1,2,3,4,5,6,7])]+[('9','Q7S','output','R')],
 'TC4427':[('2','INA','input','L'),('4','INB','input','L'),('6','VDD','power_in','L'),('3','GND','power_in','L'),('7','OUTA','output','R'),('5','OUTB','output','R'),('1','NC','no_connect','R'),('8','NC','no_connect','R')],
 'R':[('1','1','passive','L'),('2','2','passive','R')],
 'C':[('1','1','passive','L'),('2','2','passive','R')],
 'CP':[('1','+','passive','L'),('2','-','passive','R')],
 'FUSE':[('1','1','passive','L'),('2','2','passive','R')],
 'DIODE':[('1','K','passive','L'),('2','A','passive','R')],
 'MA40S4S':[('1','DRIVE','passive','L'),('2','RETURN','passive','R')],
 'POWER':[('1','VIN','passive','L'),('2','GND','passive','R')],
 'IDC26':[(str(n),'PIN_'+str(n),'passive','L' if n%2 else 'R') for n in range(1,27)],
 'CORE_P1':[(str(n),'P1_'+str(n),'passive','L' if n%2 else 'R') for n in range(1,45)],
}

def symbol(name):
    pins=DEFS[name]; counts={s:sum(v[3]==s for v in pins) for s in ['L','R']}
    h=max(2.54,(max(counts.values())-1)*2.54/2+2.54)
    width=7.62 if len(pins)>2 else 3.81
    out=f'(symbol {q(name)} (pin_names (offset 0.8)) (in_bom yes) (on_board yes)\n'
    out+=f'(property "Reference" "U" (at 0 {h+2.54} 0) (effects (font (size 1.27 1.27))))\n'
    out+=f'(property "Value" {q(name)} (at 0 {-h-2.54} 0) (effects (font (size 1.27 1.27))))\n'
    out+=f'(symbol {q(name+"_0_1")} (rectangle (start {-width} {h}) (end {width} {-h}) (stroke (width 0.254) (type default)) (fill (type background))))\n'
    out+=f'(symbol {q(name+"_1_1")}\n'; positions={}; indices={'L':0,'R':0}
    for num,nm,ty,side in pins:
        y=(counts[side]-1)*2.54/2-indices[side]*2.54; indices[side]+=1
        x=-(width+5.08) if side=='L' else width+5.08; angle=0 if side=='L' else 180
        positions[num]=(x,y,side)
        out+=f'(pin {ty} line (at {x} {y} {angle}) (length 5.08) (name {q(nm)} (effects (font (size 1 1)))) (number {q(num)} (effects (font (size 1 1)))))\n'
    return out+'))\n',positions,h

SYMS={k:symbol(k) for k in DEFS}

def with_power_flags(s,rootid,project):
    if '(lib_id "SS8:PWR_FLAG")' in s:return s
    if '(symbol "SS8:PWR_FLAG"' not in s:
        definition=SYMS['PWR_FLAG'][0].replace('(symbol "PWR_FLAG"','(symbol "SS8:PWR_FLAG"',1)
        s=s.replace('(lib_symbols\n','(lib_symbols\n'+definition,1)
    extra=''
    for i,net in enumerate(['+3V3','+12V','GND']):
        x=150+i*65;y=170;ref=f'#FLG0{i+1}';ident=uid();px=x-8.89
        extra+=f'(symbol (lib_id "SS8:PWR_FLAG") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid {ident}) (property "Reference" {q(ref)} (at {x} {y-5.08} 0) (effects (font (size 1 1)) (hide yes))) (property "Value" "External supply" (at {x} {y-2.54} 0) (effects (font (size 1 1)))) (pin "1" (uuid {uid()})) (instances (project {q(project)} (path {q("/"+rootid)} (reference {q(ref)}) (unit 1)))))\n'
        extra+=f'(global_label {q(net)} (shape passive) (at {px} {y} 0) (effects (font (size 1 1)) (justify left)) (uuid {uid()}))\n'
    return s.rstrip()[:-1]+extra+')\n'

class Design:
    def __init__(self,name,w,h):
        self.name=name; self.folder=ROOT/name; self.folder.mkdir(exist_ok=True)
        (self.folder/'SS8.pretty').mkdir(exist_ok=True)
        self.b=p.BOARD(); self.b.SetCopperLayerCount(2)
        self.w=w; self.h=h; self.comps=[]; self.nets={}; self.pages={}; self.rootid=uid()
        ds=self.b.GetDesignSettings(); ds.m_MinClearance=mm(.20); ds.m_TrackMinWidth=mm(.25); ds.m_ViasMinSize=mm(.65); ds.m_MinThroughDrill=mm(.3)
        for a,b in [((0,0),(w,0)),((w,0),(w,h)),((w,h),(0,h)),((0,h),(0,0))]:
            s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(pt(*a));s.SetEnd(pt(*b));s.SetLayer(p.Edge_Cuts);s.SetWidth(mm(.05));self.b.Add(s)
        self.n('GND'); self.page('main',self.rootid)
    def page(self,name,id=None):
        self.pages[name]={'id':id or uid(),'parts':[]}; return self.pages[name]
    def n(self,name):
        if name is None:return None
        if name not in self.nets:
            net=p.NETINFO_ITEM(self.b,name); self.b.Add(net);self.nets[name]=net
        return self.nets[name]
    def fp(self,id):
        lib,name=id.split(':'); local=self.folder/'SS8.pretty'/(name+'.kicad_mod')
        if lib!='SS8' and not local.exists():shutil.copyfile(LIB/(lib+'.pretty')/(name+'.kicad_mod'),local)
        f=p.FootprintLoad(str(self.folder/'SS8.pretty'),name)
        f.SetFPID(p.LIB_ID('SS8',name));return f
    def add(self,ref,value,sym,fp,nets,x,y,page='main',sx=50,sy=50,angle=0,bottom=False,center=True):
        f=self.fp(fp);f.SetReference(ref);f.SetValue(value);self.b.Add(f)
        # Place using the centre of pad extents for convenient symmetric placement.
        pads=list(f.Pads()); xs=[p.ToMM(v.GetPosition().x) for v in pads];ys=[p.ToMM(v.GetPosition().y) for v in pads]
        cx=(min(xs)+max(xs))/2 if center else 0;cy=(min(ys)+max(ys))/2 if center else 0
        if bottom:f.Flip(pt(0,0),False);cy=-cy
        f.SetOrientationDegrees(angle)
        theta=math.radians(angle); dx=cx*math.cos(theta)+cy*math.sin(theta);dy=-cx*math.sin(theta)+cy*math.cos(theta)
        f.SetPosition(pt(x-dx,y-dy));f.Reference().SetTextSize(pt(.8,.8));f.Reference().SetTextThickness(mm(.12));f.Value().SetVisible(False)
        for pad in f.Pads():
            net=nets.get(pad.GetNumber())
            if net:pad.SetNet(self.n(net))
        obj={'ref':ref,'value':value,'sym':sym,'fp':'SS8:'+fp.split(':')[1],'nets':nets,'uuid':uid(),'x':sx,'y':sy,'f':f,'page':page}
        path=p.KIID_PATH();path.push_back(p.KIID(self.rootid))
        if page!='main':path.push_back(p.KIID(self.pages[page]['id']))
        path.push_back(p.KIID(obj['uuid']));f.SetPath(path)
        self.comps.append(obj);self.pages[page]['parts'].append(obj);return f
    def text(self,text,x,y,layer=p.F_SilkS,size=1):
        t=p.PCB_TEXT(self.b);t.SetText(text);t.SetPosition(pt(x,y));t.SetTextSize(pt(size,size));t.SetTextThickness(mm(.15));t.SetLayer(layer)
        if layer==p.B_SilkS:t.SetMirrored(True)
        self.b.Add(t)
    def holes(self,points):
        for i,(x,y) in enumerate(points):
            f=self.fp('MountingHole:MountingHole_3.2mm_M3');f.SetReference('H'+str(i+1));f.SetPosition(pt(x,y));f.Value().SetVisible(False);f.Reference().SetVisible(False);self.b.Add(f)
    def write_sch(self,page):
        pg=self.pages[page];root=page=='main';sid=self.rootid if root else pg['id']
        s=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {sid}) (paper "A3")\n'
        s+=f'(title_block (title {q(self.name+" / "+page)}) (date "2026-10-22") (rev "A - UNVERIFIED") (comment 1 "Final verification not executed; see QA_CHECKLIST.md"))\n'
        s+='(lib_symbols\n'+''.join(v[0].replace('(symbol '+q(k),'(symbol '+q('SS8:'+k),1) for k,v in SYMS.items())+')\n'
        for c in pg['parts']:
            x,y=c['x'],c['y'];name=c['sym'];_,pos,h=SYMS[name]
            s+=f'(symbol (lib_id {q("SS8:"+name)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {c["uuid"]})\n'
            for prop,val,py,hide in [('Reference',c['ref'],y-h-5.08,False),('Value',c['value'],y-h-2.54,False),('Footprint',c['fp'],y,True)]:
                s+=f'(property {q(prop)} {q(val)} (at {x} {py} 0) (effects (font (size 1.27 1.27))'+(' (hide yes)' if hide else '')+'))\n'
            for n in pos:s+=f'(pin {q(n)} (uuid {uid()}))\n'
            path='/'+self.rootid+('' if root else '/'+pg['id'])
            s+=f'(instances (project {q(self.name)} (path {q(path)} (reference {q(c["ref"])}) (unit 1)))))\n'
            for n,(px,py,side) in pos.items():
                ax=x+px;ay=y-py;net=c['nets'].get(n)
                if net:
                    bx=ax+(-5.08 if side=='L' else 5.08)
                    s+=f'(wire (pts (xy {ax} {ay}) (xy {bx} {ay})) (stroke (width 0) (type default)) (uuid {uid()}))\n'
                    ang=0 if side=='L' else 180
                    s+=f'(global_label {q(net)} (shape passive) (at {bx} {ay} {ang}) (effects (font (size 1 1)) (justify '+('left' if side=='L' else 'right')+f')) (uuid {uid()}))\n'
                else:s+=f'(no_connect (at {ax} {ay}) (uuid {uid()}))\n'
        if root:
            for i,(nm,pg2) in enumerate((a,b) for a,b in self.pages.items() if a!='main'):
                x=20+(i%4)*95;y=208+(i//4)*28
                s+=f'(sheet (at {x} {y}) (size 80 18) (stroke (width 0.1524) (type default)) (fill (color 0 0 0 0)) (uuid {pg2["id"]}) (property "Sheetname" {q(nm)} (at {x} {y-1} 0) (effects (font (size 1.27 1.27)) (justify left bottom))) (property "Sheetfile" {q(nm+".kicad_sch")} (at {x} {y+19} 0) (effects (font (size 1.27 1.27)) (justify left top))) (instances (project {q(self.name)} (path {q("/"+self.rootid)} (page {q(i+2)})))))\n'
        s+='(text "UNVERIFIED REV A - 12 V NOMINAL DRIVE - 3.3 V LOGIC" (at 20 15 0) (effects (font (size 2 2)) (justify left)) (uuid '+uid()+'))\n'
        if root:s+='(sheet_instances (path "/" (page "1")))\n'
        s+=')\n';file=self.name if root else page
        if root and self.name=='Array8x8':s=with_power_flags(s,self.rootid,self.name)
        (self.folder/(file+'.kicad_sch')).write_text(s)
    def save(self):
        for name in self.pages:self.write_sch(name)
        (self.folder/'SS8.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor")\n'+''.join(v[0] for v in SYMS.values())+')')
        (self.folder/'sym-lib-table').write_text('(sym_lib_table (lib (name "SS8") (type "KiCad") (uri "${KIPRJMOD}/SS8.kicad_sym") (options "") (descr "Project-local symbols")))')
        (self.folder/'fp-lib-table').write_text('(fp_lib_table (lib (name "SS8") (type "KiCad") (uri "${KIPRJMOD}/SS8.pretty") (options "") (descr "Project-local footprints")))')
        proj={'meta':{'filename':self.name+'.kicad_pro','version':1},'net_settings':{'classes':[{'name':'Default','clearance':.2,'track_width':.25,'via_diameter':.65,'via_drill':.3,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.25,'diff_pair_gap':.25,'diff_pair_via_gap':.25},{'name':'Power','clearance':.25,'track_width':.8,'via_diameter':.8,'via_drill':.4,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.25,'diff_pair_gap':.25,'diff_pair_via_gap':.25}], 'netclass_patterns':[{'netclass':'Power','pattern':n} for n in ['+12V','VIN','VFUSED']],'meta':{'version':4}}}
        (self.folder/(self.name+'.kicad_pro')).write_text(json.dumps(proj,indent=2))
        p.SaveBoard(str(self.folder/(self.name+'.kicad_pcb')),self.b)
        (self.folder/'authoring').mkdir(exist_ok=True)
        p.SaveBoard(str(self.folder/'authoring'/'placed.kicad_pcb'),self.b)
        p.ExportSpecctraDSN(self.b,str(self.folder/(self.name+'.dsn')))
        with (self.folder/'BOM.csv').open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['Reference','Value / part','Footprint','Quantity','Notes'])
            for c in self.comps:w.writerow([c['ref'],c['value'],c['fp'],1,'Unverified Rev A'])
        with (self.folder/'connectivity.csv').open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['Reference','Pin','Net'])
            for c in self.comps:
                for n,net in c['nets'].items():w.writerow([c['ref'],n,net or 'NC'])

def transducer_fp(folder):
    # 0.64 +/- 0.1 mm square leads: 1.2 mm finished hole accommodates diagonal.
    s='(footprint "MA40S4S_P5mm" (version 20250114) (generator pcbnew) (layer "F.Cu") (attr through_hole)'
    s+='(property "Reference" "T" (at 0 -6 0) (layer "F.SilkS") (effects (font (size .8 .8) (thickness .12))))'
    s+='(property "Value" "MA40S4S" (at 0 6 0) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))'
    for layer,rad in [('F.SilkS',5.1),('F.CrtYd',5.25),('F.Fab',4.95)]:s+=f'(fp_circle (center 0 0) (end {rad} 0) (stroke (width .1) (type default)) (fill none) (layer "{layer}"))'
    for n,x in [(1,-2.5),(2,2.5)]:s+=f'(pad "{n}" thru_hole '+('rect' if n==1 else 'circle')+f' (at {x} 0) (size 2 2) (drill 1.2) (layers "*.Cu" "*.Mask"))'
    s+=')';(folder/'SS8.pretty/MA40S4S_P5mm.kicad_mod').write_text(s)

def build_array():
    d=Design('Array8x8',160,124);transducer_fp(d.folder)
    # Source controls, interleaved with ground in a straight 26-way ribbon.
    signals=['+3V3']+[f'DATA{i}' for i in range(8)]+['SCLK','LATCH','OE_N','CLR_N']
    cable={str(2*i+1):s for i,s in enumerate(signals)};cable.update({str(i):'GND' for i in range(2,27,2)})
    d.add('J1','IDC26 / FPGA CABLE','IDC26',IDC,cable,150,60,sx=55,sy=65)
    d.add('J2','12V DC INPUT','POWER',TERM,{'1':'VIN','2':'GND'},10,115,sx=150,sy=45)
    d.add('F1','1A fast / 1812','FUSE','Fuse:Fuse_1812_4532Metric',{'1':'VIN','2':'VFUSED'},24,115,sx=215,sy=45)
    d.add('D1','SS34 / SMC','DIODE','Diode_SMD:D_SMC',{'1':'+12V','2':'VFUSED'},33,115,sx=285,sy=45)
    d.add('C1','220uF 35V low ESR','CP',CAPB,{'1':'+12V','2':'GND'},42,115,sx=355,sy=45)
    d.add('C2','10uF 10V X7R','C',CFP,{'1':'+3V3','2':'GND'},98,115,sx=150,sy=90,bottom=True)
    d.add('R1','10k','R',RFP,{'1':'+3V3','2':'OE_N'},108,115,sx=215,sy=90,bottom=True)
    d.add('R2','10k','R',RFP,{'1':'CLR_N','2':'GND'},118,115,sx=285,sy=90,bottom=True)
    d.add('R3','10k','R',RFP,{'1':'SCLK','2':'GND'},108,120,sx=215,sy=125,bottom=True)
    d.add('R4','10k','R',RFP,{'1':'LATCH','2':'GND'},118,120,sx=285,sy=125,bottom=True)
    qpins=[15,1,2,3,4,5,6,7]
    for r in range(8):
        page=f'Row{r+1:02d}';d.page(page);y=15+12*r
        nets={'14':f'DATA{r}','11':'SCLK','12':'LATCH','13':'OE_N','10':'CLR_N','16':'+3V3','8':'GND','9':None}
        nets.update({str(qpins[c]):f'Q{r*8+c:02d}' for c in range(8)})
        d.add(f'U{r+1}','74HC595N / DIP-16','HC595',DIP16,nets,122,y,page,48,58,angle=90,bottom=True)
        d.add(f'C{10+r}','100nF 50V X7R','C',CFP,{'1':'+3V3','2':'GND'},134,y,page,48,106,bottom=True,angle=90)
        for pair in range(4):
            index=r*4+pair;ca=r*8+pair*2;cb=ca+1;x=21+24*pair
            d.add(f'U{101+index}','TC4427EPA / DIP-8','TC4427',DIP8,{'1':None,'8':None,'2':f'Q{ca:02d}','4':f'Q{cb:02d}','3':'GND','6':'+12V','7':f'DRV{ca:02d}','5':f'DRV{cb:02d}'},x,y,page,135+pair*77,55,bottom=True)
            d.add(f'C{101+index}','100nF 50V X7R','C',CFP,{'1':'+12V','2':'GND'},x+9,y-2.5,page,135+pair*77,98,bottom=True,angle=90)
            d.add(f'C{201+index}','1uF 50V X7R','C',CFP,{'1':'+12V','2':'GND'},x+9,y+2.5,page,135+pair*77,130,bottom=True,angle=90)
            for j,ch in enumerate([ca,cb]):
                d.add(f'R{101+ch}','10k','R',RFP,{'1':f'Q{ch:02d}','2':'GND'},x-9,y-2.5+j*5,page,135+pair*77,162+j*32,bottom=True,angle=90)
                d.add(f'T{ch+1}','MA40S4S','MA40S4S','SS8:MA40S4S_P5mm',{'1':f'DRV{ch:02d}','2':'GND'},15+12*(pair*2+j),y,page,135+pair*77,226+j*32,angle=90)
    d.holes([(4,4),(156,4),(4,120),(156,120)])
    d.text('SONICSURFACE 8x8 / REV A / UNVERIFIED',59,4)
    d.text('MA40S4S / 12 mm pitch / FRONT',55,108,size=.9)
    d.text('12V DC',10,109,size=.8);d.text('FPGA 3.3V',150,37,size=.8)
    d.text('TC4427 DIP-8 / 74HC595 DIP-16',60,6,p.B_SilkS)
    d.save();return d

def build_adapter():
    d=Design('CoreEP4CE6_Adapter',38,65)
    # Manufacturer P1 numbering; unused header contacts deliberately NC.
    pairs=[('DATA0',3,59),('DATA1',5,64),('DATA2',7,66),('DATA3',9,68),('DATA4',11,70),('DATA5',13,72),('DATA6',15,74),('DATA7',17,76),('SCLK',21,84),('LATCH',22,85),('OE_N',19,80),('CLR_N',20,83)]
    hn={str(i):None for i in range(1,45)};hn.update({'1':'GND','2':'+3V3','23':'GND'})
    for name,pin,fpga in pairs:hn[str(pin)]=name+'_SRC'
    d.add('J1','CoreEP4CE6 P1 ONLY','CORE_P1',SOCKET,hn,5,31,sx=50,sy=100)
    signals=['+3V3']+[a[0] for a in pairs];cn={str(2*i+1):n for i,n in enumerate(signals)};cn.update({str(i):'GND' for i in range(2,27,2)})
    d.add('J2','IDC26 to ARRAY J1','IDC26',IDC,cn,30,31,sx=355,sy=100)
    for i,(name,pin,fpga) in enumerate(pairs):
        d.add(f'R{i+1}','33R source termination','R',RFP,{'1':name+'_SRC','2':name},16.5,6+i*4.5,sx=140+(i%2)*95,sy=35+(i//2)*35)
    d.holes([(22,4),(22,61)]);d.text('CORE P1',9,2,size=.8);d.text('REV A',30,60,size=.8)
    d.save()
    with (ROOT/'CABLE_PIN_MAP.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Array J1 / Adapter J2','Signal','Core P1 physical pin','FPGA package pin','Direction'])
        w.writerow([1,'+3V3',2,'module 3.3 V rail','module to array'])
        for i,(name,pin,fpga) in enumerate(pairs):w.writerow([3+2*i,name,pin,fpga,'FPGA output'])
        for n in range(2,27,2):w.writerow([n,'GND','1 and 23','GND','return'])
    lines=['# Rev A pin assignments only; integrate with a 64-channel HDL project.', 'set_global_assignment -name FAMILY "Cyclone IV E"','set_global_assignment -name DEVICE EP4CE6E22C8','set_location_assignment PIN_23 -to CLK_50','set_instance_assignment -name IO_STANDARD "3.3-V LVTTL" -to CLK_50']
    for name,pin,fpga in pairs:
        port='DATA['+name[4:]+']' if name.startswith('DATA') else name
        lines += [f'set_location_assignment PIN_{fpga} -to {port}',f'set_instance_assignment -name IO_STANDARD "3.3-V LVTTL" -to {port}']
    (ROOT/'CoreEP4CE6_8x8_pins.qsf').write_text('\n'.join(lines)+'\n')
    return d

if __name__=='__main__':
    a=build_array();b=build_adapter()
    print('Created editable schematics, placed boards, local libraries, BOM and cable map. Routing still required.')

