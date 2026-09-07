import argparse
from datetime import datetime

import pymysql

from database.connection import obtener_conexion
from database.inicializar_bd import inicializar_base_de_datos
from services.easter_eggs_service import (
    listar_easter_eggs,
    registrar_easter_egg,
)
from services.tips_service import listar_tips, registrar_tip
from services.videojuegos_service import (
    actualizar_videojuego,
    agregar_videojuego,
    eliminar_videojuego,
    listar_videojuegos,
    obtener_videojuego,
)


def comprobar_conexion():
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT VERSION() AS version")
            return cursor.fetchone()["version"]
    finally:
        conexion.close()


def ejecutar_prueba_crud():
    marca = datetime.now().strftime("%Y%m%d%H%M%S%f")
    nombre_prueba = f"Juego de prueba CRUD {marca}"
    id_videojuego = None

    try:
        version = comprobar_conexion()
        juegos_iniciales = listar_videojuegos()
        print(f"Conexión correcta. Servidor: {version}")
        print(f"SELECT: {len(juegos_iniciales)} videojuegos encontrados.")

        id_videojuego = agregar_videojuego(
            nombre_prueba,
            "Registro temporal para probar el backend.",
            2026,
            "Equipo GameVault",
            "PC",
            "Aventura",
        )
        insertado = obtener_videojuego(id_videojuego)
        assert insertado and insertado["nombre"] == nombre_prueba
        print(f"INSERT: videojuego temporal creado con id {id_videojuego}.")

        actualizado = actualizar_videojuego(
            id_videojuego,
            nombre_prueba,
            "Descripción modificada durante la prueba CRUD.",
            2026,
            "Equipo GameVault",
            "PC",
            "Puzles",
        )
        juego_actualizado = obtener_videojuego(id_videojuego)
        assert actualizado and juego_actualizado["genero"] == "Puzles"
        print("UPDATE: el registro temporal fue modificado y comprobado.")

        registrar_easter_egg(
            id_videojuego,
            "Sala secreta de prueba",
            "Registro temporal para comprobar la relación.",
            "Fácil",
        )
        registrar_tip(
            id_videojuego,
            "Consejo de prueba",
            "Guardar la partida antes de explorar.",
        )
        assert len(listar_easter_eggs(id_videojuego)) == 1
        assert len(listar_tips(id_videojuego)) == 1
        print("RELACIONES: easter egg y tip asociados correctamente.")

        assert eliminar_videojuego(id_videojuego)
        assert obtener_videojuego(id_videojuego) is None
        assert listar_easter_eggs(id_videojuego) == ()
        assert listar_tips(id_videojuego) == ()
        id_videojuego = None
        print("DELETE: registro eliminado; relaciones borradas en cascada.")
        print("Todas las pruebas del backend finalizaron correctamente.")
    finally:
        if id_videojuego is not None:
            eliminar_videojuego(id_videojuego)


def mostrar_videojuegos():
    for juego in listar_videojuegos():
        print(
            f"{juego['id']}: {juego['nombre']} "
            f"({juego['plataforma']}, {juego['anio_lanzamiento']})"
        )


def main():
    parser = argparse.ArgumentParser(description="Backend inicial de GameVault")
    parser.add_argument(
        "accion",
        choices=("inicializar", "listar", "probar"),
        help="acción que se desea ejecutar",
    )
    args = parser.parse_args()

    try:
        if args.accion == "inicializar":
            inicializar_base_de_datos()
            print("Base de datos inicializada.")
        elif args.accion == "listar":
            mostrar_videojuegos()
        else:
            ejecutar_prueba_crud()
    except pymysql.MySQLError as error:
        print(f"Error de MySQL: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()

