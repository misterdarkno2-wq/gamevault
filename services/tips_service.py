import pymysql

from database.connection import obtener_conexion


def listar_tips(id_videojuego):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, videojuego_id, titulo, contenido
                FROM tips
                WHERE videojuego_id = %s
                ORDER BY titulo
                """,
                (id_videojuego,),
            )
            return cursor.fetchall()
    finally:
        conexion.close()


def registrar_tip(id_videojuego, titulo, contenido):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tips (videojuego_id, titulo, contenido)
                VALUES (%s, %s, %s)
                """,
                (id_videojuego, titulo, contenido),
            )
            nuevo_id = cursor.lastrowid
        conexion.commit()
        return nuevo_id
    except pymysql.MySQLError:
        conexion.rollback()
        raise
    finally:
        conexion.close()

