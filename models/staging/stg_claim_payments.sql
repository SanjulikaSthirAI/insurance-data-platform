select
    payment_id,
    claim_id,
    payment_date,
    payment_amount
from {{ source('public', 'claim_payments') }}
