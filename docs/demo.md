# Two-minute demo

1. Start the app and connect with the operator key. Keep the key file out of recordings.
2. Run Fleet summary. Explain that 24 synthetic vehicles total 25,050 km. Show the trace.
3. Search maintenance. Show POL-001 and the untrusted-reference label.
4. Propose a ticket for EV-006. Explain that no ticket has been created yet.
5. Try approving with the operator identity: the server denies permission.
6. Switch to the separate approver key. Review the exact vehicle, title, body and priority.
7. Approve once. Show the ticket and audit event. A second decision cannot execute it again.
8. In a separate terminal, run `python -m toolkit.demo_client` with an operator key set.
   Show discovery of three tools and a real MCP analytics response.

Use a short screen recording as portfolio evidence. Label all data synthetic. Explain that
these are simulated enterprise integrations, not real maintenance recommendations or
connected ticket systems. The demo is not a hosted public app or proof of production scale.
