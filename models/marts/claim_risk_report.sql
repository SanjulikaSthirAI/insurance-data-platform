with policies as (
    select * from {{ ref('stg_policies') }}
),
customers as (
    select * from {{ ref('stg_customers') }}
),
agents as (
    select * from {{ ref('stg_agents') }}
),
policy_types as (
    select * from {{ ref('stg_policy_types') }}
),
claims_agg as (
    select * from {{ ref('int_claims_per_policy') }}
),
pay_agg as (
    select * from {{ ref('int_payments_per_policy') }}
),
report as (
    select 
        cu.customer_name,
        cu.city,
        pt.policy_type_name as policy_type,
        ag.agent_name,
        p.premium as total_premium_collected,
        ca.total_claim_amount,
        coalesce(pa.total_claim_payments, 0) as total_claim_payments,
        ca.claim_count,
        round(coalesce(pa.total_claim_payments, 0) * 100.0 / nullif(p.premium, 0), 2) as claim_ratio
    from policies p
    join customers cu on cu.customer_id = p.customer_id
    join agents ag on ag.agent_id = p.agent_id
    join policy_types pt on pt.policy_type_id = p.policy_type_id
    join claims_agg ca on ca.policy_id = p.policy_id
    left join pay_agg pa on pa.policy_id = p.policy_id
    where ca.claim_count >= 2
)

select 
    customer_name,
    city,
    policy_type,
    agent_name,
    total_premium_collected,
    total_claim_amount,
    total_claim_payments,
    claim_ratio,
    case
        when claim_ratio > 80 then 'High Risk'
        when claim_ratio >= 40 then 'Medium Risk'
        else 'Low Risk'
    end as risk_category,
    rank() over(partition by city order by claim_ratio desc) as rank_in_city
from report
order by city, rank_in_city
