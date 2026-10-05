# Module-or-local record routing

This is the shared normative resolver for a capability that can write either an enabled hosted module or an existing local record owner. It defines route selection only. It does not implement a module lookup, connector, service call, permit signer/verifier, module service, local writer, migration or enablement mechanism.

## Required order and pinned authority

Resolve the route before the first durable write and pin it to the request identity through retry and recovery. The host MUST use the actual delivery context, active-firm result and module-state result; a connector listing or available local workspace does not establish either state.

| Condition | Route | Required result |
|---|---|---|
| Plugin-only local delivery for a requested existing local workflow | Local owner | Selecting the requested local skill/save workflow selects local custody by default; apply that owner's existing authorization, record-write contract and readback. |
| Hosted delivery, verified firm, verified module `enabled` | Module | Invoke the exact reviewed stable module tool. Do not write the local counterpart. |
| Hosted delivery, verified module `disabled` | None | Return `MODULE_NOT_ENABLED`. Perform no hosted or local write. |
| A later explicit local selection after the observed `MODULE_NOT_ENABLED` result | Local owner | Start a new routing step and apply the unchanged local contract. This is not connector fallback. |
| Firm or module state missing, ambiguous or unreadable | None | Fail closed with no hosted or local write. Do not treat unavailable as disabled. |
| A pinned module route later fails, including connector, permit, replay, service or readback failure | Pinned module remains authoritative | Stop with explicit pending/failed hosted state. Never report or perform local success. |

Plugin-only local delivery has no hosted authority lookup prerequisite and no extra custody confirmation: asking the local owner to perform a local save selects that existing workflow. Delivery is local only when the installed plugin actually owns the operation; a hosted failure or missing module lookup cannot be relabelled local. For hosted delivery, an explicit local selection means the user requests the local CSV/clip destination after seeing MODULE_NOT_ENABLED; it starts a separately authorized local operation.

Route selection does not cache authorization. Every module invocation remains subject to the accepted current firm/module-state and service-permit contract. The local route remains separately authorized; prior authorization for hosted work does not authorize a local substitute.

## Module-record-write evidence

`module-record-write` requires `connector.invoke`, not `file.write`. The exact target is the canonical module plus stable host-facing tool and destination record identity. Completion requires:

1. the reviewed request supplied to that exact tool;
2. an observed connector result for the same target;
3. reconciliation of retry, idempotency and expected revision under the operation owner; and
4. a fresh read through the module tool of the actual hosted destination or durable operation result.

A tool response without destination readback is unverified. Local bytes, local exports and self-reported success are not hosted readback.

## Non-wire projection boundary

The checked downstream `routeBindingTemplates` are routing metadata only. An object with `kind: non-wire-route-binding-template`, `readyToSign: false`, `pathTemplate`, or no complete signed wire claims MUST NOT be presented, consumed or counted as a T0119 service permit. In particular, `pathTemplate` is not the exact normalized wire claim `path`. This package neither constructs nor verifies permits.

Implementations consume this contract through their actual host and connector boundaries. Route metadata and conformance checks grant no authority and perform no durable record mutation.
