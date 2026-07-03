select
    agent_id,
    agent_name
from {{ source('public', 'agents') }}
