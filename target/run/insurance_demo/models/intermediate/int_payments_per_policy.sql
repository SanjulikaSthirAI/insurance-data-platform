
  create view "postgres"."public"."int_payments_per_policy__dbt_tmp"
    
    
  as (
    with claims as (
    select * from "postgres"."public"."stg_claims"
),
claim_payments as (
    select * from "postgres"."public"."stg_claim_payments"
)

select 
    c.policy_id,
    sum(cp.payment_amount) as total_claim_payments
from claims c 
join claim_payments cp on cp.claim_id = c.claim_id
where c.claim_date >= current_date - interval '12 months'
group by c.policy_id
  );