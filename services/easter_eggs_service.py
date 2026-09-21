"""Easter eggs asociados a un videojuego."""
from database.connection import ejecutar_comando, ejecutar_consulta

DIFICULTADES = ("Fácil", "Media", "Difícil")


def listar_easter_eggs(id_videojuego):
    return ejecutar_consulta(
        "SELECT * FROM easter_eggs WHERE id_videojuego = %s ORDER BY id",
        (id_videojuego,),
    )


def registrar_easter_egg(id_videojuego, nombre, descripcion, dificultad):
    if not nombre or not nombre.strip():
        raise ValueError("El nombre del easter egg es obligatorio.")
    if not descripcion or not descripcion.strip():
        raise ValueError("La descripción del easter egg es obligatoria.")
    if dificultad not in DIFICULTADES:
        raise ValueError("La dificultad debe ser Fácil, Media o Difícil.")
    _, nuevo_id = ejecutar_comando(
        """
        INSERT INTO easter_eggs (id_videojuego, nombre, descripcion, dificultad)
        VALUES (%s, %s, %s, %s)
        """,
        (id_videojuego, nombre.strip(), descripcion.strip(), dificultad),
    )
    return nuevo_id


def eliminar_easter_egg(id_easter_egg):
    filas, _ = ejecutar_comando(
        "DELETE FROM easter_eggs WHERE id = %s", (id_easter_egg,)
    )
    return filas > 0
