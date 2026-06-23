import mysql.connector
from mysql.connector import Error
from config import Config

def get_db_connection():
    """Создает соединение с базой данных"""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        return connection
    except Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

def init_db():
    """Инициализация базы данных (если нужно)"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Здесь можно добавить начальные данные или проверить таблицы
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"Найдено таблиц: {len(tables)}")
        
        cursor.close()
        connection.close()
