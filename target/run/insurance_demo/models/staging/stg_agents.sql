
  create view "postgres"."public"."stg_agents__dbt_tmp"
    
    
  as (
    select
    agent_id,
    agent_name
from "postgres"."public"."agents"
  );