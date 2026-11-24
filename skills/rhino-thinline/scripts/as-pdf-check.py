#! python3
"""Read a PDF's contents and check that it is the black and white sheet it should be (Arch Studio, as-rhino-thinline).

A PDF cannot be judged by looking at it from the panel, so this parses the file. An empty parse
is a failure, not a pass: when no colour operators are found, the parser did not read the page.

Runs by file path through run_python, with the standard library only:

    P = "<absolute path of this skill's folder>/scripts/as-pdf-check.py"
    exec(compile(open(P).read(), P, "exec"), {"AS_SCRIPT_FILE": P, "AS_PDF": "/abs/sheet.pdf", "AS_PDF_SIZE": [914.4, 609.6]})

AS_PDF_SIZE is the expected page in mm. AS_PDF_PAGES defaults to 1. Prints each measurement and ends with
ASPDF status=pass|fail. Colours are written as RGB (Rhino uses SC and sc after /DeviceRGB CS), as
gray, or as CMYK; all of these count.
"""
import os
import re
import zlib

STREAM = re.compile(rb"stream\r?\n(.*?)\r?\n?endstream", re.S)
PT_MM = 25.4 / 72.0
COLOUR = {b"rg", b"RG", b"g", b"G", b"k", b"K", b"sc", b"SC", b"scn", b"SCN"}
NUM = re.compile(rb"[-+]?(?:\d+\.\d*|\.\d+|\d+)$")
NOT_CONTENT = re.compile(rb"/Type\s*/(?:ObjStm|XRef|Metadata)|/Subtype\s*/Image|/Length1|/Subtype\s*/(?:Type1C|CIDFontType0C|OpenType)")
TOKEN = re.compile(rb"\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]*>|/[^\s/\[\]<>()]+|[-+]?(?:\d+\.\d*|\.\d+|\d+)|[A-Za-z'\"*]+\d?\*?|\[|\]|<<|>>")


def _is_black_or_white(values):
    """Each colour as gray, RGB or CMYK; a tolerance covers rounding in the writer."""
    tol = 0.002
    if len(values) == 1:
        return values[0] <= tol or values[0] >= 1 - tol
    if len(values) == 3:
        return all(v <= tol for v in values) or all(v >= 1 - tol for v in values)
    if len(values) == 4:
        return (all(v <= tol for v in values[:3]) and (values[3] >= 1 - tol or values[3] <= tol))
    return False


def _flate(data):
    """Inflate a stream. decompressobj, not decompress: the stream pattern drops a trailing CR or LF before
    endstream, and when the deflated data itself ends in one, decompress fails and the raw bytes would be
    read as page content."""
    try:
        return zlib.decompressobj().decompress(data) or None
    except zlib.error:
        return None


def streams(raw):
    """Every stream in the file with its dictionary, decompressed when it is deflated."""
    out = []
    for match in STREAM.finditer(raw):
        start = raw.rfind(b"obj", 0, match.start())
        body = match.group(1)
        out.append((raw[start:match.start()], _flate(body) or body))
    return out


def scan(content, widths, colours):
    """Track the graphics state through one content stream, recording line widths in mm and colours."""
    ops = found = 0
    matrix = (1.0, 0.0, 0.0, 1.0)
    stack = []
    args = []
    width = 1.0
    for tok in TOKEN.findall(re.sub(rb"%[^\r\n]*", b"", content)):
        if tok[:1] in b"(</[]" or tok in (b"<<", b">>"):
            continue
        if NUM.match(tok):
            args.append(float(tok))
            continue
        ops += 1
        scale = abs(matrix[0] * matrix[3] - matrix[1] * matrix[2]) ** 0.5
        if tok == b"q":
            stack.append((matrix, width))
        elif tok == b"Q" and stack:
            matrix, width = stack.pop()
        elif tok == b"cm" and len(args) >= 6:
            a, b, c, d = args[-6:-2]
            m = matrix
            matrix = (a * m[0] + b * m[2], a * m[1] + b * m[3], c * m[0] + d * m[2], c * m[1] + d * m[3])
        elif tok == b"w" and args:
            width = args[-1]
        elif tok in COLOUR and args:
            colours.append(tuple(args[-{b"g": 1, b"G": 1, b"rg": 3, b"RG": 3, b"k": 4, b"K": 4}.get(tok, len(args)):]))
            found += 1
        elif tok in (b"S", b"s", b"B", b"B*", b"b", b"b*"):
            widths.add(round(max(width * scale, 0.0) * PT_MM, 3))
        args = []
    return ops, found


