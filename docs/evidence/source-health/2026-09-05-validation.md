# Source foundation validation — 2026-09-05

- Implementation: [source checker](../../../tools/integrations/source-health.mjs), Node.js built-ins.
- Offline check: `node tools/integrations/source-health.mjs --validate` passed for three sources.
- Deterministic check: `bash tests/test-source-contracts.sh` passed 12 tests under Node.js v25.9.0.
- Cases: malformed/missing fields, unknown edition preservation, credential-bearing URLs, duplicate/dangling IDs, jurisdiction cycle, synthetic second jurisdiction sharing one standard, identity markers, login pages, redirects to private addresses, changed identity, content-type/byte caps, access denial, outage, abort timeout, error-message redaction, concurrency isolation, unknown source IDs and early-response cancellation.
- Initial live attempt at 2026-09-05T16:04:11Z in the restricted network sandbox returned `transport-error`, reachability/identity unknown, for all three maintained sources. This is environment-limited evidence, not publisher failure or a passed identity check.
- No hosted binding, scheduled service, new city/legal resolver, live EC3 integration, or project-record write was tested or implemented.

Outside-sandbox check at 2026-09-05T16:05:18Z returned HTTP 200 with matched markers for Zoning Resolution (SHA-256 `7c83f3652a4c3d7839d7e2ddf4f469ef71494e69ceec5076948b6fc3741cc632`) and PLUTO (`f4c5ad1ab79d731cbe2dca09042648e650df1f5d875b313ad74c17f8e6e522b7`). The initial construction index URL returned 404. The maintained entry was corrected using the official [DOB Codes page](https://www.nyc.gov/site/buildings/codes/codes.page), found in official NYC search results; a fresh checker receipt for that corrected URL follows separately. None of these checks determines applicable law, edition, or freshness.

Repaired construction index checked at 2026-09-05T16:08:26.404Z: HTTP 200, identity `matched-markers`, content SHA-256 `7a8f43115d83f8f8c1d308d1f37931701c255abd84ded854ea79316c56aad3b7`. All three maintained endpoints have a successful bounded live identity receipt in this session. The receipts are observations at those timestamps, not continuing health guarantees.
