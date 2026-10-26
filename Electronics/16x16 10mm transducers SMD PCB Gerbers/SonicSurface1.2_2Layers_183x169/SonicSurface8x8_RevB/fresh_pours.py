from pathlib import Path
import re
root=Path('SonicSurface8x8_RevB/Array8x8_RevB/authoring');s=(root/'routing_input.dsn').read_text()
def block(s,start):
 d=0
 for i in range(start,len(s)):
  if s[i]=='(':d+=1
  elif s[i]==')':
   d-=1
   if not d:return s[start:i+1]
for m in list(re.finditer(r'\(class Ground|\(net GND\s',s))[::-1]:
 v=block(s,m.start());s=s[:m.start()]+s[m.start()+len(v):]
m=s.index('(class Signals');v=block(s,m);s=s[:m]+v.replace('Via[0-1]_650:300_um','Via[0-1]_500:200_um').replace('(width 200)','(width 150)')+s[m+len(v):]
s=s.replace('(width 1000)','(width 600)').replace('(width 500)','(width 400)')
pos=s.index('(library')+len('(library');s=s[:pos]+'\n(padstack "Via[0-1]_500:200_um" (shape (circle F.Cu 500)) (shape (circle B.Cu 500)) (attach off))\n'+s[pos:]
s=s.replace('(via "Via[0-1]_650:300_um"','(via "Via[0-1]_500:200_um" "Via[0-1]_650:300_um"',1)
(root/'fresh_pours.dsn').write_text(s)
