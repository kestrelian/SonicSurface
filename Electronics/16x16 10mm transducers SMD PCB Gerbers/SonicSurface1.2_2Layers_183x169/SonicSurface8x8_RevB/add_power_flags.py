"""Mark externally supplied Rev B nets with PWR_FLAG symbols on each root sheet (ERC only)."""
from pathlib import Path
import re, uuid

ROOT = Path(__file__).resolve().parent
FLAGS = {
    'Array8x8_RevB': ['+3V3', 'VDRV', 'GND'],                       # supplied through J1 / J2
    'DualArray_Controller_RevB': ['GND', 'VINPUT_FUSED', 'IN_RTN', 'VDRV_SAFE'],
}

def uid():
    return str(uuid.uuid4())

for project, nets in FLAGS.items():
    f = ROOT / project / (project + '.kicad_sch')
    s = f.read_text()
    if '(lib_id "SS8:PWR_FLAG")' in s:
        print(project, 'already flagged'); continue
    assert '(symbol "SS8:PWR_FLAG"' in s, 'PWR_FLAG library symbol missing'
    root = re.search(r'\(uuid ([0-9a-f-]+)\)', s).group(1)
    extra = ''
    for i, net in enumerate(nets):
        x, y = 150 + 65 * i, 560; ref = f'#FLG0{i + 1}'
        extra += (f'(symbol (lib_id "SS8:PWR_FLAG") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (dnp no) '
                  f'(uuid {uid()}) (property "Reference" "{ref}" (at {x} {y - 5.08} 0) (effects (font (size 1 1)) (hide yes))) '
                  f'(property "Value" "External supply" (at {x} {y - 2.54} 0) (effects (font (size 1 1)))) (pin "1" (uuid {uid()})) '
                  f'(instances (project "{project}" (path "/{root}" (reference "{ref}") (unit 1)))))\n')
        extra += (f'(global_label "{net}" (shape passive) (at {x - 8.89} {y} 0) (effects (font (size 1 1)) (justify left)) '
                  f'(uuid {uid()}))\n')
    s = s.rstrip()[:-1] + extra + ')\n'
    f.write_text(s)
    print(project, 'flagged:', ', '.join(nets))
