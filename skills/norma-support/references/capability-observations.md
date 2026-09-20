# Arch Studio connector observations — September 13, 2026

Source: owner-supplied Arch Studio Test 01 session receipts and screenshots reviewed for the R5 support slice. This is Arch Studio's own acceptance evidence, with no customer files, names, file IDs or credentials bundled. It is **owner-reported**, not a fresh test performed by the current support session. The runs used Arch Studio 1.5.0 digest `sha256:bbdcaaf8f2877244b9f387f5ccccd44160290a90d23304054d492f43bf972594`. Different fixtures and available host capabilities prevent a host-wide ranking.

| Route | Supported observation | Remaining boundary |
|---|---|---|
| ChatGPT Work / native Google Docs and Sheets | Synthetic document and schedule created/read; cell corrections, recalculation, formulas, links and notes checked; images inserted through the native Sheets Drive picker and visually verified after reload. | This does not prove real customer extraction/template fidelity or that a connector API itself can insert native cell images. |
| Claude Cowork / local XLSX | Customer test copy corrected, PDFs produced, formulas/styles checked and two catalog images embedded locally. | Local workbook preview or a Drive button does not establish native Google writeback. |
| Claude Cowork / Google Drive connection | Corrected CSV imported as a new native Google Sheet and read back; formulas recalculated; images uploaded separately. | Existing-Sheet cell editing and in-cell images were not demonstrated. CSV import does not establish workbook-format or multi-tab preservation. |
| ChatGPT Work / Miro | Two native presentation frames with editable text and product images created and checked. | The tested account lacked the HTML slide-upload feature; this was a native-frame route. |
| Claude Cowork / Miro | Two product-specification frames created with text/layout. | Image transport failed; placeholders remained. The reported upload rejection is evidence for that environment, not proof that all Claude or Miro accounts block images. |
| ChatGPT Work / Figma | Two native editable slides with reused images and source/schedule links created, reread and visually checked. | Synthetic imagery was illustrative, not verified product photography. |
| Claude Cowork / Figma | Two editable auto-layout specification cards created; a failed clone operation was reported to roll back in that single attempt. | Image upload failed and placeholders remained. One observed rollback is not a guarantee that all failed writes are atomic. |
| Arch Studio packaged helper execution in the two Test 01 sessions | Workflows delivered instructions; host tools performed the work. | `as-run` was unavailable in those sessions. Mandatory packaged helper steps did not run. This does not mean the user's host-generated work failed or that Arch Studio never executes elsewhere. |

For a new request check the actual tools and destination. A Google Drive connector may expose different operations in different hosts; its name alone proves neither Sheets edits nor their absence. Test text writes, images, formulas, file creation and existing-file updates separately. Do not claim full Google/Miro/Figma parity across hosts from the observations above.

If upload fails, retain the exact sanitized route/status and leave the result partial. Do not make customer media public, route around network policy, broaden an allowlist or replace it with generated images without the relevant authorization. A private native picker may be a valid route when actually available and authorized; a missing route remains a useful support finding.
