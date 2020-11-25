""""
Proof of concept: DAG using http operator and integration with Azure.

Note that interaction with API endpoints can also be done using the requests library in a PythonOperator, for more
complex workflows.

We use the postman echo example as a demonstration: https://docs.postman-echo.com/

relevant airflow docs:
- https://airflow.apache.org/docs/stable/_api/airflow/operators/http_operator/index.html
- https://airflow.apache.org/docs/stable/integration.html
"""


from airflow.models import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.utils.dates import days_ago
#from airflow.contrib.hooks.wasb_hook import WasbHook
import logging

# blob_storage = WasbHook(conn_id='cgm-azure-storage')
# blob_connection = blob_storage.get_conn()  # a BlockBlobService object from azure-sdk
# list_all_blobs = blob_connection.list_blobs(
#     container_name='preprocessed',
#     prefix='omdena_datasets/sample_dataset')

default_args = {
    'start_date': days_ago(1)  # otherwise waits until tonight to be scheduled
}

with DAG(
        dag_id='omdena-http-proof-of-concept',
        default_args=default_args,
        schedule_interval=None,
) as dag:

    get_data = SimpleHttpOperator(
        task_id='get-data',
        endpoint='postman-echo.com/get',
        http_conn_id='http_default',
        method='GET',
        data={"foo1": "bar1", "foo2": "bar2"},
        log_response=True,
        xcom_push=True
    )

    post_data = SimpleHttpOperator(
        task_id='post-data',
        endpoint='postman-echo.com/post',
        http_conn_id='http_default',
        method='POST',
        headers={'Content-Type': 'application/json'},
        data="{{ ti.xcom_pull(task_ids='get-data', key='return_value') }}",
        log_response=True
    )

    get_data >> post_data



