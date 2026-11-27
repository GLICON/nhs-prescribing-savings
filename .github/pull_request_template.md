## What does this change?
<!-- One or two sentences. Link the issue it closes, e.g. "Closes #12" -->

## Which layer(s)?
- [ ] Ingestion (Dagster / APIs)
- [ ] Bronze / Silver / Gold (PySpark)
- [ ] Statistics
- [ ] Power BI / Excel
- [ ] Docs / GitHub setup

## Checks
- [ ] `ruff check .` and `ruff format --check .` pass
- [ ] `pytest` passes (new logic has a test)
- [ ] No secrets, tokens or raw NHS data files committed
- [ ] Safety: practice level and above only; no named prescribers
- [ ] Wording: findings described as "unexplained variation", not "bad practice"