def analyse(raw):
    """The measurements of a PDF's bytes. Streams are read both as page content and as object streams."""
    data = streams(raw)
    text = raw + b"\n" + b"\n".join(body for head, body in data if re.search(rb"/Type\s*/ObjStm", head))
    pages = len(re.findall(rb"/Type\s*/Page(?![A-Za-z])", text))
    boxes = [tuple(float(v) for v in m) for m in re.findall(rb"/MediaBox\s*\[\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)", text)]
    images = len(re.findall(rb"/Subtype\s*/Image", text))
    widths, colours = set(), []
    content, operators = 0, 0
    for head, body in data:
        if NOT_CONTENT.search(head):
            continue
        ops, _found = scan(body, widths, colours)
        if ops:
            content += 1
            operators += ops
    return {"pages": pages, "media_boxes": boxes, "images": images, "content_streams": content, "operators": operators,
            "colours": sorted(set(colours)), "colour_ops": len(colours), "line_widths_mm": sorted(widths)}


def check(raw, size_mm=None, pages=1, size_tol_mm=1.0):
    """Failures for a PDF's bytes. Empty when it is one page of the right size, in black and white, with no images."""
    m = analyse(raw)
    failures = []
    if m["pages"] != pages:
        failures.append("%d pages, expected %d" % (m["pages"], pages))
    if not m["media_boxes"]:
        failures.append("no MediaBox found")
    elif size_mm:
        x0, y0, x1, y1 = m["media_boxes"][0]
        w, h = sorted([(x1 - x0) * PT_MM, (y1 - y0) * PT_MM])
        want = sorted(size_mm)
        if abs(w - want[0]) > size_tol_mm or abs(h - want[1]) > size_tol_mm:
            failures.append("page is %.1f x %.1f mm, expected %.1f x %.1f" % (w, h, want[0], want[1]))
    if m["images"]:
        failures.append("%d raster images; a vector sheet has none" % m["images"])
    if not m["content_streams"]:
        failures.append("no page content was read: the check cannot say anything about this file")
    if not m["colour_ops"]:
        failures.append("no colour operators were found: the parser did not read this file, so this is not a pass")
    unreadable = [c for c in m["colours"] if any(v < 0 or v > 1 for v in c)]
    if unreadable:
        failures.append("%d colour values outside 0 to 1, such as %s: the content was not read as page content" % (len(unreadable), unreadable[:3]))
    bad = [c for c in m["colours"] if not _is_black_or_white(c) and c not in unreadable]
    if bad:
        failures.append("%d colours that are not black or white, such as %s" % (len(bad), bad[:3]))
    if not m["line_widths_mm"]:
        failures.append("no stroked lines were found")
    return m, failures


def main():
    path = globals()["AS_PDF"]
    size = globals().get("AS_PDF_SIZE")
    with open(path, "rb") as handle:
        raw = handle.read()
    m, failures = check(raw, size, int(globals().get("AS_PDF_PAGES", 1)))
    print("  %s, %.0f KB" % (os.path.basename(path), len(raw) / 1024.0))
    print("  pages %d; media box %s; images %d; content streams %d; operators %d" % (m["pages"], m["media_boxes"][:1], m["images"], m["content_streams"], m["operators"]))
    print("  colours %d operators, %d distinct: %s" % (m["colour_ops"], len(m["colours"]), m["colours"][:6]))
    print("  line widths mm: %s" % m["line_widths_mm"][:20])
    for failure in failures:
        print("  FAIL: " + failure)
    print("ASPDF status=%s failures=%d" % ("fail" if failures else "pass", len(failures)))


if "AS_PDF" in globals():
    main()
