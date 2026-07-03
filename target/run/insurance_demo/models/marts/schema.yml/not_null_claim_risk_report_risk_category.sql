
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select risk_category
from "postgres"."public"."claim_risk_report"
where risk_category is null



  
  
      
    ) dbt_internal_test