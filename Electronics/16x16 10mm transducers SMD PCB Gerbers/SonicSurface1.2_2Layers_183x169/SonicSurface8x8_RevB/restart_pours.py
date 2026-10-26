from pathlib import Path
import shutil
import pcbnew as p
f=Path('SonicSurface8x8_RevB/Array8x8_RevB/authoring');shutil.copyfile(f/'work.kicad_pcb',f/'manual_connections_backup.kicad_pcb')
b=p.LoadBoard(str(f/'placed.kicad_pcb'));assert p.ImportSpecctraSES(b,str(f/'routed.ses'));p.SaveBoard(str(f/'work.kicad_pcb'),b)
s=Path('SonicSurface8x8_RevB/route_with_pours.py').read_text();s=s.replace("(root/'no_ground.dsn').write_text(s)",'''if '(padstack "Via[0-1]_500:200_um"' not in s:
 pos=s.index('(library')+len('(library')
 s=s[:pos]+'\\n(padstack "Via[0-1]_500:200_um" (shape (circle F.Cu 500)) (shape (circle B.Cu 500)) (attach off))\\n'+s[pos:]
 s=s.replace('(via "Via[0-1]_650:300_um"', '(via "Via[0-1]_500:200_um" "Via[0-1]_650:300_um"',1)
(root/'no_ground.dsn').write_text(s)''');Path('SonicSurface8x8_RevB/route_with_pours.py').write_text(s)
