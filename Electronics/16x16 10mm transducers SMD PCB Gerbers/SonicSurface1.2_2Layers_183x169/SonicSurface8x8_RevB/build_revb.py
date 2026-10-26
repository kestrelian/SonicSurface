"""Rev B authoring generator. Does not run ERC, DRC or final manufacturing QA."""
from pathlib import Path
import csv,json,math,sys,hashlib
import design_base as b
import pcbnew as p

ROOT=Path(__file__).resolve().parent
b.ROOT=ROOT
SO8='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'
TSS20='Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm'
SOT6='Package_TO_SOT_SMD:SOT-23-6'
SOT5='Package_TO_SOT_SMD:SOT-23-5'
R='Resistor_SMD:R_0603_1608Metric'
C='Capacitor_SMD:C_0603_1608Metric'
PWRCON='Connector_Molex:Molex_Micro-Fit_3.0_43650-0215_1x02_P3.00mm_Vertical'
TP='TestPoint:TestPoint_Pad_D1.5mm'

def defs(name,pins):
    b.DEFS[name]=[(str(n),nm,ty,side) for n,nm,ty,side in pins]
defs('TP',[(1,'TEST','passive','L')])
defs('L',[(1,'1','passive','L'),(2,'2','passive','R')])
defs('LVC244',[(20,'VCC','power_in','L'),(10,'GND','power_in','L'),(1,'OE1_N','input','L'),(19,'OE2_N','input','L')]+[(n,'A'+str(i),'input','L') for i,n in enumerate([2,4,6,8,11,13,15,17])]+[(n,'Y'+str(i),'tri_state','R') for i,n in enumerate([18,16,14,12,9,7,5,3])])
defs('SUP',[(6,'VDD','power_in','L'),(2,'GND','power_in','L'),(5,'SENSE','input','L'),(3,'MR_N','input','L'),(4,'CT','passive','R'),(1,'RESET_N','open_collector','R')])
defs('INV',[(1,'NC','no_connect','L'),(2,'A','input','L'),(3,'GND','power_in','L'),(4,'Y','output','R'),(5,'VCC','power_in','L')])
defs('OR',[(1,'A','input','L'),(2,'B','input','L'),(3,'GND','power_in','L'),(4,'Y','output','R'),(5,'VCC','power_in','L')])
defs('EFUSE',[(1,'IN','power_in','L'),(2,'IN','power_in','L'),(3,'UVLO','input','L'),(4,'NC','no_connect','L'),(5,'OVP','input','L'),(6,'MODE','input','L'),(7,'SHDN_N','input','L'),(8,'RTN','power_in','L'),(9,'GND','power_in','L'),(10,'IMON','output','R'),(11,'ILIM','passive','R'),(12,'dVdT','passive','R'),(13,'NC','no_connect','R'),(14,'FLT_N','open_collector','R'),(15,'OUT','power_out','R'),(16,'OUT','power_out','R'),(17,'EP_RTN','power_in','L')])
defs('BUCKBOOST',[(1,'PGND','power_in','L'),(2,'RUN','input','L'),(3,'SW2','passive','R'),(4,'PVOUT','power_out','R'),(5,'GND','power_in','L'),(6,'GND','power_in','L'),(7,'VC','passive','R'),(8,'FB','input','L'),(9,'RT','passive','L'),(10,'PGND','power_in','L'),(11,'PGND','power_in','L'),(12,'VCC','power_out','R'),(13,'VIN','power_in','L'),(14,'PVCC','power_out','R'),(15,'BST2','passive','R'),(16,'BST1','passive','R'),(17,'PVIN','power_in','L'),(18,'SW1','passive','R'),(19,'PWM_SYNC','input','L'),(20,'PGND','power_in','L'),(21,'EP_PGND','power_in','L')])
defs('OVCUT',[(1,'VIN','power_in','L'),(2,'UV','input','L'),(3,'OV','input','L'),(4,'GND','power_in','L'),(5,'SHDN_N','input','L'),(6,'FAULT_N','open_collector','R'),(7,'VOUT','power_in','R'),(8,'GATE','output','R')])
defs('DUALMOS',[(1,'S1','passive','L'),(2,'G1','input','L'),(3,'S2','passive','L'),(4,'G2','input','L'),(5,'D2','passive','R'),(6,'D2','passive','R'),(7,'D1','passive','R'),(8,'D1','passive','R')])
defs('REG33',[(1,'VIN','power_in','L'),(2,'GND','power_in','L'),(3,'VOUT','power_out','R')])
b.SYMS={k:b.symbol(k) for k in b.DEFS}

