import psycopg2
from psycopg2 import Error

def get_cursor():
    try:
        connection = psycopg2.connect(user="user",
									  password="user",
									  host="localhost",
									  port="5432",
									  database="Ufanet_rooms")
        cursor = connection.cursor()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if cursor:
            return cursor