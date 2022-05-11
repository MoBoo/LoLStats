import json
import io
import pendulum
import requests

from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from airflow.models import Variable
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from minio import Minio
from minio.error import MinioException

START_TIME = pendulum.now("UTC").replace(hour=0, minute=0, second=0, microsecond=0).subtract(days=1)
END_TIME = START_TIME.add(hours=23, minutes=59, seconds=59, microseconds=999)
DB_ETL_OBJECT_PATH_VARIABLE = Variable.get("lolstats_db_etl_object_path_variable")
DB_ETL_PLAYER_DATA_VARIABLE = Variable.get("lolstats_db_etl_player_data_variable")
LOLSTATS_DB_ETL_DAG_ID = Variable.get("lolstats_db_etl_dag_id")
RIOT_API_TOKEN_HEADER = "X-Riot-Token"
RIOT_API_CONN_ID = Variable.get("lolstats_riot_api_conn_id")
MINIO_CONN_ID = Variable.get("lolstats_minio_conn_id")


@dag(
    schedule_interval='@daily',
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=['lolstats'],
)
def lolstats_load_api_data():
    @task
    def get_player_data(player):
        connection = BaseHook.get_connection(RIOT_API_CONN_ID)
        summoner_api_base_url = Variable.get("lolstats_summoner_api_base_url")

        request_headers = {
            RIOT_API_TOKEN_HEADER: connection.password
        }

        player_request_url = summoner_api_base_url.format(player=player)
        res = requests.get(player_request_url, headers=request_headers)
        res.raise_for_status()
        player_data = res.json()

        return player_data

    @task
    def get_matches(player_data):
        connection = BaseHook.get_connection(RIOT_API_CONN_ID)
        matches_api_base_url = Variable.get("lolstats_matches_api_base_url")

        request_headers = {
            RIOT_API_TOKEN_HEADER: connection.password
        }

        start = 0
        count = 100
        match_ids = list()
        while True:
            matches_request_url = matches_api_base_url.format(puuid=player_data.get("puuid"),
                                                              startTime=int(START_TIME.timestamp()),
                                                              endTime=int(END_TIME.timestamp()), start=start,
                                                              count=count)
            res = requests.get(matches_request_url, headers=request_headers)
            res.raise_for_status()
            res_match_ids = res.json()
            match_ids.extend(res_match_ids)
            if len(res_match_ids) <= count:
                break
            else:
                start += count

        return match_ids

    @task
    def load_match_details(match_ids, player_data):
        api_connection = BaseHook.get_connection(RIOT_API_CONN_ID)
        minio_connection = BaseHook.get_connection(MINIO_CONN_ID)
        bucket_name = Variable.get("lolstats_minio_bucket_name")
        match_api_base_url = Variable.get("lolstats_match_api_base_url")

        minio_client = Minio(f"{minio_connection.host}:{minio_connection.port}", access_key=minio_connection.login,
                             secret_key=minio_connection.password, secure=False)

        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        request_headers = {
            RIOT_API_TOKEN_HEADER: api_connection.password
        }

        match_data_paths = list()
        for match_id in match_ids:
            match_request_url = match_api_base_url.format(matchId=match_id)
            res = requests.get(match_request_url, headers=request_headers)
            res.raise_for_status()
            data = res.json()

            # upload to minIO
            object_path = f"{player_data.get('puuid')}/{int(START_TIME.timestamp())}/{match_id}.json"
            data_str = json.dumps(data)
            data_length = len(data_str)
            data_bytes = io.BytesIO(bytes(data_str, "utf8"))
            try:
                minio_client.put_object(bucket_name, object_path, data_bytes, data_length,
                                        content_type="application/json")
                match_data_paths.append(object_path)
            except MinioException as err:
                print("Uploading match data for match_id={match_id} failed:", err, "continuing...")
            finally:
                data_bytes.close()

        return {"paths": match_data_paths}

    trigger_dag_task = TriggerDagRunOperator(
        task_id="trigger_other_dag",
        trigger_dag_id=LOLSTATS_DB_ETL_DAG_ID
    )

    players = Variable.get("lolstats_players", deserialize_json=True)
    for player in players:
        player_data_task = get_player_data(player)
        match_ids_task = get_matches(player_data_task)
        match_data_paths_task = load_match_details(match_ids_task, player_data_task)

        # hacky way to pass run config based on current player
        if trigger_dag_task.conf is None:
            ctx = dict()
            ctx[DB_ETL_OBJECT_PATH_VARIABLE] = match_data_paths_task
            ctx[DB_ETL_PLAYER_DATA_VARIABLE] = player_data_task
            trigger_dag_task.conf = ctx
        else:
            trigger_dag_task.conf[DB_ETL_OBJECT_PATH_VARIABLE] = match_data_paths_task
            trigger_dag_task.conf[DB_ETL_PLAYER_DATA_VARIABLE] = player_data_task

        match_data_paths_task >> trigger_dag_task


lolstats_dag = lolstats_load_api_data()
