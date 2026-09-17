from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "airflow",
    "retries": 2,                           
    "retry_delay": timedelta(minutes=5),    
}

with DAG(
    dag_id="triplens_countries_pipeline",
    default_args=default_args,
    start_date=datetime(2026, 9, 6),  # noqa: DTZ001
    schedule="@daily",                      
    catchup=False,                          
    tags=["triplens", "countries"],
) as dag:
    extract_task = BashOperator(
        task_id="extract_and_land_minio",
        bash_command="python /usr/local/airflow/extract/fetch_countries.py",
    )

    snowflake_load_task = BashOperator(
        task_id="load_to_snowflake",
        bash_command="python /usr/local/airflow/extract/load_to_snowflake.py"
    )

    build_dbt_models = BashOperator(
        task_id="build_dbt_models",
        bash_command="/usr/local/airflow/dbt_venv/bin/dbt run --project-dir /usr/local/airflow/dbt --profiles-dir /usr/local/airflow/dbt"
    )

    test_dbt_models = BashOperator(
        task_id="test_dbt_models",
        bash_command="/usr/local/airflow/dbt_venv/bin/dbt test --project-dir /usr/local/airflow/dbt --profiles-dir /usr/local/airflow/dbt"
    )

    extract_task >> snowflake_load_task >> build_dbt_models >> test_dbt_models