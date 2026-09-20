# Private case context and handoff

The host/adapter supplies the channel, current message, verified account and selected firm binding, authorized case subset, confirmed facts with provenance, actual channel capabilities and pinned Arch Studio/support identities. The model does not infer protected context from an email domain, signed text, subject line, case ID or an old thread. Missing binding means generic guidance plus the application's authenticated account handoff when available. No case search on another person's supplied email.

Use the single configured Norma identity for all users. The adapter maps RFC Message-ID/In-Reply-To/References to candidate cases and retains provider receipt IDs separately. Neither those references nor the sender header alone authorizes a case. Unknown/conflicting references need an unbound inquiry or authenticated clarification, not an automatic merge with the latest case. Recipient selection and current membership revalidation remain application code, including immediately before protected access and delivery.

## Transfer only what is needed

When a user requests a channel handoff, prepare the minimum summary: their question and intended outcome, confirmed facts and corrections, attempted operations with environment/result, release identities, unresolved step, and selected text evidence. Keep user statements distinct from inferred telemetry. Do not attach entire conversations, private project files, credentials or unrelated firm context by default.

Show the selected content when the user has not already authorized that exact subset/destination. Invoke only an actually exposed authenticated handoff operation and retain its receipt. The receiver must bind the same account and firm through its authenticated flow before loading protected content. If the tool or binding is missing, provide the summary for the user to carry across and state that no case was saved, sent or synchronized. A portable summary is not an access token.

General production work requested by email stays a host handoff. A native host can carry out that work through its domain owner under the user's authorization; this support skill does not make all Norma work support-only or grant the managed environment access to it.

## Service adapter responsibilities

Persist messages and confirmed support facts through the private case boundary, serialize case turns, suppress stale responses after newer inbound messages, and use immutable send intents. Do not ask the model to guess whether an uncertain provider send succeeded. The model may propose response text and a relevant next action; it must not set recipients, identity, eligibility, membership, budgets or retention. Outreach is the approved welcome plus at most one eligible 72-hour follow-up; further replies are user-led. Opt-out, resolution and other suppression signals stop proactive outreach through the adapter.

The native support-only entry point is `skill:norma-support` (expected MCP projection `as_norma_support`, to be verified in the built release). Exclude that support activity  from production usage metrics through the runtime classifier. General `skill:norma` and `agent:norma` retain their existing architectural coordination/worker roles. Loading this reference does not implement a classifier or turn mixed project work into support-only activity.
