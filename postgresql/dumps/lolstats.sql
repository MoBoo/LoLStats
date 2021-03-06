PGDMP                         z            test    13.6 (Debian 13.6-1.pgdg110+1)    13.6     ?           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            ?           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            ?           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            ?           1262    16386    test    DATABASE     X   CREATE DATABASE test WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'en_US.utf8';
    DROP DATABASE test;
                airflow    false            ?           0    0    DATABASE test    ACL     $   GRANT ALL ON DATABASE test TO test;
                   airflow    false    3007            ?            1259    17159    match    TABLE     [  CREATE TABLE public.match (
    id character varying NOT NULL,
    game_creation_ts timestamp without time zone,
    game_start_ts timestamp without time zone,
    game_end_ts timestamp without time zone,
    game_duration_seconds smallint,
    game_mode character varying,
    game_version character varying,
    platform_id character varying
);
    DROP TABLE public.match;
       public         heap    test    false            ?            1259    17151    player    TABLE     ?   CREATE TABLE public.player (
    id uuid NOT NULL,
    player_uuid character varying,
    summoner_name character varying,
    summoner_level smallint,
    revision_date timestamp without time zone
);
    DROP TABLE public.player;
       public         heap    test    false            ?            1259    17167    player_match_stats    TABLE     #  CREATE TABLE public.player_match_stats (
    id uuid NOT NULL,
    match_id character varying,
    player_id uuid,
    player_uuid character varying,
    player_name character varying,
    player_level smallint,
    team smallint,
    win boolean,
    game_was_surrendered boolean,
    "position" character varying,
    champion_id smallint,
    champion_name character varying,
    champion_level smallint,
    champion_exp integer,
    kills smallint,
    assists smallint,
    deaths smallint,
    minions_killed smallint,
    turrets_destroyed smallint,
    dragon_kills smallint,
    baron_kills smallint,
    gold_earned smallint,
    gold_spent smallint,
    items_purchased smallint,
    wards_placed smallint,
    vision_wards_bought smallint,
    wards_killed smallint,
    vision_score smallint,
    physical_damage_dealt integer,
    physical_damage_dealt_to_champs integer,
    physical_damage_taken integer,
    magic_damage_dealt integer,
    magic_damage_dealt_to_champs integer,
    magic_damage_taken integer,
    true_damage_dealt integer,
    true_damage_dealt_to_champs integer,
    true_damage_taken integer,
    total_damage_dealt integer,
    total_damage_dealt_to_champs integer,
    total_damage_taken integer,
    total_time_played_seconds smallint,
    total_time_spent_dead smallint
);
 &   DROP TABLE public.player_match_stats;
       public         heap    test    false            ?          0    17159    match 
   TABLE DATA           ?   COPY public.match (id, game_creation_ts, game_start_ts, game_end_ts, game_duration_seconds, game_mode, game_version, platform_id) FROM stdin;
    public          test    false    201   ?       ?          0    17151    player 
   TABLE DATA           _   COPY public.player (id, player_uuid, summoner_name, summoner_level, revision_date) FROM stdin;
    public          test    false    200   ?       ?          0    17167    player_match_stats 
   TABLE DATA           ?  COPY public.player_match_stats (id, match_id, player_id, player_uuid, player_name, player_level, team, win, game_was_surrendered, "position", champion_id, champion_name, champion_level, champion_exp, kills, assists, deaths, minions_killed, turrets_destroyed, dragon_kills, baron_kills, gold_earned, gold_spent, items_purchased, wards_placed, vision_wards_bought, wards_killed, vision_score, physical_damage_dealt, physical_damage_dealt_to_champs, physical_damage_taken, magic_damage_dealt, magic_damage_dealt_to_champs, magic_damage_taken, true_damage_dealt, true_damage_dealt_to_champs, true_damage_taken, total_damage_dealt, total_damage_dealt_to_champs, total_damage_taken, total_time_played_seconds, total_time_spent_dead) FROM stdin;
    public          test    false    202   ?       1           2606    17166    match match_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.match
    ADD CONSTRAINT match_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.match DROP CONSTRAINT match_pkey;
       public            test    false    201            3           2606    17174 *   player_match_stats player_match_stats_pkey 
   CONSTRAINT     h   ALTER TABLE ONLY public.player_match_stats
    ADD CONSTRAINT player_match_stats_pkey PRIMARY KEY (id);
 T   ALTER TABLE ONLY public.player_match_stats DROP CONSTRAINT player_match_stats_pkey;
       public            test    false    202            /           2606    17158    player player_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.player
    ADD CONSTRAINT player_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.player DROP CONSTRAINT player_pkey;
       public            test    false    200            4           2606    17175 3   player_match_stats player_match_stats_match_id_fkey    FK CONSTRAINT     ?   ALTER TABLE ONLY public.player_match_stats
    ADD CONSTRAINT player_match_stats_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.match(id);
 ]   ALTER TABLE ONLY public.player_match_stats DROP CONSTRAINT player_match_stats_match_id_fkey;
       public          test    false    202    2865    201            ?      x?????? ? ?      ?      x?????? ? ?      ?      x?????? ? ?     