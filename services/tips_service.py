"""Tips (consejos) asociados a un videojuego."""
from database.connection import ejecutar_comando, ejecutar_consulta


def listar_tips(id_videojuego):
    return ejecutar_consulta(
        "SELECT * FROM tips WHERE id_videojuego = %s ORDER BY id",
        (id_videojuego,),
    )


def registrar_tip(id_videojuego, titulo, contenido):
    if not titulo or not titulo.strip():
        raise ValueError("El título del tip es obligatorio.")
    if not contenido or not contenido.strip():
        raise ValueError("El contenido del tip es obligatorio.")
    _, nuevo_id = ejecutar_comando(
        "INSERT INTO tips (id_videojuego, titulo, contenido) VALUES (%s, %s, %s)",
        (id_videojuego, titulo.strip(), contenido.strip()),
    )
    return nuevo_id


def eliminar_tip(id_tip):
    filas, _ = ejecutar_comando("DELETE FROM tips WHERE id = %s", (id_tip,))
    return filas > 0
