import pymysql

from database.connection import obtener_conexion


def listar_videojuegos():
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nombre, descripcion, anio_lanzamiento,
                       desarrollador, plataforma, genero
                FROM videojuegos
                ORDER BY nombre
                """
            )
            return cursor.fetchall()
    finally:
        conexion.close()


def obtener_videojuego(id_videojuego):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nombre, descripcion, anio_lanzamiento,
                       desarrollador, plataforma, genero
                FROM videojuegos
                WHERE id = %s
                """,
                (id_videojuego,),
            )
            return cursor.fetchone()
    finally:
        conexion.close()


def agregar_videojuego(
    nombre,
    descripcion,
    anio_lanzamiento,
    desarrollador,
    plataforma,
    genero,
):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO videojuegos
                    (nombre, descripcion, anio_lanzamiento,
                     desarrollador, plataforma, genero)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    nombre,
                    descripcion,
                    anio_lanzamiento,
                    desarrollador,
                    plataforma,
                    genero,
                ),
            )
            nuevo_id = cursor.lastrowid
        conexion.commit()
        return nuevo_id
    except pymysql.MySQLError:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def actualizar_videojuego(
    id_videojuego,
    nombre,
    descripcion,
    anio_lanzamiento,
    desarrollador,
    plataforma,
    genero,
):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                UPDATE videojuegos
                SET nombre = %s,
                    descripcion = %s,
                    anio_lanzamiento = %s,
                    desarrollador = %s,
                    plataforma = %s,
                    genero = %s
                WHERE id = %s
                """,
                (
                    nombre,
                    descripcion,
                    anio_lanzamiento,
                    desarrollador,
                    plataforma,
                    genero,
                    id_videojuego,
                ),
            )
            actualizado = cursor.rowcount > 0
        conexion.commit()
        return actualizado
    except pymysql.MySQLError:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def eliminar_videojuego(id_videojuego):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "DELETE FROM videojuegos WHERE id = %s",
                (id_videojuego,),
            )
            eliminado = cursor.rowcount > 0
        conexion.commit()
        return eliminado
    except pymysql.MySQLError:
        conexion.rollback()
        raise
    finally:
        conexion.close()

