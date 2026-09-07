import pymysql

from database.connection import obtener_conexion


def listar_easter_eggs(id_videojuego):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, videojuego_id, titulo, descripcion, dificultad
                FROM easter_eggs
                WHERE videojuego_id = %s
                ORDER BY titulo
                """,
                (id_videojuego,),
            )
            return cursor.fetchall()
    finally:
        conexion.close()


def registrar_easter_egg(
    id_videojuego,
    titulo,
    descripcion,
    dificultad="Media",
):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO easter_eggs
                    (videojuego_id, titulo, descripcion, dificultad)
                VALUES (%s, %s, %s, %s)
                """,
                (id_videojuego, titulo, descripcion, dificultad),
            )
            nuevo_id = cursor.lastrowid
        conexion.commit()
        return nuevo_id
    except pymysql.MySQLError:
        conexion.rollback()
        raise
    finally:
        conexion.close()

