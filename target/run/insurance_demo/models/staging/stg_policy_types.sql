
  create view "postgres"."public"."stg_policy_types__dbt_tmp"
    
    
  as (
    select
    policy_type_id,
    policy_type_name
from "postgres"."public"."policy_types"
  );