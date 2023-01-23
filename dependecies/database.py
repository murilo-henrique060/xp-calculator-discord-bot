import mysql.connector
from decouple import config
from mysql.connector import Error

DB_HOST = config("DB_HOST")
DB_USER = config("DB_USER")
DB_PASSWORD = config("DB_PASSWORD")
DB_DATABASE = config("DB_DATABASE")
DB_TABLE = config("DB_TABLE")

def load():
    with mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {DB_TABLE}")
            return cursor.fetchall()

def reset():
    with mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {DB_TABLE}")
            connection.commit()

def insert(guild_id, channel_id):
    with mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO {DB_TABLE} (guild_id, channel_id) VALUES (%s, %s)", (guild_id, channel_id))
            connection.commit()

def delete(guild_id):
    with mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {DB_TABLE} WHERE guild_id = %s", (guild_id,))
            connection.commit()

def update(guild_id, channel_id):
    with mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE {DB_TABLE} SET channel_id = %s WHERE guild_id = %s", (channel_id, guild_id))
            connection.commit()