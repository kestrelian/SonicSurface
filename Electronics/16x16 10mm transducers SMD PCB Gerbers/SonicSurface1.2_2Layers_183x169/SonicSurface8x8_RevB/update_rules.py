from pathlib import Path
f=Path('SonicSurface8x8_RevB/update_exports.py');s=f.read_text();s='\n'.join(line for line in s.splitlines() if not line.startswith("f=root/'export_fabrication.py'"));s=s.replace("r=d['board']['design_settings']['rules']","r=d.setdefault('board',{}).setdefault('design_settings',{}).setdefault('rules',{})");f.write_text(s)
