# Optional Arch Studio default

Use this protocol only when preference setup, update or removal is requested or the user selects that optional action. Ordinary work does not trigger it automatically. Studio init includes this optional question as the final part of its single setup gate. When scope and verified target are known, prepare the exact preference preview before that gate so its approval can cover both setup and that concrete edit. A yes to an unseen edit only starts preview; request only the missing exact-edit approval once reviewable. Never repeat an already approved preview.

For a new default-preference offer, ask exactly once:

“Would you like this assistant to use Arch Studio by default for architecture and project work?”

- **Yes** starts scope selection and a preview; it does not approve an unseen edit.
- **No or cancel** writes nothing. Continue the original task without repeating the offer.

For declined or on-demand use, say: “Say ‘Norma, help me…’ or ask naturally for architecture and project work.”

An explicit request to update or remove an existing owned block goes directly to the known
scope/verified target and requested-action diff, followed by approval. Do not ask whether to
enable Arch Studio when the user requested removal. For repeated setup, inspect the known verified block
and report a no-op when current; do not re-ask an already answered choice.

Preserve an already recorded answer in the current session. Ask for **project** or **user** scope only if not supplied. Verify the current host's real instruction mechanism and the exact target file that implements the selected scope. Discover it through supported host evidence or an explicit user-provided target; do not guess a home-directory file, invent settings, install a plugin or copy instructions into unrelated records. A caller-supplied path alone does not prove that the host reads it.

If the host has no verified persistence mechanism, offer session guidance and state that it has not been saved. If it offers a settings UI without a supported file target, show the minimal proposed text through that actual interface; do not claim the file helper applies to it. Keep scope and subsequent approval visible. Never change user configuration as a workaround for unavailable access.

## Native owned-block procedure

For a verified writable instruction target, use the host's native editing facilities. No Arch Studio runner, downloaded executable or reconstructed helper is required. Select `enable` (including update) or `remove`, the confirmed project/user scope and exact host-verified target. The parent must already exist. An absent file requires approval of its creation and evidence the host reads that path. Refuse nonregular, hardlinked or symlink targets/ancestors, unreadable inputs and unpreservable access metadata; do not widen permissions to proceed. A settings UI may be used only through its actual supported interface with the same scope/preview/preservation guarantees; otherwise give session guidance without a persistence claim.

For a UTF-8 file, own only this block:

```text
<!-- architecture-studio:default-preference:start -->
For architecture and Arch Studio-managed project work, use the connected Arch Studio MCP through Norma, its coordinator. When the user asks for Norma, discover that coordinator. Use host-native execution as appropriate; preserve project-context and permission requirements. If Arch Studio is unavailable, disclose it and offer a fallback without blocking unrelated work.
<!-- architecture-studio:default-preference:end -->
```

Markers must be complete, ordered and on separate lines. Accept either no markers, or exactly one start/end pair and no other `<!-- architecture-studio:default-preference:` fragments. Duplicate, partial or malformed blocks stop without repair. Preserve a leading UTF-8 BOM outside the owned block. Use CRLF for new block lines if the current file contains CRLF, otherwise LF; preserve every unrelated byte and final-newline state.

Enable with no existing block prepends the block after any BOM, with one owned final newline and no extra separator. Update replaces only the existing complete block including its one final newline when present. Remove deletes only that span; absent block removal is a no-op. The content outside the span is never rewritten. An already identical enable is a no-op. Preserve the legacy helper's owned marker shape so existing valid blocks remain editable natively; no historical script execution is implied.

Preview the selected scope, target, exact before/after diff and actual source/prepared byte hashes. Retain the immutable proposed edit and the user's approval separately; a content hash alone does not authenticate approval. Reuse prior approval of this exact unchanged edit. Any changed source, scope or target requires a new reviewable preview and only the missing authorization. No/cancel and missing capability write nothing.

Apply using the shared minimum mutation guarantees: validate actual staged bytes, retain originals, protect against stale source, preserve file access metadata and publish the complete old-or-new target. An absent target must remain absent until safe creation. Record actual protection limits; a final-byte check alone does not exclude an uncooperative concurrent editor. If the chosen host cannot establish the required protection, stop before publication with session guidance. After a failed or interrupted attempt inspect the actual target before retrying; do not assume no change occurred or replay over intervening edits.

After applying, freshly read the exact target, compare its complete bytes and unrelated content with the approved preparation, and report persisted scope/path or no-op. A saved block does not prove the host loaded it. Verify actual fresh-session behavior before claiming that; until then report persisted bytes and runtime behavior unverified. The preference does not connect Arch Studio, grant new authority or override later user instructions.
