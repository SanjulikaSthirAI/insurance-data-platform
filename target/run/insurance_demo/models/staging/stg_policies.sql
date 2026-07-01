
  create view "postgres"."public"."stg_policies__dbt_tmp"
    
    
  as (
    select
    policy_id,
    customer_id,
    agent_id,
    policy_type_id,
    premium,
    start_date
from "postgres"."public"."policies"
  );