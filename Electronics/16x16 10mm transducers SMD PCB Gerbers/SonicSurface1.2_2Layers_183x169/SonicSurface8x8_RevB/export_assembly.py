from pathlib import Path
import subprocess,csv
import pcbnew as p
root=Path(__file__).resolve().parent
cli='C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
for name in ['Array8x8_RevB','DualArray_Controller_RevB']:
 f=root/name;b=p.LoadBoard(str(f/(name+'.kicad_pcb')))
 with (f/'TEST_POINTS.csv').open('w',newline='') as out:
  wr=csv.writer(out);wr.writerow(['Reference','Net','X mm','Y mm','Side'])
  for fp in b.GetFootprints():
   if fp.GetReference().startswith('TP'):
    wr.writerow([fp.GetReference(),fp.GetValue(),p.ToMM(fp.GetPosition().x),p.ToMM(fp.GetPosition().y),'Back' if fp.IsFlipped() else 'Front'])
 subprocess.run([cli,'pcb','export','pos','--format','csv','--units','mm','-o',str(f/'PLACEMENT.csv'),str(f/(name+'.kicad_pcb'))],check=True)
 for side in ['F','B']:
  subprocess.run([cli,'pcb','export','svg','--layers',side+'.Fab,'+side+'.SilkS,Edge.Cuts','--sketch-pads-on-fab-layers','--fit-page-to-board','--exclude-drawing-sheet','--mode-single','-o',str(f/('ASSEMBLY_'+side+'.svg')),str(f/(name+'.kicad_pcb'))],check=True)
print('Placement drawings and test-point maps exported; no final checks run.')
