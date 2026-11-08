# Validation report — v0.1.0

Executed locally with Python 3.12 against the packaged code and synthetic fixtures.
This report describes observed checks, not production certification.

| Check | Observed result |
| --- | --- |
| Pytest suite | 31 passed, zero failures |
| Real MCP subprocess | Initialize, discover 3 tools, read analytics, reject invalid metric, propose ticket |
| Independent MCP client demo | Exit 0; 24 vehicles, 25,050 km; structured trace/source response |
| Role and input tests | Invalid keys, role spoofing and arbitrary SQL inputs denied |
| Human decision tests | Separate approver required; exact payload used; reject/expiry enforced |
| Race/replay tests | Two concurrent decisions yield one success and one conflict; one ticket |
| Failure test | Audit insertion failure rolls back ticket and approval transition |
| Reliability tests | Read lock retries bounded; unavailable storage returns 503; rate limit returns 429 |
| Browser workflow | Analytics, policy lookup, proposal, separate approval, tickets, audit all passed |
| Browser rendering | Desktop 1440px and mobile 390px; no horizontal page overflow on mobile |
| Browser errors | No uncaught JavaScript errors observed during the walkthrough |
| Ruff | Lint and formatting checks passed |
| Packaging | Python wheel built successfully; static assets included |
| Dependency consistency | pip check passed |

Evidence: [JUnit](../reports/pytest.xml), [MCP demo transcript](../reports/mcp-demo.txt),
[dashboard](../screenshots/dashboard.png), [approval queue](../screenshots/approval-review.png),
[mobile view](../screenshots/mobile.png).

The screenshots are captures of the running application with generated synthetic data,
not design mockups. Credentials were cleared from the visible input before capture.
Metric counts and latency are from that local session and vary on each run.

One upstream Starlette/AnyIO deprecation warning appeared during testing. It did not fail
any tests. We did not hide the warning or modify upstream packages.

Not executed here: Docker engine build/run, GitHub-hosted workflows, Windows-specific
installation, Python 3.13 execution, external AI-client compatibility beyond the official
SDK client, real enterprise integration, load testing, penetration testing or live LLM
prompt-injection evaluation. These are not implied by the test results. CI defines both
Python versions and a Docker smoke test for execution after upload.

A local security test establishes a specific server-side boundary. It is not proof that
all clients, prompts, dependencies or deployments are secure. See security.md.
