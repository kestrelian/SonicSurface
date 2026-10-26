from pathlib import Path
import re,sys
root=Path(__file__).resolve().parent
for name in (sys.argv[1:] or ['Array8x8_RevB','DualArray_Controller_RevB']):
    folder=root/name;s=(folder/(name+'.dsn')).read_text()
    s=s.replace('(clearance 200)','(clearance 150)').replace('(clearance 50 (type smd_smd))','(clearance 150 (type smd_smd))')
    s=s.replace('Via[0-1]_600:300_um','Via[0-1]_650:300_um')
    s=re.sub(r'(\(circle\s+\S+\s+)600(?=\s|\))',r'\g<1>650',s)
    start=s.index('(class kicad_default');depth=0
    for j in range(start,len(s)):
        if s[j]=='(':depth+=1
        elif s[j]==')':
            depth-=1
            if depth==0:end=j+1;break
    old=s[start:end];nets=old[len('(class kicad_default'):old.index('(circuit')].split()
    power=[n for n in nets if n.startswith(('VDRV','VIN','VREG','VPROT','VINPUT')) or n in ['SW1','SW2','FET_COMMON']]
    logic=[n for n in nets if n=='+3V3'];ground=[n for n in nets if n in ['GND','IN_RTN']]
    def cls(n,ns,w):return '(class '+n+' '+' '.join(ns)+' (circuit (use_via "Via[0-1]_650:300_um")) (rule (width '+str(w)+') (clearance 150)))'
    new=cls('Signals',[n for n in nets if n not in power+logic+ground],200)+'\n'+cls('DriverPower',power,500 if 'Controller' in name else 1000)+'\n'+cls('LogicPower',logic,500)+'\n'+cls('Ground',ground,400)
    s=s[:start]+new+s[end:]
    (folder/'authoring/routing_input.dsn').write_text(s)
    print(name,'routing input written')
