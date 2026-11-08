# Local operations runbook

## Start and stop

Initialize once with `python -m toolkit.bootstrap`. Start the API with the README command.
Stop with Ctrl+C. Restarting preserves the local SQLite data. Stdio MCP is started and
stopped by its client. Separate processes must share TOOLKIT_HOME to see the same database.

## Readiness failure

`/health` checks the process; `/ready` checks the database and presence of configured keys.
If readiness says credentials_required, run bootstrap and restart. If the database is
unavailable, verify the directory and permissions. Never solve this by disabling auth.

## Unauthorized / forbidden

Confirm the key came from this installation's demo-credentials.json and that the server
was restarted after key configuration changed. Use operator to propose and approver to
decide. An approver cannot propose; an operator cannot approve. One identity cannot approve
its own proposal even if it has a second role key.

## Expired or already decided

Inspect the existing approval/ticket. Never retry a new proposal blindly after an uncertain
client response; the original operation may have committed. Proposal creation has no client
idempotency key. Replaying a decision cannot create another ticket. Expired proposals must
be reviewed and re-submitted as new proposals; they are not automatically deleted.

## Database lock or high latency

Read calls retry twice on locked-database errors. Writes return 503 without automatic replay.
Stop long-running manual transactions and extra processes holding locks. Check audit latency,
retry counts and structured stderr. Do not delete WAL files from an active database.

## Rate limit

Wait one minute. Counters are per principal per process. Dashboard refresh sends two calls;
metric totals therefore include dashboard activity. Do not raise limits to hide a tight loop.

## Suspicious document or unsafe request

Retrieved text never grants permissions. Inspect the source document ID and trace, keep
it out of model system instructions, and test the specific client integration. Do not add
an execute-SQL tool, an approval MCP tool or a permission override to “fix” a denied call.

## Audit outage

Successful writes fail closed if their audit insertion fails. Error events may only be
available on stderr during database failure. Restore storage and investigate the trace
before retrying a write. The demo does not provide centralized log durability.

## Backup and reset

Stop all API/MCP writers before copying the complete data directory, including credentials.
Keep backups private. For a fresh demo, use a NEW TOOLKIT_HOME and bootstrap it; retain the
old folder rather than deleting it. Docker uses a distinct named volume.

## Deployment

Python is the locally exercised route. Docker uses a non-root user and binds the host port
to 127.0.0.1. GitHub CI builds and smoke-tests the image. Remote deployment additionally
requires the controls listed in security.md and a deliberate remote MCP authorization design.
