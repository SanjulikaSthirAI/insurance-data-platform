select
    claim_id,
    policy_id,
    claim_date,
    claim_amount
from {{ source('public', 'claims') }}
