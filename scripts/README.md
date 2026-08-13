# Instructor Scripts

This folder will contain small, reusable scripts that support the seminar demonstrations, session preparation, and cross-engine validation. Scripts should be designed as auditable teaching artefacts rather than opaque automation.

## Planned scripts

| Script family | Purpose |
|---|---|
| `session1_*` | Simulate sampling distributions, confidence-interval coverage, bootstrap procedures, and Monte Carlo examples |
| `session2_*` | Produce reproducible examples for comparisons, contingency tables, regression, diagnostics, and sensitivity analysis |
| `session3_*` | Validate Python/R output parity, create analysis provenance summaries, and prepare BYOD teaching materials |
| `validation_*` | Compare fixed datasets and defined parameters across the Python and R engines |

Each script should state its inputs, software requirements, expected outputs, and pedagogical role. Scripts must not contain credentials or make participant data available outside the documented workshop environment.
