# Contributing

Use Python 3.12. Install the locked dependencies and editable package using the README.
Run `python -m ruff check .`, `python -m ruff format --check .`, and `python -m pytest -q`.

New tools need typed input/output schemas, explicit role permissions, bounded queries,
and tests for both authorized and denied requests. Write tools must propose immutable
payloads and use the existing human decision boundary. Do not add an MCP approval tool.

Use only synthetic examples. Never commit generated keys, databases, customer records,
or screenshots containing credentials. Explain behavioral changes and test results in PRs.
