select
    policy_id,
    customer_id,
    agent_id,
    policy_type_id,
    premium,
    start_date
from {{ source('public', 'policies') }}
