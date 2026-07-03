with claims as (
    select * from {{ ref('stg_claims') }}
),
claim_payments as (
    select * from {{ ref('stg_claim_payments') }}
)

select 
    c.policy_id,
    sum(cp.payment_amount) as total_claim_payments
from claims c 
join claim_payments cp on cp.claim_id = c.claim_id
where c.claim_date >= current_date - interval '{{ var("report_window_months", 12) }} months'
group by c.policy_id
