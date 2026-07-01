## Jira Ticket
Resolves [FRAUD-214]

## Description
This PR introduces the automated dbt pipeline for daily auto-insurance claim fraud-risk scoring. The monolithic SQL script has been refactored into a layered dbt architecture.

## Changes Included
- **Staging:** Added 6 new staging models for raw sources (claims, policies, customers, etc.)
- **Intermediate:** Added `int_claims_per_policy` and `int_payments_per_policy` to calculate historical aggregations.
- **Marts:** Added `claim_risk_report` to categorize risk and rank claims.
- **Tests:** Added `schema.yml` enforcing `not_null`, `unique`, and `relationships` constraints.

## Validation
Pipeline passes all local `dbt test` assertions. Ready for automated execution.
