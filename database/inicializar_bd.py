from pathlib import Path

from database.connection import obtener_conexion


RUTA_SQL = Path(__file__).with_name("gamevault.sql")


def inicializar_base_de_datos():
    script = RUTA_SQL.read_text(encoding="utf-8")
    conexion = obtener_conexion(
        usar_base_de_datos=False,
        multiples_consultas=True,
    )

    try:
        with conexion.cursor() as cursor:
            cursor.execute(script)
            while cursor.nextset():
                pass
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()

