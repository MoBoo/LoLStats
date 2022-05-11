import pendulum
import json

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.hooks.base import BaseHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from models import Match, Player, PlayerMatchStats, sessionmaker

from minio import Minio
from minio.error import MinioException

DB_ETL_OBJECT_PATH_VARIABLE = Variable.get("lolstats_db_etl_object_path_variable")
DB_ETL_PLAYER_DATA_VARIABLE = Variable.get("lolstats_db_etl_player_data_variable")
DATABASE_CONN_ID = Variable.get("lolstats_db_conn_id")
MINIO_CONN_ID = Variable.get("lolstats_minio_conn_id")


@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2022, 1, 1, tz="UTC"),
    catchup=False,
    tags=['lolstats'],
)
def lolstats_db_etl():
    @task
    def get_dag_player_conf(**ctx):
        player_data = ctx["dag_run"].conf.get(DB_ETL_PLAYER_DATA_VARIABLE)

        print(player_data)

        return dict(player_data)

    @task
    def get_dag_objects_conf(**ctx):
        object_paths = ctx["dag_run"].conf.get(DB_ETL_OBJECT_PATH_VARIABLE)

        print(object_paths)

        return dict(object_paths)

    @task
    def load_player_data(player_data_dict):
        postgres_hook = PostgresHook(DATABASE_CONN_ID)
        engine = postgres_hook.get_sqlalchemy_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        player_revision_date = pendulum.from_timestamp(player_data_dict.get("revisionDate") / 1000)

        player = Player(
            player_uuid=player_data_dict.get("puuid"),
            summoner_name=player_data_dict.get("name"),
            summoner_level=player_data_dict.get("summonerLevel"),
            revision_date=player_revision_date
        )

        session.add(player)
        session.commit()

        player_data_dict["id"] = str(player.id)
        print(player_data_dict)

        session.close()

        return player_data_dict

    @task
    def load_match_data(object_paths, player_data):
        postgres_hook = PostgresHook(DATABASE_CONN_ID)
        engine = postgres_hook.get_sqlalchemy_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        minio_connection = BaseHook.get_connection(MINIO_CONN_ID)
        bucket_name = Variable.get("lolstats_minio_bucket_name")

        minio_client = Minio(f"{minio_connection.host}:{minio_connection.port}", access_key=minio_connection.login,
                             secret_key=minio_connection.password, secure=False)

        print(object_paths)

        for object_path in object_paths["paths"]:
            res = minio_client.get_object(bucket_name, object_path)
            data_str = res.data.decode()
            match_data = json.loads(data_str)

            match = Match(
                id=match_data["metadata"].get("matchId"),
                game_creation_ts=pendulum.from_timestamp(match_data["info"].get("gameCreation") / 1000),
                game_start_ts=pendulum.from_timestamp(match_data["info"].get("gameStartTimestamp") / 1000),
                game_end_ts=pendulum.from_timestamp(match_data["info"].get("gameEndTimestamp") / 1000),
                game_duration_seconds=match_data["info"].get("gameDuration"),
                game_mode=match_data["info"].get("gameMode"),
                game_version=match_data["info"].get("gameVersion"),
                platform_id=match_data["info"].get("platformId"),
            )

            session.add(match)

            for participant in match_data["info"].get("participants"):
                player_stats = PlayerMatchStats(
                    match_id=match_data["metadata"].get("matchId"),
                    player_id=player_data.get("id") if participant["puuid"] == player_data["puuid"] else None,
                    player_uuid=participant["puuid"],
                    player_name=participant["summonerName"],
                    player_level=participant["summonerLevel"],

                    team=participant["teamId"],
                    win=participant["win"],
                    game_was_surrendered=participant["gameEndedInSurrender"],

                    position=participant["teamPosition"],
                    champion_id=participant["championId"],
                    champion_name=participant["championName"],
                    champion_level=participant["champLevel"],
                    champion_exp=participant["champExperience"],

                    kills=participant["kills"],
                    assists=participant["assists"],
                    deaths=participant["deaths"],

                    minions_killed=participant["totalMinionsKilled"],
                    turrets_destroyed=participant["turretKills"],
                    dragon_kills=participant["dragonKills"],
                    baron_kills=participant["baronKills"],

                    gold_earned=participant["goldEarned"],
                    gold_spent=participant["goldSpent"],
                    items_purchased=participant["itemsPurchased"],

                    wards_placed=participant["wardsPlaced"],
                    vision_wards_bought=participant["visionWardsBoughtInGame"],
                    wards_killed=participant["wardsKilled"],
                    vision_score=participant["visionScore"],

                    physical_damage_dealt=participant["physicalDamageDealt"],
                    physical_damage_dealt_to_champs=participant["physicalDamageDealtToChampions"],
                    physical_damage_taken=participant["physicalDamageTaken"],
                    magic_damage_dealt=participant["magicDamageDealt"],
                    magic_damage_dealt_to_champs=participant["magicDamageDealtToChampions"],
                    magic_damage_taken=participant["magicDamageTaken"],
                    true_damage_dealt=participant["trueDamageDealt"],
                    true_damage_dealt_to_champs=participant["trueDamageDealtToChampions"],
                    true_damage_taken=participant["trueDamageTaken"],
                    total_damage_dealt=participant["totalDamageDealt"],
                    total_damage_dealt_to_champs=participant["totalDamageDealtToChampions"],
                    total_damage_taken=participant["totalDamageTaken"],

                    total_time_played_seconds=participant["timePlayed"],
                    total_time_spent_dead=participant["totalTimeSpentDead"],
                )

                session.add(player_stats)
        session.commit()
        session.close()

    player_data_conf = get_dag_player_conf()
    object_paths = get_dag_objects_conf()
    player_data = load_player_data(player_data_conf)
    load_match_data(object_paths, player_data)


dag = lolstats_db_etl()
