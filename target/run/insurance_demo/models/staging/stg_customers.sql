
  create view "postgres"."public"."stg_customers__dbt_tmp"
    
    
  as (
    select
    customer_id,
    customer_name,
    city
from "postgres"."public"."customers"
  );