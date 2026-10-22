"""Prepare explicit manufacturing routing classes in the exported DSN."""
from pathlib import Path
import re
root=Path(__file__).resolve().parent
src=root/'Array8x8/Array8x8.dsn'
s=src.read_text()
s=s.replace('(width 200)','(width 250)').replace('(clearance 50 (type smd_smd))','(clearance 200 (type smd_smd))')
s=s.replace('Via[0-1]_600:300_um','Via[0-1]_700:300_um')
s=re.sub(r'(\(circle\s+\S+\s+)600(?=\s|\))',r'\g<1>700',s)
start=s.index('(class kicad_default');depth=0;end=start
for i in range(start,len(s)):
    if s[i]=='(':depth+=1
    elif s[i]==')':
        depth-=1
        if depth==0:end=i+1;break
old=s[start:end];names=old[len('(class kicad_default'):old.index('(circuit')].split()
def cls(name,nets,width):
    return f'(class {name} '+ ' '.join(nets)+f' (circuit (use_via "Via[0-1]_700:300_um")) (rule (width {width}) (clearance 200)))'
power=['+12V','VFUSED','VIN'];ground=['GND']
new=cls('Signals',[n for n in names if n not in power+ground],250)+'\n'+cls('Power',power,800)+'\n'+cls('Ground',ground,400)
s=s[:start]+new+s[end:]
out=root/'Array8x8/authoring/routing_input.dsn';out.write_text(s)
print(out)
