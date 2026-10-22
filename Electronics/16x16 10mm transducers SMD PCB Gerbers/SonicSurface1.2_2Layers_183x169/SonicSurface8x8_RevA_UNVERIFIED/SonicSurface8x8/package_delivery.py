"""Group the generated BOM and package files. Does not perform PCB QA."""
from pathlib import Path
import csv,collections,zipfile
root=Path(__file__).resolve().parent
for name in ['Array8x8','CoreEP4CE6_Adapter']:
    groups=collections.defaultdict(list)
    with (root/name/'BOM.csv').open() as f:
        for row in csv.DictReader(f):groups[(row['Value / part'],row['Footprint'])].append(row['Reference'])
    with (root/name/'BOM_grouped.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['Quantity','Value / part','Footprint','References'])
        for (value,fp),refs in groups.items():writer.writerow([len(refs),value,fp,', '.join(refs)])
archive=root.parent/'SonicSurface8x8_RevA_UNVERIFIED.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in sorted(root.rglob('*')):
        rel=path.relative_to(root)
        if not path.is_file() or any(x in rel.parts for x in ['tools','__pycache__']):continue
        z.write(path,Path(root.name)/rel)
print(archive)
print('Archive bytes:',archive.stat().st_size)
