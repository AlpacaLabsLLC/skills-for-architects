# Local operation package

Arch Studio installs executable bytes directly to disk. Instruction/resource retrieval does not install or execute a helper. The package includes the operation registry, implementation modules, imports, schemas, templates and locked runtime declarations. It accepts one named operation and a closed JSON input, never a shell command or model-authored helper source.

## Build and install

Export the reviewed immutable Git commit first; package.py rejects an active checkout. The caller records the exact commit and, when available, the independently established hosted source digest. Build outside the export:

```sh
python3 tools/runner/package.py --root /path/to/clean-export --source-commit FULL_COMMIT --output /path/to/as-package.zip
```

The result names the archive SHA-256 and the runner `release_digest`. The latter hashes the manifest containing every packaged file hash. A hosted `source_digest`, source commit and runner package digest are distinct identities; `as-package.json` records their mapping. Never substitute one for another.

From the downloaded/extracted release, install on Mac:

```sh
sh tools/runner/bootstrap.sh --package /path/to/as-package.zip --sha256 ARCHIVE_SHA256 --destination /path/to/as-installations
```

On Windows, run the shipped PowerShell entry point:

```powershell
& .\tools\runner\bootstrap.ps1 -Package C:\path\as-package.zip -Sha256 ARCHIVE_SHA256 -Destination C:\path\as-installations
```

Bootstrap verifies a pinned uv binary and acquires managed Python 3.13.7. Installation verifies the archive and every package file, installs the exact `uv.lock` dependency resolution, and downloads checksum-pinned Node 24.14.1. PyMuPDF supplies PDF text/metadata and pypdf checks physical page boxes. Retained local operations require no Poppler or Bash runtime. The shell entry point only bootstraps a Mac installation; Windows uses PowerShell.

Each release installs into its own digest directory. The installer returns that directory and its manifest. An existing matching installation is reused; active jobs keep their original path/pin. A failed new installation removes only its incomplete directory. Selecting an earlier retained installation is package rollback; it never rolls back user documents. No historical data converter is included. Installation needs network access to the declared official download/package sources; execution does not acquire code or dependencies.

## Invoke

The installation generates `as-run` on Mac or `as-run.cmd` on Windows. Invoke its full installed path:

```sh
/path/to/installation/as-run --request request.json
```

```json
{
  "schema_version": 1,
  "operation": "dimension_values.normalize",
  "release_digest": "sha256:PIN_FROM_AS_PACKAGE_MANIFEST",
  "input": {
    "data": {"raw": "24 inches wide", "axes": {"W": 24}, "unit": "in", "meaning": "overall"},
    "unit": "mm"
  }
}
```

The [registry](operations.json) and its document-operation include own each operation's input schema, effects, dependencies and fixture references. Paths inside task inputs are explicit authorized user paths; they do not resolve a new studio implicitly. Existing helper CLIs remain internal implementation interfaces where still used by current tests/callers. Their closed adapters expose structured JSON without rewriting functioning computations.

The runner checks the package and operation dependencies before dispatch. Unknown operations, missing/altered files, wrong runtime, malformed input, child timeout and parse failures produce JSON errors. Request/result limits are 4 MiB; child CLI execution is bounded to 120 seconds. Operation-owned failure details and partial results are retained. The dispatcher is not an operating-system sandbox or a capability grant; the invoking host must supply the authorized destination and operation scope.

`status: ok` means the named operation returned normally. Inspect the domain result: a successful comparison can report violations or incomplete membership. `workflow_completed` stays false. A PDF mechanical pass cannot independently certify manufacturer facts or visual inspection; the receipt preserves source status, unresolved specifications and whether visual evidence was host-reported.

## Local desktop adapter

Installation produces `desktop-mcp.json` with an exact managed Python path, `desktop.py`, package manifest and installation environment. A desktop host with a local stdio MCP launch facility can use that entry. The adapter uses the pinned [official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), exposes only `as_execute_operation`, and invokes the same package contract. It does not expose HTTP, a remote filesystem or shared memory. Review the host's actual configuration facility before registering it; configuration is not proof that a target host can execute or access a particular file.

Four OS/mode targets remain Mac CLI, Mac desktop, Windows CLI and Windows desktop. Unit and local stdio fixture results are engineering evidence only. Final W10 must identify actual products/versions, run through each actual route after complete implementation, and record tested, untested and unsupported paths separately. Missing local process/file access is a concrete target gap; a hosted Arch Studio connection is not a substitute. This package does not claim actual-host acceptance.

The optional `assistant_preference.preview/apply` helper retains POSIX no-follow write protection and is explicitly unsupported on Windows. The runner refuses it before task writes. A Windows host may perform a separately reviewed native preference edit only when it exposes the needed file operation and existing user authorization covers the exact change. No fallback runs automatically. This exception does not remove Windows cut-sheet/setup execution from final acceptance.

## Checks

Run `tools/runner/lint.py`, `tests/test-local-runner.py`, current document-library tests and the affected existing helper suites with the managed Python environment. The [fixture index](fixtures/operations.json) links every retained operation to its contract and behavior evidence; lint checks coverage but does not certify execution. Source-health fixtures inject transport and time instead of treating live pages as deterministic. All fixtures use synthetic or isolated files. Final real-host cut-sheet prepare/check acceptance runs last.
