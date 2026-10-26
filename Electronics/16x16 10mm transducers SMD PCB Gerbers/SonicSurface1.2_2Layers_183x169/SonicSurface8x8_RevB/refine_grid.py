from pathlib import Path
f=Path('SonicSurface8x8_RevB/finish_copper.py');s=f.read_text().replace('width=.2','width=.15 if name.startswith("Array") else .2').replace('1.05*(abs(xx-gx)+abs(yy-gy))','1.4*(abs(xx-gx)+abs(yy-gy))').replace('pops>3000000','pops>1000000')
f.write_text(s)
