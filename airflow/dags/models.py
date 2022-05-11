import uuid

from sqlalchemy import Column, Integer, SmallInteger, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Player(Base):
    __tablename__ = "player"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    player_uuid = Column(String)
    summoner_name = Column(String)
    summoner_level = Column(SmallInteger)
    revision_date = Column(DateTime)


class Match(Base):
    __tablename__ = "match"

    id = Column(String, primary_key=True)

    game_creation_ts = Column(DateTime)
    game_start_ts = Column(DateTime)
    game_end_ts = Column(DateTime)
    game_duration_seconds = Column(SmallInteger)
    game_mode = Column(String)
    game_version = Column(String)

    platform_id = Column(String)


class PlayerMatchStats(Base):
    __tablename__ = "player_match_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    match_id = Column(String, ForeignKey("match.id"))
    player_id = Column(UUID(as_uuid=True))  # as-posted view
    player_uuid = Column(String)  # as-is view
    player_name = Column(String)
    player_level = Column(SmallInteger)

    team = Column(SmallInteger)
    win = Column(Boolean)
    game_was_surrendered = Column(Boolean)

    position = Column(String)
    champion_id = Column(SmallInteger)
    champion_name = Column(String)
    champion_level = Column(SmallInteger)
    champion_exp = Column(Integer)

    kills = Column(SmallInteger)
    assists = Column(SmallInteger)
    deaths = Column(SmallInteger)

    minions_killed = Column(SmallInteger)
    turrets_destroyed = Column(SmallInteger)
    dragon_kills = Column(SmallInteger)
    baron_kills = Column(SmallInteger)

    gold_earned = Column(SmallInteger)
    gold_spent = Column(SmallInteger)
    items_purchased = Column(SmallInteger)

    wards_placed = Column(SmallInteger)
    vision_wards_bought = Column(SmallInteger)
    wards_killed = Column(SmallInteger)
    vision_score = Column(SmallInteger)

    physical_damage_dealt = Column(Integer)
    physical_damage_dealt_to_champs = Column(Integer)
    physical_damage_taken = Column(Integer)
    magic_damage_dealt = Column(Integer)
    magic_damage_dealt_to_champs = Column(Integer)
    magic_damage_taken = Column(Integer)
    true_damage_dealt = Column(Integer)
    true_damage_dealt_to_champs = Column(Integer)
    true_damage_taken = Column(Integer)
    total_damage_dealt = Column(Integer)
    total_damage_dealt_to_champs = Column(Integer)
    total_damage_taken = Column(Integer)

    total_time_played_seconds = Column(SmallInteger)
    total_time_spent_dead = Column(SmallInteger)

if __name__ == "__main__":
    from sqlalchemy import create_engine
    engine = create_engine("postgresql://test:test@localhost/test")
    Base.metadata.create_all(engine)
