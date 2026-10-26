from pathlib import Path
import re,shutil
import pcbnew as p
f=Path('SonicSurface8x8_RevB/Array8x8_RevB/authoring/work.kicad_pcb')
shutil.copyfile(f,f.with_name('before_ground_pours.kicad_pcb'))
b=p.LoadBoard(str(f));n=b.FindNet('GND').GetNetCode();s=f.read_text();count=0
for m in list(re.finditer(r'\((?:segment|via)\s',s))[::-1]:
 start=m.start();depth=0
 for i in range(start,len(s)):
  if s[i]=='(':depth+=1
  elif s[i]==')':
   depth-=1
   if not depth:break
 block=s[start:i+1]
 if '(net "GND")' in block:s=s[:start]+s[i+1:];count+=1
f.write_text(s)
print('Replaced',count,'ground trace/via items with planned ground pours.')
f=Path('SonicSurface8x8_RevB/finish_copper_smart.py');s=f.read_text().replace("if len(pads)<2:continue","if len(pads)<2 or b.FindNet(n).GetNetname()=='GND':continue").replace('choices[:6]','choices[:3]');f.write_text(s)
