select
    policy_type_id,
    policy_type_name
from {{ source('public', 'policy_types') }}
