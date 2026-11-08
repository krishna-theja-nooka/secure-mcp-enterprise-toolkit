# Architecture and decisions

## Business workflow

A fleet analyst needs governed access to vehicle metrics and operational policies.
An operator can recommend an escalation. A reviewer must examine the exact proposal
before it creates a ticket. Agents need reusable tools, not unrestricted SQL or a
credential powerful enough to execute arbitrary write actions.

The seed contains 24 synthetic vehicles across three real city-name labels and four
fictional policy documents. No enterprise accounts, drivers, customers, or external
fleet systems are represented. Tickets and approvals are simulated integration records.

## Components and trust boundaries

- `toolkit.mcp_server`: official SDK handles stdio JSON-RPC, initialization, discovery,
  and input/output schemas. The trusted host supplies a key through its environment.
- `toolkit.api`: dashboard and human decision endpoints, JSON body limit, trusted-host
  checks, no CORS allowance, static CSP, OpenAPI API-key authorization.
- `toolkit.service`: shared identity, role, rate, schema validation and fixed tool logic.
- `toolkit.store`: SQLite schema, seeded fixtures, connections, audit persistence.
- `toolkit/static`: human-readable controls; all dynamic output uses text nodes.

Input and document content cannot supply executable SQL, alter permissions or create
new tools. Approval is not a tool exposed to the AI client. The human channel is a
separate credential boundary, not a guarantee that a human actually possesses the key.

## ADR-001: SQLite and explicit transactions

SQLite keeps the demo portable and inspectable. `BEGIN IMMEDIATE` serializes decisions.
The pending-state check, ticket insert, state transition and audit insert commit together.
A unique approval ID constraint in `tickets` provides a second duplicate-execution guard.
If any insert fails, the whole operation rolls back. No external write provider is called.

Tradeoff: one host, limited write concurrency, no tamper-evident remote audit. A future
real provider needs an outbox/idempotency key and explicit uncertain-outcome recovery.

## ADR-002: stdio MCP and a separate HTTP console

The official SDK provides a real MCP transport instead of relabeling REST as MCP.
Stdio is appropriate for a local portfolio client. We pin SDK 1.26.0 and exercise it
with an actual ClientSession subprocess integration test. The browser uses HTTP, not MCP.

Remote MCP authorization is deliberately out of scope. Do not expose this app publicly
and assume the demo API-key scheme implements MCP OAuth authorization.

## ADR-003: bounded SQL and literal lexical retrieval

Two metric names map to hardcoded aggregate queries. Region is an enum passed as a
bound parameter. Document lookup escapes LIKE wildcard characters and returns at most
five references. This is literal substring retrieval, not semantic search or full RAG.
The client can cite IDs but must not interpret retrieved content as trusted instructions.

## ADR-004: approval before execution

Operators create immutable, one-hour proposals. A distinct approver identity can approve
or reject. No self-approval, post-approval edits, ticket deletion or status reversal API
exists. A previously decided ID always fails closed instead of executing again.

## ADR-005: bounded failure handling

Connection lock waits are 200 ms. Read-only operations retry lock errors twice with
exponential backoff; writes never retry. Latency metrics include retry delays and audit
insertion. All operations returning from the service get a fresh trace ID. Network retry
logic is unnecessary here because enterprise integrations are SQLite simulations.
