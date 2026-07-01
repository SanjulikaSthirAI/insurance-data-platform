
  create view "postgres"."public"."stg_claims__dbt_tmp"
    
    
  as (
    select
    claim_id,
    policy_id,
    claim_date,
    claim_amount
from "postgres"."public"."claims"
  );