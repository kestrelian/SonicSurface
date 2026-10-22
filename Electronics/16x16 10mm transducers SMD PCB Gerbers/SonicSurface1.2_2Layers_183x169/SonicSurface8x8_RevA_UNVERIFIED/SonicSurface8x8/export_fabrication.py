"""Export fabrication drawings without running any final verification checks."""
from pathlib import Path
import pcbnew as p
import sys
ROOT=Path(__file__).resolve().parent
for name in (sys.argv[1:] or ['Array8x8','CoreEP4CE6_Adapter']):
    folder=ROOT/name;out=folder/'fabrication_UNVERIFIED';out.mkdir(exist_ok=True)
    b=p.LoadBoard(str(folder/(name+'.kicad_pcb')))
    plot=p.PLOT_CONTROLLER(b);opts=plot.GetPlotOptions();opts.SetOutputDirectory(str(out))
    opts.SetPlotFrameRef(False);opts.SetPlotValue(False);opts.SetPlotReference(True);opts.SetSubtractMaskFromSilk(True)
    opts.SetUseGerberX2format(True);opts.SetIncludeGerberNetlistInfo(True);opts.SetCreateGerberJobFile(True)
    for layer,suffix in [(p.F_Cu,'F_Cu'),(p.B_Cu,'B_Cu'),(p.F_Mask,'F_Mask'),(p.B_Mask,'B_Mask'),(p.F_Paste,'F_Paste'),(p.B_Paste,'B_Paste'),(p.F_SilkS,'F_SilkS'),(p.B_SilkS,'B_SilkS'),(p.Edge_Cuts,'Edge_Cuts')]:
        plot.SetLayer(layer);plot.OpenPlotfile(suffix,p.PLOT_FORMAT_GERBER,'REV A UNVERIFIED - final checks deferred');plot.PlotLayer()
    plot.ClosePlot()
    drill=p.EXCELLON_WRITER(b);drill.SetFormat(True);drill.SetOptions(False,False,p.VECTOR2I(0,0),False);drill.CreateDrillandMapFilesSet(str(out),True,False)
    (out/'READ_BEFORE_FABRICATION.txt').write_text('UNVERIFIED REV A. Final ERC, DRC, Gerber review, drill review and manufacturing QA have NOT been executed. These files are design exports, not a fabrication release. Read ../../QA_CHECKLIST.md and ../../DESIGN_NOTES.md before use.\n')
    print('Exported',name,flush=True)