class Design(b.Design):
    def __init__(self,name,w,h):
        super().__init__(name,w,h)
        self.groupcounts={}
        ds=self.b.GetDesignSettings();ds.m_MinClearance=b.mm(.15);ds.m_TrackMinWidth=b.mm(.20)
    def fp(self,id):
        lib,name=id.split(':')
        alias=name if len(name)<42 else 'FP_'+hashlib.sha1(name.encode()).hexdigest()[:12]
        local=self.folder/'SS8.pretty'/(alias+'.kicad_mod')
        if lib!='SS8' and not local.exists():
            source=(b.LIB/(lib+'.pretty')/(name+'.kicad_mod')).read_text()
            local.write_text(source.replace('"'+name+'"','"'+alias+'"',1))
        obj=p.FootprintLoad(str(self.folder/'SS8.pretty'),alias)
        if obj is None:raise RuntimeError('Footprint load failed: '+id)
        obj.SetFPID(p.LIB_ID('SS8',alias))
        return obj
    def part(self,ref,value,sym,fp,nets,x,y,group='Circuit',**kw):
        count=self.groupcounts.get(group,0);self.groupcounts[group]=count+1
        # Six components per sheet leaves room for explicit names and pin labels.
        pg=group+f'_{count//6+1:02d}'
        if pg not in self.pages:self.page(pg)
        obj=self.add(ref,value,sym,fp,nets,x,y,pg,60+130*(count%3),65+110*((count%6)//3),**kw)
        name=fp.split(':')[1]; self.comps[-1]['fp']='SS8:'+(name if len(name)<42 else 'FP_'+hashlib.sha1(name.encode()).hexdigest()[:12])
        return obj
    def resistor(self,ref,value,n1,n2,x,y,group='Circuit',fp=R,**kw):return self.part(ref,value,'R',fp,{'1':n1,'2':n2},x,y,group,**kw)
    def cap(self,ref,value,n1,n2,x,y,group='Circuit',fp=C,**kw):return self.part(ref,value,'C',fp,{'1':n1,'2':n2},x,y,group,**kw)
    def tp(self,ref,net,x,y,group='Test',**kw):return self.part(ref,net,'TP',TP,{'1':net},x,y,group,**kw)
    def save(self):
        super().save()
        # Root is an index; distribute the many hierarchy entries across A2 paper.
        f=self.folder/(self.name+'.kicad_sch');s=f.read_text().replace('(paper "A3")','(paper "A1")')
        # Relocate root sheet boxes generated by base to a regular, spacious index.
        import re
        sheetno=0
        def move(m):
            nonlocal sheetno
            x=25+(sheetno%6)*130;y=40+(sheetno//6)*42;sheetno+=1
            oldx,oldy=map(float,m.group(1,2));chunk=m.group(0)
            return chunk
        # Existing root index starts at y208; A1 is tall enough for every sheet.
        f.write_text(s)
        pro=json.loads((self.folder/(self.name+'.kicad_pro')).read_text())
        pro['net_settings']['classes'][0].update(clearance=.15,track_width=.20,via_diameter=.65,via_drill=.3)
        pro['net_settings']['classes'][1].update(clearance=.2,track_width=.5 if self.name.startswith('Dual') else 1.0)
        pro['net_settings']['netclass_patterns']=[{'netclass':'Power','pattern':n} for n in self.nets if n.startswith(('VDRV','VIN','VREG','VPROT','VINPUT','+3V3'))]
        (self.folder/(self.name+'.kicad_pro')).write_text(json.dumps(pro,indent=2))

def buffer(d,ref,ins,outs,x,y,oe='GND',supply='+3V3',group='Interface',bottom=False):
    ns={'20':supply,'10':'GND','1':oe,'19':oe}
    for i,(a,z) in enumerate(zip([2,4,6,8,11,13,15,17],[18,16,14,12,9,7,5,3])):
        ns[str(a)]=ins[i] if i<len(ins) else 'GND';ns[str(z)]=outs[i] if i<len(outs) else None
    d.part(ref,'SN74LVC244APW / Ioff','LVC244',TSS20,ns,x,y,group,bottom=bottom)
    d.cap('C'+ref[1:]+'0','100nF 50V X7R',supply,'GND',x+5.5,y+(4.7 if bottom else -4.7),group,bottom=bottom)

def supervisor(d,ref,part,sense,mr,out,x,y,group='Supervision',bottom=False):
    d.part(ref,part,'SUP',SOT6,{'1':out,'2':'GND','3':mr,'4':None,'5':sense,'6':'+3V3'},x,y,group,bottom=bottom)
    d.cap('C'+ref[1:]+'0','100nF 50V X7R','+3V3','GND',x+3.5,y,group,bottom=bottom)
    d.resistor('R'+ref[1:]+'0','10k',out,'+3V3',x,y+3.5,group,bottom=bottom)

def cable_nets(prefix='',raw=False):
    signals=['+3V3']+[prefix+f'DATA{i}'+('_RX' if raw else '') for i in range(8)]+[prefix+s+('_RX' if raw else '') for s in ['SCLK','LATCH','OE_N','CLR_N']]
    return {**{str(2*i+1):s for i,s in enumerate(signals)},**{str(i):'GND' for i in range(2,27,2)}}

def array():
    d=Design('Array8x8_RevB',114,120);b.transducer_fp(d.folder)
    # Round 1.7 mm copper pads retain 0.25 mm nominal annular rings on 1.2 mm holes.
    fp=d.folder/'SS8.pretty/MA40S4S_P5mm.kicad_mod'
    s=fp.read_text().replace('thru_hole rect','thru_hole circle').replace('(size 2 2)','(size 1.7 1.7)').replace('5.25','5.1')
    fp.write_text(s)
    d.part('J1','KEYED IDC26 / 100mm MAX','IDC26',b.IDC,cable_nets(raw=True),28,105,'Interface',angle=90,bottom=True)
    d.part('J2','REGULATED DRIVER POWER ONLY','POWER',PWRCON,{'1':'VDRV','2':'GND'},104,106,'Power',bottom=True)
    d.part('C1','220uF 35V low ESR','CP',b.CAPB,{'1':'VDRV','2':'GND'},101,94,'Power',bottom=True)
    d.cap('C2','10uF 10V X7R','+3V3','GND',68,108,'Power',fp=b.CFP,bottom=True)
    d.resistor('R1','2.2k 0.5W discharge','VDRV','GND',99,115,'Power',fp='Resistor_SMD:R_1210_3225Metric',bottom=True)
    buffer(d,'U50',[f'DATA{i}_RX' for i in range(8)],[f'DATA{i}' for i in range(8)],21,93,bottom=True)
    buffer(d,'U51',[s+'_RX' for s in ['SCLK','LATCH','OE_N','CLR_N']],['SCLK','LATCH','OE_CMD_N','CLR_N'],61,93,bottom=True)
    for i,n in enumerate([f'DATA{j}_RX' for j in range(8)]+['SCLK_RX','LATCH_RX','CLR_N_RX']):
        d.resistor(f'R{20+i}','100k',n,'GND',8+5*i,88,'Interface',bottom=True,angle=90)
    d.resistor('R31','10k','OE_N_RX','+3V3',72,91,'Interface',bottom=True)
    d.resistor('R32','10k','OE_CMD_N','+3V3',72,95,'Interface',bottom=True)
    d.resistor('R33','10k','OE_LOCAL_N','+3V3',85,115,'Supervision',bottom=True)
    supervisor(d,'U52','TPS3808G33DBVR','+3V3','+3V3','LOGIC_OK',78,103,bottom=True)
    supervisor(d,'U53','TPS3808G01DBVR','DRV_SENSE','LOGIC_OK','RAILS_OK',89,103,bottom=True)
    d.resistor('R34','374k 0.1%','VDRV','DRV_SENSE',88,94,'Supervision',bottom=True)
    d.resistor('R35','10k 0.1%','DRV_SENSE','GND',88,97,'Supervision',bottom=True)
    d.part('U54','SN74LVC1G04DBVR','INV',SOT5,{'1':None,'2':'RAILS_OK','3':'GND','4':'RAIL_BAD','5':'+3V3'},78,112,'Supervision',bottom=True)
    d.part('U55','SN74LVC1G32DBVR','OR',SOT5,{'1':'RAIL_BAD','2':'OE_CMD_N','3':'GND','4':'OE_LOCAL_N','5':'+3V3'},89,112,'Supervision',bottom=True)
    d.cap('C54','100nF 50V X7R','+3V3','GND',74,112,'Supervision',bottom=True)
    d.cap('C55','100nF 50V X7R','+3V3','GND',93,112,'Supervision',bottom=True)
    qpins=[15,1,2,3,4,5,6,7]
    for row in range(8):
        y=8+10.3*row;grp=f'Row{row+1:02d}'
        nets={'14':f'DATA{row}','11':'SCLK','12':'LATCH','13':'OE_LOCAL_N','10':'CLR_N','16':'+3V3','8':'GND','9':None}
        nets.update({str(qpins[col]):f'Q{8*row+col:02d}' for col in range(8)})
        d.part(f'U{row+1}','SN74HC595N DIP-16','HC595',b.DIP16,nets,100,y,grp,angle=90,bottom=True)
        d.cap(f'C{10+row}','100nF 50V X7R','+3V3','GND',111,y,grp,bottom=True,angle=90)
        for pair in range(4):
            k=row*4+pair;ch=8*row+2*pair;x=13.15+20.6*pair
            f=d.part(f'U{101+k}','TC4427EPA DIP-8','TC4427',b.DIP8,{'1':None,'8':None,'2':f'Q{ch:02d}','4':f'Q{ch+1:02d}','3':'GND','6':'VDRV','7':f'OUT{ch:02d}','5':f'OUT{ch+1:02d}'},x,y,grp,bottom=True)
            # Pin 1 remains marked on silk/fab; all pads round for dense lead clearance.
            for pad in f.Pads():pad.SetShape(p.PAD_SHAPE_CIRCLE);pad.SetSize(b.pt(1.6,1.6))
            d.cap(f'C{101+k}','100nF 50V X7R','VDRV','GND',x+8.0,y-3.35,grp,bottom=True,angle=90)
            d.cap(f'C{201+k}','1uF 50V X7R','VDRV','GND',x+11.2,y-3.35,grp,fp=b.CFP,bottom=True,angle=90)
            for j in range(2):
                n=ch+j
                d.resistor(f'R{101+n}','10k',f'Q{n:02d}','GND',x+8.0+3.2*j,y,grp,bottom=True,angle=90)
                d.resistor(f'R{201+n}','22R damping',f'OUT{n:02d}',f'DRV{n:02d}',x+8.0+3.2*j,y+3.35,grp,bottom=True,angle=90)
                d.part(f'T{n+1}','MA40S4S','MA40S4S','SS8:MA40S4S_P5mm',{'1':f'DRV{n:02d}','2':'GND'},8+10.3*(2*pair+j),y,grp,angle=90)
    for i,(n,x) in enumerate([('GND',8),('+3V3',15),('VDRV',22),('SCLK',29),('LATCH',36),('OE_LOCAL_N',43),('RAILS_OK',50),('DRV00',57),('DRV63',64)]):d.tp('TP'+str(i+1),n,x,116,bottom=True)
    d.holes([(3,3),(111,3),(3,117),(111,117)])
    d.text('8x8 REV B / 10.3mm / UNVERIFIED',54,118,size=.8)
    d.text('J1 PIN1 / KEYED / 3V3 ONLY',28,111,p.B_SilkS,.7)
    d.text('J2 16.8V REGULATED',101,100,p.B_SilkS,.7)
    d.save()
    # Save the rounded DIP pad variant as a matching local footprint.
    f=next(c['f'] for c in d.comps if c['ref']=='U101')
    p.FootprintSave(str(d.folder/'SS8.pretty'),f)
    return d

# Core P1 pin numbers from Waveshare schematic; module rails are not joined to array rails.
DATA_A=[(3,59),(5,64),(7,66),(9,68),(11,70),(13,72),(15,74),(17,76)]
DATA_B=[(4,60),(6,65),(8,67),(10,69),(12,71),(14,73),(16,75),(18,77)]
CONTROL={'SCLK':(21,84),'LATCH':(22,85),'A_OE_N':(19,80),'B_OE_N':(20,83),'A_CLR_N':(25,86),'B_CLR_N':(26,87)}

def adapter():
    d=Design('DualArray_Controller_RevB',120,140)
    hdr={str(i):None for i in range(1,45)};hdr.update({'1':'GND','2':'CORE_3V3_SENSE','23':'GND'})
    mapping={}
    for bank,arr in [('A',DATA_A),('B',DATA_B)]:
        for i,(pin,pkg) in enumerate(arr):mapping[f'{bank}_DATA{i}']=(pin,pkg)
    mapping.update(CONTROL)
    for name,(pin,pkg) in mapping.items():hdr[str(pin)]=name+'_SRC'
    d.part('J1','CoreEP4CE6 P1 / POWER PINS ISOLATED','CORE_P1',b.SOCKET,hdr,8,35,'Core')
    # Three octal buffers independently drive the two cable branches.
    supervisor(d,'U4','TPS3808G01DBVR','CORE_SENSE_DIV','+3V3','CORE_OK',21,67,group='Core')
    d.resistor('R90','64.9k 0.1%','CORE_3V3_SENSE','CORE_SENSE_DIV',16,65,'Core')
    d.resistor('R91','10k 0.1%','CORE_SENSE_DIV','GND',16,69,'Core')
    d.part('U5','SN74LVC1G04DBVR','INV',SOT5,{'1':None,'2':'CORE_OK','3':'GND','4':'CORE_BAD','5':'+3V3'},29,67,'Core')
    d.cap('C5','100nF 50V X7R','+3V3','GND',33,67,'Core')
    for bank,y in [('A',24),('B',70)]:
        d.part('J2' if bank=='A' else 'J3','KEYED IDC26 / ARRAY '+bank,'IDC26',b.IDC,cable_nets(bank+'_'),109,y,'Cable'+bank)
        buffer(d,'U1' if bank=='A' else 'U2',[f'{bank}_DATA{i}_SRC' for i in range(8)],[f'{bank}_DATA{i}_BUF' for i in range(8)],60,y,oe='CORE_BAD',group='Cable'+bank)
        for i in range(8):
            d.resistor(f'R{1+(0 if bank=="A" else 8)+i}','33R source',f'{bank}_DATA{i}_BUF',f'{bank}_DATA{i}',85,y-14+i*4,'Cable'+bank)
            d.resistor(f'R{101+(0 if bank=="A" else 8)+i}','100k',f'{bank}_DATA{i}_SRC','GND',43,y-14+i*4,'Cable'+bank)
    ins=[];outs=[]
    for bank in ['A','B']:
        for sig in ['SCLK','LATCH','OE_N','CLR_N']:
            ins.append((sig if sig in ['SCLK','LATCH'] else bank+'_'+sig)+'_SRC');outs.append(bank+'_'+sig+'_BUF')
    buffer(d,'U3',ins,outs,60,47,oe='CORE_BAD',group='Control')
    for i,(bank,sig) in enumerate((bank,sig) for bank in ['A','B'] for sig in ['SCLK','LATCH','OE_N','CLR_N']):
        y=39+(i%4)*4;x=76 if bank=='A' else 92
        d.resistor(f'R{17+i}','33R source',bank+'_'+sig+'_BUF',bank+'_'+sig,x,y,'Control')
    for i,sig in enumerate(CONTROL):
        d.resistor(f'R{120+i}','100k',sig+'_SRC','CORE_3V3_SENSE' if 'OE_N' in sig else 'GND',35,14+i*6,'Core')
    d.resistor('R92','10k','A_OE_N','+3V3',99,41,'Control')
    d.resistor('R93','10k','B_OE_N','+3V3',99,55,'Control')
    power(d)
    for i,(n,x,y) in enumerate([('GND',8,82),('+3V3',18,82),('VIN',28,82),('VPROT',38,82),('VREG_16V8',48,82),('VDRV_SAFE',58,82),('CORE_OK',68,82),('A_SCLK',78,82),('B_SCLK',88,82),('A_OE_N',98,82),('B_OE_N',108,82)]):d.tp(f'TP{i+1}',n,x,y)
    d.holes([(3,3),(117,3),(3,137),(117,137)])
    d.text('CORE P1 PIN1',12,3,size=.8);d.text('ARRAY A',108,3,size=.8);d.text('ARRAY B',108,93,size=.8)
    d.text('REV B / 17-20V INPUT / 16.8V DRIVER OUTPUTS',60,137,size=.8)
    d.save()
    with (ROOT/'FPGA_INTERFACE.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Signal','Core P1 pin','FPGA package pin','Direction'])
        for name,(pin,pkg) in mapping.items():w.writerow([name,pin,pkg,'FPGA output'])
    lines=['# Hardware interface only. No firmware or bitstream supplied.','set_global_assignment -name FAMILY "Cyclone IV E"','set_global_assignment -name DEVICE EP4CE6E22C8','set_location_assignment PIN_23 -to CLK_50','set_instance_assignment -name IO_STANDARD "3.3-V LVTTL" -to CLK_50']
    for name,(pin,pkg) in mapping.items():
        port=name if 'DATA' not in name else name[:6]+'['+name[6:]+']'
        lines += [f'set_location_assignment PIN_{pkg} -to {{{port}}}',f'set_instance_assignment -name IO_STANDARD "3.3-V LVTTL" -to {{{port}}}']
    (ROOT/'CoreEP4CE6_DualArray_pins.qsf').write_text('\n'.join(lines)+'\n')
    return d

def power(d):
    g='InputProtection'
    d.part('J4','17-20V DC INPUT','POWER',PWRCON,{'1':'VIN','2':'GND'},10,101,g)
    d.part('F1','0451002.MRL / 2A 125V','FUSE','Fuse:Fuse_Littelfuse-NANO2-451_453',{'1':'VIN','2':'VINPUT_FUSED'},19,100,g)
    d.part('U10','TPS26600PWPR','EFUSE','Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.46x2.31mm_ThermalVias',{'1':'VINPUT_FUSED','2':'VINPUT_FUSED','3':'IN_UV','4':None,'5':'IN_OV','6':'IN_RTN','7':None,'8':'IN_RTN','9':'GND','10':'IN_IMON','11':'IN_ILIM','12':'IN_DVDT','13':None,'14':None,'15':'VPROT','16':'VPROT','17':'IN_RTN'},30,100,g)
    for ref,val,a,z,x,y in [('R200','121k 0.1%','VINPUT_FUSED','IN_UV',23,92),('R201','10k 0.1%','IN_UV','IN_RTN',28,92),('R202','178k 0.1%','VINPUT_FUSED','IN_OV',23,108),('R203','10k 0.1%','IN_OV','IN_RTN',28,108),('R204','8.06k 1%','IN_ILIM','IN_RTN',35,108),('R205','10k','IN_IMON','IN_RTN',35,92)]:d.resistor(ref,val,a,z,x,y,g)
    d.cap('C200','100nF 50V X7R','VINPUT_FUSED','GND',24,100,g)
    d.cap('C201','100nF 50V X7R','IN_DVDT','IN_RTN',40,108,g)
    d.cap('C202','10uF 50V X7R','VPROT','GND',40,100,g,fp='Capacitor_SMD:C_1210_3225Metric')
    g='BuckBoost'
    d.part('U11','LTC3115IFE-1#PBF','BUCKBOOST','Package_SO:HTSSOP-20-1EP_4.4x6.5mm_P0.65mm_EP2.74x3.86mm',{'1':'GND','2':'VPROT','3':'SW2','4':'VREG_16V8','5':'GND','6':'GND','7':'VC','8':'FB','9':'RT','10':'GND','11':'GND','12':'VCC_BB','13':'VPROT','14':'VCC_BB','15':'BST2','16':'BST1','17':'VPROT','18':'SW1','19':'VCC_BB','20':'GND','21':'GND'},59,103,g)
    d.part('L1','15uH MSS1048-153MLB','L','Inductor_SMD:L_Coilcraft_MSS1048-XXX',{'1':'SW1','2':'SW2'},59,119,g)
    for ref,val,a,z,x,y,fp in [('C210','100nF 50V X7R','BST1','SW1',65,99,C),('C211','100nF 50V X7R','BST2','SW2',53,99,C),('C212','4.7uF 10V X7R','VCC_BB','GND',65,103,b.CFP),('C213','100nF 50V X7R','VPROT','GND',65,107,C),('C214','10uF 50V X7R','VPROT','GND',67,113,'Capacitor_SMD:C_1210_3225Metric'),('C215','22uF 50V X7R','VREG_16V8','GND',51,113,'Capacitor_SMD:C_1210_3225Metric'),('C216','22uF 50V X7R','VREG_16V8','GND',46,113,'Capacitor_SMD:C_1210_3225Metric'),('C217','8.2nF C0G','COMP','FB',54,90,C),('C218','150pF C0G','VC','FB',59,90,C)]:d.cap(ref,val,a,z,x,y,g,fp=fp)
    for ref,val,a,z,x,y in [('R210','158k 0.1%','VREG_16V8','FB',48,99),('R211','10k 0.1%','FB','GND',48,103),('R212','47.5k 1%','RT','GND',53,107),('R213','18k 1%','VC','COMP',49,90)]:d.resistor(ref,val,a,z,x,y,g)
    d.resistor('R214','2.67k 1%','VREG_16V8','FF',65,90,g)
    d.cap('C219','1nF C0G','FF','FB',70,90,g)
    d.part('C222','470uF 35V low ESR','CP','Capacitor_THT:CP_Radial_D10.0mm_P5.00mm',{'1':'VREG_16V8','2':'GND'},46,129,g)
    g='OutputProtection'
    d.part('U12','LTC4365ITS8#PBF','OVCUT','Package_TO_SOT_SMD:TSOT-23-8',{'1':'VREG_16V8','2':'OUT_UV','3':'OUT_OV','4':'GND','5':'VREG_16V8','6':'OUT_FAULT_N','7':'VDRV_SAFE','8':'PASS_GATE'},82,106,g)
    d.part('Q1','Si9945CDY-T1-GE3','DUALMOS',SO8,{'1':'FET_COMMON','2':'PASS_GATE','3':'FET_COMMON','4':'PASS_GATE','5':'VDRV_SAFE','6':'VDRV_SAFE','7':'VREG_16V8','8':'VREG_16V8'},82,117,g)
    for ref,val,a,z,x,y in [('R220','290k 0.1%','VREG_16V8','OUT_UV',74,100),('R221','10k 0.1%','OUT_UV','GND',74,104),('R222','340k 0.01%','VREG_16V8','OUT_OV',89,100),('R223','10k 0.01%','OUT_OV','GND',89,104),('R224','10k','OUT_FAULT_N','+3V3',89,108)]:d.resistor(ref,val,a,z,x,y,g)
    # Gate capacitor limits turn-on current into the two array bulk capacitors.
    d.cap('C220','47nF 50V X7R','PASS_GATE','FET_COMMON',76,111,g)
    d.part('C221','470uF 35V low ESR','CP','Capacitor_THT:CP_Radial_D10.0mm_P5.00mm',{'1':'VDRV_SAFE','2':'GND'},99,114,g)
    for bank,y in [('A',101),('B',125)]:
        d.part('F2' if bank=='A' else 'F3','0451.750MRL / 750mA 125V','FUSE','Fuse:Fuse_Littelfuse-NANO2-451_453',{'1':'VDRV_SAFE','2':'VDRV_'+bank},98,y,g)
        d.part('J5' if bank=='A' else 'J6','16.8V POWER ARRAY '+bank,'POWER',PWRCON,{'1':'VDRV_'+bank,'2':'GND'},110,y,g)
    d.resistor('R225','10k 0.25W','VDRV_SAFE','GND',82,128,g,fp=b.RFP)
    g='LogicPower'
    d.part('U13','R-78E3.3-0.5','REG33','Converter_DCDC:Converter_DCDC_RECOM_R-78E-0.5_THT',{'1':'VPROT','2':'GND','3':'+3V3'},22,124,g)
    d.cap('C230','10uF 50V X7R','VPROT','GND',12,124,g,fp='Capacitor_SMD:C_1210_3225Metric')
    d.cap('C231','10uF 10V X7R','+3V3','GND',33,124,g,fp=b.CFP)
    d.cap('C232','100nF 50V X7R','+3V3','GND',33,128,g)
    d.resistor('R230','330R 0.125W minimum load','+3V3','GND',24,132,g,fp=b.RFP)

if __name__=='__main__':
    which=sys.argv[1:] or ['array','adapter']
    if 'array' in which:array()
    if 'adapter' in which:adapter()
    print('Rev B editable files authored. Routing and exports pending; final QA not executed.')

