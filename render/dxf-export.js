// QCAD "Print to PDF" exporter.
//
// API is "documented" at e.g. https://www.qcad.org/doc/qcad/latest/developer/class_print.html

include("scripts/Tools/arguments.js");
include("scripts/File/Print/Print.js");

var firstStderr = true;

// Print msg to stderr, bypassing QT_LOGGING_RULES.
function stderr(msg) {
  var f = new QFile("/dev/stderr");
  f.open(QIODeviceBase.WriteOnly | QIODeviceBase.Text);
  if (firstStderr) {
    f.write("\n\n"); // Separate our output from any QT console spam.
    firstStderr = false;
  }
  f.write(msg + "\n");
  f.close();
}

// Terminate the enclosing qcad instance with a non-zero exit code
// after printing a message.
function fatal(msg) {
  stderr("FATAL: " + msg);
  stderr(new Error().stack);
  stderr("\n\n") // Extra newlines to separate from QCad death throes.
  var p = new QProcess();
  p.start("/bin/bash", ["-c", "kill -ABRT " + QCoreApplication.applicationPid()]);
  p.waitForFinished(5000); // Likely unreachable.
}

function absolutePathFor(path) { // Necessary because qcad changes CWD to /opt/qcad during runtime(!).
  if (!path) fatal("missing path: " + path);
  if (!new QFileInfo(path).isAbsolute()) {
    path = RSettings.getLaunchPath() + QDir.separator + path;
  }
  return path;  
}

// Redirect embedded image references to clipart directory.
// Return true on success.
function repointToClipart(di, document, clipartDir) {
  var op = new RModifyObjectsOperation();
  document.queryAllEntities().forEach(id => {
    var ent = document.queryEntity(id);
    if (ent.getType() !== RS.EntityImage) return;
    if (document.queryLayer(ent.getLayerId()).isFrozen()) return;
    var ref = ent.getData().getFileName();
    var baseName = new QFileInfo(ref).fileName();
    var candidate = clipartDir + QDir.separator + baseName;
    if (!new QFileInfo(candidate).exists()) {
      fatal("ERROR: clipart NOT FOUND: " + baseName + " in " + clipartDir + "; (referenced as " + ref + ")");
    }
    ent.setFileName(candidate);
    op.addObject(ent, false);
  });
  di.applyOperation(op);
}

// Freeze/thaw layers based on --layers flag. Return true on success.
function selectLayers(di, document, layerNames) {
  var op = new RModifyObjectsOperation();
  document.queryAllLayers().forEach(id => {
    const layer = document.queryLayer(id);
    const name = layer.getName();
    layer.setFrozen(layerNames.indexOf(name) == -1);
    op.addObject(layer);
    layerNames = layerNames.filter(n => { return n !== name; });
  });
  if (layerNames.length) {
    fatal("\n\nSpecified layer(s) not found: " + layerNames);
  }
  di.applyOperation(op);
}

function cropToContents(di, document) {
  // Set the output page size to the size of the contents (to avoid
  // whitespace margins) plus a tiny margin to account for any ink
  // bleed outside the geometric bounding box due to antialiasing etc.
  var margin = 5;
  var bb = document.getBoundingBox(true, true);
  var bw = bb.getWidth() + margin;
  var bh = bb.getHeight() + margin;
  var bmin = bb.getMinimum();
  var scale = Print.getScale(document);
  var paperWIn = bw * scale;
  var paperHIn = bh * scale;
  Print.setValue("UnitSettings/PaperUnit", document.getUnit(), di);
  Print.setValue("PageSettings/PaperWidth", paperWIn, di);
  Print.setValue("PageSettings/PaperHeight", paperHIn, di);
  Print.setOffset(di, new RVector(bmin.x - margin/2, bmin.y - margin/2));
}

function load(inFile) {
  var document = new RDocument(new RMemoryStorage(), new RSpatialIndexSimple());
  var di = new RDocumentInterface(document);
  if (di.importFile(inFile) !== RDocumentInterface.IoErrorNoError) {
    fatal("Failed to import " + inFile);
  }
  return {di, document};
}

function showUsage() {
  stderr("\n\nUsage: qcad -platform offscreen -no-gui -allow-multiple-instances -autostart export.js -f -o out.pdf --layers=A,B --clipart path/to/dir in.dxf");
}

function printToPDF(di, document, outFile) {
  var view = new RGraphicsViewImage();
  view.setScene(new RGraphicsSceneQt(di));
  var pp = new Print(undefined, document, view);
  pp.print(outFile);
}

function main() {
  if (testArgument(args, "-h", "--help")) { showUsage(); return; }
  const { di, document } = load(absolutePathFor(args[args.length - 1]));

  var layersArg = getArgument(args, "-l", "--layers");
  if (!layersArg) {
    showUsage();
    fatal("No layers specified. Use --layers=LayerA,LayerB,etc\nFound layers:\n" +
      document.queryAllLayers().map(id => { return document.queryLayer(id).getName(); }).sort().join("\n") + "\n");
  }
  selectLayers(di, document, layersArg.split(","));

  var clipartDir = getArgument(args, "-c", "--clipart");
  if (!clipartDir) { showUsage(); fatal("Missing arg --clipart"); }
  clipartDir = absolutePathFor(clipartDir);
  repointToClipart(di, document, clipartDir);

  cropToContents(di, document);

  var outfileArg = getArgument(args, "-o", "-outfile");
  if (!outfileArg) { showUsage(); fatal("Missing arg --output"); }
  printToPDF(di, document, absolutePathFor(outfileArg));
}

main();
