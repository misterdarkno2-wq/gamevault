"""Conexión a MySQL/MariaDB y funciones auxiliares para ejecutar SQL."""
import pymysql
from pymysql.constants import CLIENT
from pymysql.cursors import DictCursor

import config


def obtener_conexion(usar_base_datos=True):
    """Abre una conexión nueva. Las filas se devuelven como diccionarios."""
    parametros = {
        "host": config.MYSQL_HOST,
        "port": config.MYSQL_PORT,
        "user": config.MYSQL_USER,
        "password": config.MYSQL_PASSWORD,
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        # rowcount cuenta las filas encontradas, aunque el UPDATE no cambie nada
        "client_flag": CLIENT.FOUND_ROWS,
        "connect_timeout": 5,
    }
    if usar_base_datos:
        parametros["database"] = config.MYSQL_DATABASE
    return pymysql.connect(**parametros)


def ejecutar_consulta(sql, parametros=None, uno=False):
    """SELECT: devuelve una fila (o None) si uno=True; si no, una tupla de filas."""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, parametros)
            if uno:
                return cursor.fetchone()
            return tuple(cursor.fetchall())
    finally:
        conexion.close()


def ejecutar_comando(sql, parametros=None):
    """INSERT/UPDATE/DELETE: confirma la transacción y devuelve (filas, ultimo_id)."""
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, parametros)
            filas = cursor.rowcount
            ultimo_id = cursor.lastrowid
        conexion.commit()
        return filas, ultimo_id
    except pymysql.MySQLError:
        conexion.rollback()
        raise
    finally:
        conexion.close()
