import pymysql
from pymysql.constants import CLIENT

from config import (
    MYSQL_DATABASE,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
)


def obtener_conexion(usar_base_de_datos=True, multiples_consultas=False):
    opciones = {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": False,
    }

    if usar_base_de_datos:
        opciones["database"] = MYSQL_DATABASE
    if multiples_consultas:
        opciones["client_flag"] = CLIENT.MULTI_STATEMENTS

    return pymysql.connect(**opciones)

