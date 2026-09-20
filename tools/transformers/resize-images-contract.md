# Native image resize presets

This owns `resize_images.resize` for MCP delivery. The host uses its available image decoding,
resampling, encoding and file tools. No Arch Studio executable, supplied implementation or installed
Pillow package is required. Existing native libraries are permissible tools. Follow the
[host contract](../../docs/host-harness-contract.md), [native mutation sequence](../../docs/workspace-model.md#native-mutation-sequence)
and [completion contract](../../docs/completion-reporting.md). These are Arch Studio-authored presets,
not claims about current external platform requirements. Background removal, source acquisition,
product records and image adoption are outside this operation.

## Inputs and exact membership

The input object has exactly `folder` (string path) and `modes` (nonempty array containing only
`web`, `social`, `slides`, `print`). Repeated modes apply once; process selected modes in that order.
Use the supplied authorized folder; one-off resizing needs no project. An alternative target,
filename or custom crop is a separately authorized workflow, not an undocumented argument here.

Establish actual source and output path boundaries, permissions and access metadata. Resolve any
folder alias explicitly; do not follow source/output symlinks or ancestor aliases into an unverified
scope. Do not change permissions to gain access. Inspect supported regular files non-recursively,
suffix case-insensitively `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff`, `.webp`; sort by full path in Unicode
scalar order. Preserve original bytes and access metadata and every unrelated entry. Invalid folder
or no supported files produces an explicit refusal/empty-input result before creating output folders.
A supported suffix does not establish decodable image content.

Keep each source's exact basename minus its final suffix as its stem. Before any public write:

- Refuse duplicate Unicode case-folded stems, even when extensions differ.
- Derive all selected destinations `<folder>/resized-<mode>/<stem>-<label>.<suffix>` from the table.
- Refuse any existing entry whose name begins with the **literal** `<stem>-` prefix in a selected
  output directory, not just the planned suffixes. Also inspect actual filesystem case/normalization
  equivalence so distinct names cannot alias. Source `[`/`?`/`*` characters are literal text, never
  glob syntax. This corrects the historical helper's glob-pattern collision bug while preserving
  its reserved prefix and no-overwrite rule.
- Existing matching files are reusable only through the proven exact-retry route below. Never
  silently rename, overwrite or adopt an unrelated existing result. A nondirectory target or an
  unresolved path/access conflict blocks before publication.

## Decode, frame and color

Fully decode each source's initially opened frame. Animated/multipage sources contribute only that
frame; report this scope. Do not silently process all frames or choose another frame. Keep `RGB`
and grayscale `L` pixel modes; convert all other modes, including RGBA, palette and CMYK, to `RGB`
before resizing. Conversion discards alpha; it is not a transparency-preserving output or a promised
matte-composite operation. Do not incorrectly claim WebP cannot support alpha.

Operate in decoded pixel orientation without implicitly applying EXIF orientation. The historical
helper applies no explicit orientation transpose, ICC color-management transform, metadata scrub,
or EXIF/ICC preservation. Establish and report the actual selected tool's behavior; do not invent
such guarantees. Inspect resulting orientation and visible colors/crops. Do not strip or alter
original metadata. Any requested color-management, orientation correction or privacy transformation
needs an explicit supported scope rather than an undocumented preset change.

Use LANCZOS resampling. Encoder quality values below identify the historical Pillow-style settings;
an available equivalent encoder must demonstrate their applicable mapping and actual output format,
not assume unrelated quality scales mean the same thing. Record method/version and actual settings.
A missing decoder/encoder or inability to meet selected precision is a capability gap, not permission
to install an Arch Studio dependency or substitute a different format. Compressed byte identity and
exact resampled pixel identity across codec implementations are not promised.

## Presets

All dimensions are pixels. Filename suffix and visible label are exact.

| Mode | Label | Geometry | Suffix / encoding |
|---|---|---|---|
| web | hero | maximum width 1920 | webp / WEBP quality 82 |
| web | standard | maximum width 1200 | webp / WEBP quality 82 |
| web | thumb | maximum width 400 | webp / WEBP quality 82 |
| social | social-square | center fill/crop 1080×1080 | webp / WEBP quality 85 |
| social | social-portrait | center fill/crop 1080×1350 | webp / WEBP quality 85 |
| social | social-landscape | center fill/crop 1200×675 | webp / WEBP quality 85 |
| social | social-linkedin | center fill/crop 1200×627 | webp / WEBP quality 85 |
| slides | slides-standard | center fill/crop 1024×768 | jpg / JPEG quality 92 |
| slides | slides-wide | center fill/crop 1920×1080 | jpg / JPEG quality 92 |
| print | arch-a | fit box 2700×3600 | jpg / JPEG quality 95, DPI 300×300 |
| print | arch-b | fit box 3600×5400 | jpg / JPEG quality 95, DPI 300×300 |
| print | arch-c | fit box 5400×7200 | jpg / JPEG quality 95, DPI 300×300 |

Let decoded positive integer size be `(w,h)`. Geometry arithmetic below uses exact integer/rational
values before rounding, not a floating approximation that changes a limiting edge. Extremely large
or unsupported dimensions remain a truthful native capability limit; do not truncate the input.

### Web: width only, no enlargement

For maximum width `m`, if `w <= m`, output `(w,h)`. Otherwise output
`(m, floor(h*m/w))`. A computed zero height is a source preparation failure; do not silently clamp it
to one pixel. There is no maximum height or longest-edge cap. Portraits can be taller than `m`.
Even a small source produces every requested preset-labelled file; no enlargement does not mean
no output. Exact rational arithmetic clarifies the intended truncation rather than preserving a
binary floating-point artifact at an integer boundary.

### Social and slides: centered fill, enlargement allowed

For target `(W,H)`, compare `W*h` with `H*w`. If `W*h >= H*w`, resize to
`(W, floor(h*W/w))`; otherwise resize to `(floor(w*H/h), H)`. Thus both dimensions cover the target.
Crop from `left=floor((resized_width-W)/2)`, `top=floor((resized_height-H)/2)` with exact final size
`(W,H)`. When excess is odd, remove the additional pixel at the right/bottom. No focal-point or
subject detection is implied; show material subject clipping. A user-selected crop is outside these
preset arguments.

This preserves the intended center-fill/truncation rule and explicitly corrects the old helper's
possible one-pixel undershoot from binary64 multiplication. Do not pad a target with an invented
black/transparent edge to reproduce that accident. The limiting edge equals its exact target.

### Print: fit the fixed box, no enlargement or rotation

For box `(W,H)`, keep `(w,h)` if both dimensions already fit. Otherwise compare `W*h` with `H*w`.
When `W*h >= H*w`, set height `H`; choose width from positive `floor(H*w/h)` and `ceil(H*w/h)`,
clamped to at least 1 and restricted to the box/source limits, minimizing the exact aspect error
`abs(w/h - candidate_width/H)`. Otherwise set width `W`; choose height from positive
`floor(W*h/w)` and `ceil(W*h/w)`, clamped to at least 1 and restricted to the box/source limits,
minimizing `abs(w/h - W/candidate_height)`. Break an exact tie toward the smaller candidate.
Compare rational errors exactly; zero is never a valid output dimension.

This makes the historical thumbnail's aspect-error rounding intent explicit without requiring one
Pillow release's floating-point implementation. Do not rotate the portrait-oriented box for a
landscape input, crop to fill it, or enlarge an already-fitting source. Resampling implementations
may have reduction optimizations; record the actual method, with no cross-encoder pixel/byte equality
claim. Write explicit 300×300 DPI in each print JPEG and verify its actual metadata; DPI tagging does
not create pixels or guarantee physical print quality.

## Prepare the complete batch before publication

Inspect and retain the exact selected intent, source membership/raw hashes/access and relevant
existing destination state. Establish the writer boundary and discoverable pending evidence. Before
its first public publisher, prepare the entire batch: decode/process each source independently;
fully prepare all requested derivatives for each successful source, plus any requested public
results/history/report. A preparation failure fails that source, omits **all** its derivatives from
the publication set and continues other sources. Preserve the failure evidence and truthful partial
batch result. This deliberately removes the old helper's half-written failed-source outputs.

Durably retain full originals where required for recovery and every complete prepared byte string,
intended destination and access metadata. Finish/close writes, then separately reopen and validate
all retained original/prepared bytes and metadata before publishing any batch member. Decode each
actual prepared image; verify exact dimensions, format, frame/color behavior and applicable DPI,
and inspect the actual images for relevant visible crop/orientation defects. A valid in-memory image,
unchecked write call or encoder success is insufficient. Private pending evidence is not a public
result. A requested public JSON or report needs the same complete preparation as its images.

Publish complete prepared files under guarded/no-clobber semantics; never expose a public pathname
and stream bytes into it. A race, interruption or failed publisher keeps the batch pending with exact
progress; stop new publication and reconcile under the same writer boundary. Do not erase successful
prior files or claim a completed batch. After publishing, reopen **all actual destinations**, verify
bytes/hash, decode and inspect geometry/format/DPI and actual access metadata, then recheck the full
source/protected set. Complete only after the entire applicable result/visual/custody review passes.

## Exact retry and reporting

Inspect pending state before any new preparation. Proven identical intent, source bytes/access,
selected output membership and retained prepared bytes can resume absent outputs or reuse actual
matching outputs without re-encoding, duplicate names or new history. An existing matching hash alone
is not evidence of prior authorized application. Changed source/preset/destination or an unrelated
third-state file is a conflict. Retain the original failures and source outcomes on a completed exact
retry; retrying a failed source with changed input is a new explicitly selected scope. No mandatory
Arch Studio request-ID, journal file format or record schema is introduced.

The compatible summary shape has exactly `results`, `succeeded`, `failed`, `workflow_completed`.
Each source result is `{source: absolute_path, status: "resized"}` or
`{source: absolute_path, status: "failed", error: text}`. Counts are source counts. Report `resized`
only after every derivative for that source has passed actual publication/readback checks. Preserve
`workflow_completed: false` in this historical mechanical summary; separately report actual workflow
completion/partial state and evidence through the completion contract. Do not retag old helper output
as whole-workflow acceptance. An invocation's process status, if applicable, is nonzero for any failure;
inline/native facilities report the equivalent truthful status without inventing a process.

List actual filenames, decoded dimensions and sizes in integer KiB (`bytes // 1024`), successful and
failed source counts, exact omitted outputs, error reasons and visual/metadata limitations. Bind
separate verification evidence to original and output raw SHA-256, actual codec/settings, frame/mode,
geometry, observed DPI/access and final full-set checks. Do not claim all requested outputs succeeded
when a source failed, and do not infer record registration or delivery from an image being written.
