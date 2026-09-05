# FF&E intake

`ffe_intake.py` creates an accepted job input manifest from explicit source files or host-captured URL observations. It verifies available local bytes, pinned adopted record references and unique selected tags; corrections create a new job linked to the previous one. It never adopts a schedule or replaces an existing manifest.

Run with Python 3.10+ using `--project <resolved-project> --input <request.json>`. See [input schema](../../schema/ffe-intake.schema.json). Source paths are project-relative; authenticated retrieval belongs to the host. Output template dependencies are resolved separately by the output workflow.
