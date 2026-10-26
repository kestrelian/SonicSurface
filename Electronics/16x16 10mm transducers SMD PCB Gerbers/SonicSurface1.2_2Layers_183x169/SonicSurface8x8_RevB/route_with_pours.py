from pathlib import Path
import re
import pcbnew as p
root=Path('SonicSurface8x8_RevB/Array8x8_RevB/authoring');b=p.LoadBoard(str(root/'work.kicad_pcb'));p.ExportSpecctraDSN(b,str(root/'no_ground.dsn'))
def block(s,start):
 d=0
 for i in range(start,len(s)):
  if s[i]=='(':d+=1
  elif s[i]==')':
   d-=1
   if not d:return s[start:i+1]
s=(root/'no_ground.dsn').read_text();old=(root/'routing_input.dsn').read_text()
classes=[]
for m in re.finditer(r'\(class ',old):
 v=block(old,m.start())
 if v.startswith('(class Ground'):continue
 if v.startswith('(class Signals'):v=v.replace('(width 200)','(width 150)').replace('Via[0-1]_650:300_um','Via[0-1]_500:200_um')
 classes.append(v)
for m in list(re.finditer(r'\(class |\(net GND\s',s))[::-1]:
 v=block(s,m.start());s=s[:m.start()]+s[m.start()+len(v):]
idx=s.index('(network')+len('(network');s=s[:idx]+'\n'+'\n'.join(classes)+s[idx:]
s=s.replace('(clearance 200)','(clearance 150)').replace('(clearance 50 (type smd_smd))','(clearance 150 (type smd_smd))').replace('Via[0-1]_600:300_um','Via[0-1]_650:300_um')
s=re.sub(r'(\(circle\s+\S+\s+)600(?=\s|\))',r'\g<1>650',s)
if '(padstack "Via[0-1]_500:200_um"' not in s:
 pos=s.index('(library')+len('(library')
 s=s[:pos]+'\n(padstack "Via[0-1]_500:200_um" (shape (circle F.Cu 500)) (shape (circle B.Cu 500)) (attach off))\n'+s[pos:]
 s=s.replace('(via "Via[0-1]_650:300_um"', '(via "Via[0-1]_500:200_um" "Via[0-1]_650:300_um"',1)
(root/'no_ground.dsn').write_text(s)
print('Prepared ground-pour routing seed; via 500:', 'padstack "Via[0-1]_500:200_um"' in s)
