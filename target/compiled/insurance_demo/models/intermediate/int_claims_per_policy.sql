with claims as (
    select * from "postgres"."public"."stg_claims"
)

select 
    policy_id,
    count(*) as claim_count,
    sum(claim_amount) as total_claim_amount
from claims
where claim_date >= current_date - interval '12 months'
group by policy_id