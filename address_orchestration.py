from airflow.sdk import dag
from airflow.sdk import task
from datetime import timedelta
from datetime import datetime
from airflow.providers.postgres.hooks.postgres import PostgresHook

import requests

@dag(
        dag_id="address_orchestration",
        schedule=timedelta(minutes=3),
        start_date=datetime(2025, 11, 2),
        catchup = False,
        default_args={
            "owner": "Company of Data Engineering",
            "depends_on_past": False,
            "retries": 3,
            "retry_delay": timedelta(seconds=30)
        },
        description="Pipeline for address data ingestion."

)
def address_orchestration():

    @task
    def extract_data_from_randomusers_api():
        response = requests.get("https://randomuser.me/api/?results=100&nat=br")
        status_code = response.status_code

        if status_code == 200:
            return response.json()
        else:
            raise Exception(f"Bad response from API: {status_code}")
        
    @task.branch
    def decides_next_step(extraction_result):
        if extraction_result is None:
            return "stop_execution"
        return "transform_response"
    
    @task
    def stop_execution():
        print("Bad response - Stoping...")
        
    @task
    def transform_response(response_data):
        addresses = []
        for result in response_data["results"]:
            addresses.append((
                result["location"]["state"],
                result["location"]["city"],
                result["location"]["street"]["name"],
                result["location"]["street"]["number"],
                result["location"]["postcode"]
            ))
        return addresses
    
    @task
    def load_batch_into_postgres(addresses_data):
        postgres_hook = PostgresHook(postgres_conn_id="postgres")
        conn = postgres_hook.get_conn()
        cursor = conn.cursor()

        sql_query = """
                    INSERT INTO brazilian_address (estado, cidade, rua, numero_endereco, cep) 
                    VALUES (%s, %s, %s, %s, %s)
                    """ 
        
        cursor.executemany(sql_query, addresses_data)
        conn.commit()
        cursor.close()

    # @task
    # def print_addresses_from_postgres(): 
    #     postgres_hook = PostgresHook(postgres_conn_id="postgres")
    #     conn = postgres_hook.get_conn()
    #     cursor = conn.cursor()

    #     cursor.execute("SELECT id, estado, cidade, rua, numero_endereco, cep FROM brazilian_address;")
    #     rows = cursor.fetchall()

    #     print("Registros na tabela brazilian_address:")
    #     for row in rows:
    #         print(row)

    #     cursor.close()
    #     conn.close()
    # Use this if you want to see the results in the task's LOG.


    
    extraction = extract_data_from_randomusers_api()
    decision = decides_next_step(extraction)
    stop = stop_execution()
    transformation = transform_response(extraction)
    load = load_batch_into_postgres(transformation)
    
    # test = print_addresses_from_postgres() 
    # (Use this if you want to see the results in the task's LOG.)

    extraction >> decision >> [stop, transformation] 
    transformation >> load # >> test # (Use this if you want to see the results in the task's LOG.)

address_orchestration()