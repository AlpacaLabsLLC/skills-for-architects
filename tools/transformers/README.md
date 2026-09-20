# FF&E intake

For document-bound PDF evidence, explicit dimension normalization, drawing instance ledgers,
quantity comparisons and delivery coverage, see the [native evidence contracts](evidence-contracts.md).
These bounded procedures do not replace host extraction judgment or visual verification.

`ffe_intake.py` creates an accepted job input manifest from explicit source files or host-captured URL observations. It verifies available local bytes, pinned adopted record references and unique selected tags; corrections create a new job linked to the previous one. It never adopts a schedule or replaces an existing manifest.

Hosted intake workflows follow this contract natively with the host's own tools; no Arch Studio runner or package is required. `ffe_intake.py` is a retained maintainer reference implementation and test oracle, and its CLI flags below describe implementation semantics for development. See [input schema](../../schema/ffe-intake.schema.json). Source paths are project-relative; authenticated retrieval belongs to the host. Output template dependencies are resolved separately by the output workflow.

Intake and output preparation share [product_identity.py](product_identity.py), which imports the
package-relative [identity schema](../../schema/product-identity.schema.json). The release keeps both at the same digest and relative paths as reference material; never reconstruct them from conversation. Exact product IDs allow 1–80 ASCII letters,
digits, dots, underscores and hyphens, starting with a letter or digit. Ordinary dotted tags remain
unchanged. Job IDs retain their existing separate dot-free rule. Filename mapping belongs to the
[versioned output contract](../renderers/README.md#product-identity-and-filenames), never canonical retagging.

Every source must explicitly contain `sha256`. Null is allowed for an available file because intake
hashes its actual bytes, and for an unavailable source as an explicit unknown. An available URL
requires a host-captured hash. Missing, invalid and mismatched hashes identify the source index/field;
they do not become verified provenance. An unsuccessful intake publishes no partial job manifest.

For standalone sample outputs, use `--workspace <existing-authorized-task-folder> --input <request.json>` instead. Only `one-off` mode with a null record basis is permitted. Paths and `ffe/jobs/` are relative to that task folder; no PROJECT.md or studio registration is created. Source checks, create-only publication, correction lineage and overwrite refusal are identical. This flag does not authorize access or library/adopted-record writes.
