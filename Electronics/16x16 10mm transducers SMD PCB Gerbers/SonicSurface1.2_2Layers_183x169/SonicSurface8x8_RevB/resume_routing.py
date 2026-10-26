"""Preserve authored copper when continuing a routing session; no final QA."""
from pathlib import Path
import sys,re
import pcbnew as p
root=Path(__file__).resolve().parent
name=sys.argv[1];f=root/name
b=p.LoadBoard(str(f/'authoring/placed.kicad_pcb'))
assert p.ImportSpecctraSES(b,str(f/'authoring/routed.ses'))
p.SaveBoard(str(f/'authoring/work.kicad_pcb'),b)
p.ExportSpecctraDSN(b,str(f/'authoring/seed.dsn'))
def block(s,start):
    depth=0
    for i in range(start,len(s)):
        if s[i]=='(':depth+=1
        elif s[i]==')':
            depth-=1
            if depth==0:return s[start:i+1]
s=(f/'authoring/seed.dsn').read_text();old=(f/'authoring/routing_input.dsn').read_text()
classes='\n'.join(block(old,m.start()) for m in re.finditer(r'\(class ',old))
for m in list(re.finditer(r'\(class ',s))[::-1]:
    v=block(s,m.start());s=s[:m.start()]+s[m.start()+len(v):]
idx=s.index('(network')+len('(network');s=s[:idx]+'\n'+classes+s[idx:]
s=s.replace('(clearance 200)','(clearance 150)').replace('(clearance 50 (type smd_smd))','(clearance 150 (type smd_smd))')
s=s.replace('Via[0-1]_600:300_um','Via[0-1]_650:300_um')
s=re.sub(r'(\(circle\s+\S+\s+)600(?=\s|\))',r'\g<1>650',s)
(f/'authoring/seed.dsn').write_text(s)
print('Saved continued copper to seed.dsn')
