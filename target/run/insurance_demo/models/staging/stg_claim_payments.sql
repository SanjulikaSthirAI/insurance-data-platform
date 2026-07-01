
  create view "postgres"."public"."stg_claim_payments__dbt_tmp"
    
    
  as (
    select
    payment_id,
    claim_id,
    payment_date,
    payment_amount
from "postgres"."public"."claim_payments"
  );