# Tool and API contracts

All service responses contain `trace_id`, `status`, `data`, `error`, `code`, and `synthetic`.
The official MCP SDK also publishes structured output schemas. MCP validation failures
use the SDK's tool error envelope. Domain errors use `ToolResult.status = error`; clients
must check that field, not only MCP's `isError` flag.

## MCP tools

- `fleet_analytics(metric, region)`: metric is `fleet_summary` or `maintenance_by_region`;
  region is All, Austin, Dallas, or Denver. Source is the synthetic `vehicles` table.
- `document_lookup(query, limit)`: 2–200 characters, integer limit 1–5 (default 3).
  Returns id/title/body references and `content_trust=untrusted_reference_only`.
- `propose_ticket(vehicle_id, title, description, priority)`: operator only. Vehicle must
  exist (EV-001 through EV-024), title 5–120 characters, description 10–1000 characters,
  priority normal/urgent. Returns pending approval ID and expiry, never a ticket ID.

Control characters and extra fields are rejected by the domain schemas. The SDK exposes
basic parameter types/enums; the shared service enforces the full length/range contract.

## Human decision

`POST /api/approvals/{id}/decision` with `X-API-Key` for a different approver:

```json
{"decision": "approve"}
```

The transaction verifies existence, requester separation, pending state and expiry, then
creates one local ticket from the exact saved proposal. Rejection creates no ticket.
Replays receive 409; a missing ID receives 404. Approval is deliberately absent from MCP.

## Error semantics

401 invalid/missing key; 403 permission or self-approval; 404 missing entity;
409 expired/already-decided; 422 invalid arguments; 429 per-process identity limit;
503 storage unavailable. HTTP POST bodies above 8 KiB receive 413.

Fixed aggregate queries use parameterized filters. The repeated-alert metric includes
vehicles whose synthetic alert count is at least three. It is a demonstration rule, not
predictive maintenance or a mechanical diagnosis. All distances are km.
