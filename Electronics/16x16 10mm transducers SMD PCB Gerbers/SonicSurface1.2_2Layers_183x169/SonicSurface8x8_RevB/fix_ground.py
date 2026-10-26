from pathlib import Path
f=Path('SonicSurface8x8_RevB/ground_pours.py');s=f.read_text().replace("if re.search(r'\\(net\\s+'+str(n)+r'\\)',block):", "if '(net \"GND\")' in block:")
f.write_text(s)
