"""Crea la base de datos, las tablas y los datos de ejemplo leyendo gamevault.sql."""
from pathlib import Path

import config
from database.connection import obtener_conexion

RUTA_SQL = Path(__file__).with_name("gamevault.sql")


def _leer_sentencias():
    """Separa el script en sentencias, ignorando comentarios '--'."""
    texto = RUTA_SQL.read_text(encoding="utf-8")
    lineas = [l for l in texto.splitlines() if not l.strip().startswith("--")]
    sentencias = "\n".join(lineas).split(";")
    return [s.strip() for s in sentencias if s.strip()]


def _tiene_columna(cursor, tabla, columna):
    """Indica si una tabla de la base de datos actual contiene una columna."""
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND column_name = %s
        """,
        (tabla, columna),
    )
    return cursor.fetchone() is not None


def _aplicar_migraciones(cursor):
    """Actualiza instalaciones creadas con versiones anteriores del proyecto."""
    # CREATE TABLE IF NOT EXISTS no modifica tablas ya existentes. Se añaden
    # los campos requeridos por la aplicación antes de crear la vista. Los
    # valores por defecto conservan los registros que hubieran sido creados
    # con la versión antigua, que tenía menos columnas.
    columnas_requeridas = {
        "videojuegos": (
            ("descripcion", "TEXT NULL"),
            ("anio_lanzamiento", "SMALLINT NOT NULL DEFAULT 1970"),
            ("desarrollador", "VARCHAR(100) NOT NULL DEFAULT 'Desconocido'"),
            ("plataforma", "VARCHAR(50) NOT NULL DEFAULT 'Sin especificar'"),
            ("genero", "VARCHAR(50) NOT NULL DEFAULT 'Sin especificar'"),
        ),
        "easter_eggs": (
            ("id_videojuego", "INT NULL"),
            ("nombre", "VARCHAR(120) NULL"),
            ("descripcion", "TEXT NULL"),
            ("dificultad", "ENUM('Fácil', 'Media', 'Difícil') NOT NULL DEFAULT 'Media'"),
        ),
        "tips": (
            ("id_videojuego", "INT NULL"),
            ("titulo", "VARCHAR(120) NULL"),
            ("contenido", "TEXT NULL"),
        ),
    }

    for tabla, columnas in columnas_requeridas.items():
        for columna, definicion in columnas:
            if not _tiene_columna(cursor, tabla, columna):
                cursor.execute(
                    f"ALTER TABLE `{tabla}` "
                    f"ADD COLUMN `{columna}` {definicion}"
                )


def inicializar_base_de_datos():
    nombre_bd = config.MYSQL_DATABASE.replace("`", "``")

    # 1) Crear la base de datos (si no existe) usando el nombre del .env
    conexion = obtener_conexion(usar_base_datos=False)
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{nombre_bd}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conexion.commit()
    finally:
        conexion.close()

    # 2) Ejecutar las tablas, migraciones, vista y datos dentro de esa base.
    # La vista se deja para después de las migraciones porque depende de las
    # columnas de videojuegos. Esto permite reparar una instalación antigua.
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sentencias = _leer_sentencias()
            sentencias_tablas = [
                s for s in sentencias if s.upper().startswith("CREATE TABLE")
            ]
            sentencias_vista = [
                s
                for s in sentencias
                if s.upper().startswith("CREATE OR REPLACE VIEW")
            ]
            sentencias_datos = [
                s for s in sentencias if s.upper().startswith("INSERT")
            ]

            for sentencia in sentencias_tablas:
                cursor.execute(sentencia)
            _aplicar_migraciones(cursor)
            for sentencia in sentencias_vista + sentencias_datos:
                cursor.execute(sentencia)
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()
