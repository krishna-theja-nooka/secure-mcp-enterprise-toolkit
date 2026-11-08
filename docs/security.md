# Security and privacy boundaries

## Roles

| Role | Analytics / documents | Propose ticket | Decide | Approval visibility |
| --- | --- | --- | --- | --- |
| analyst | yes | no | no | own only |
| operator | yes | yes | no | own only |
| approver | yes | no | yes, different requester | all |

All authenticated demo roles can view tickets, metrics and audit events. This is not
row-level tenant isolation. Permissions are enforced in the shared service used by
both REST and MCP. Frontend visibility is not an authorization control.

## Credentials

Bootstrap creates random 256-bit URL-safe keys. Server configuration stores SHA-256
digests mapped to role/identity; constant-time comparison checks the digest. Plaintext
demo keys are saved separately for local onboarding, never shipped in the archive.
The private files are mode 0600 on POSIX; Windows users must protect the project folder
with OS file permissions. `.gitignore` and `.dockerignore` exclude data and environment files.

For rotation, replace the applicable digest in keys.json using a securely generated key,
then restart the API and MCP processes. They read key mappings at startup. Preserve the
principal ID if the same person receives another role/key, so self-approval cannot be
bypassed by merely switching credentials. Do not give an agent an approver key.

## Threats and controls

- SQL injection: enums and bind parameters; no SQL text input.
- Role spoofing: extra input fields forbidden; identity bound to server configuration.
- Prompt injection: document content is data and never dispatched or executed. A malicious
  string in a proposal cannot grant approval. This does not prove any connected LLM is
  immune to misleading document instructions or data exfiltration in its own context.
- Approval tampering: decision accepts only approve/reject; payload is read from storage.
- Replay/races: transaction lock, pending-state check, unique approval-to-ticket constraint.
- XSS: textContent rendering, external script files, restrictive dashboard CSP.
- Browser cross-origin abuse: no permissive CORS, non-cookie key header, localhost host checks.
- Excess input: field bounds, 8 KiB HTTP POST limit; MCP host/process is a trusted boundary.
- Brute-force/DoS: high-entropy keys and per-identity throttling; no comprehensive unauthenticated
  traffic protection. Process-level rate counters reset on restart and are not global.

## Audit and data handling

Audit stores identity, operation, status, code, latency, retries, timestamp and trace ID.
It excludes API keys and tool argument bodies. Proposals and tickets intentionally store
the supplied title and description. Only synthetic text is allowed in this demo; there is
no PII detector, encryption-at-rest layer or automatic retention policy.

Successful mutations require a successful audit insert. Error audit is best effort if
storage itself fails, with an `audit_unavailable` structured stderr event. Framework and
SDK validation errors outside the service are not in the audit table. Local database
owners can modify audit records; do not claim immutable or regulatory-compliant logging.

## Before production

Use managed identity/SSO, per-user MFA for approvals, TLS, centralized secret management,
shared rate limiting, tenant scoping, tamper-evident audit export, backup/retention policies,
network controls and external-provider idempotency. Perform a security review of the actual
client/transport and deployment. This repository is an educational portfolio implementation.
