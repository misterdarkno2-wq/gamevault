"""CRUD de videojuegos."""
from database.connection import ejecutar_comando, ejecutar_consulta


def _validar(nombre, anio_lanzamiento, desarrollador, plataforma, genero):
    if not nombre or not nombre.strip():
        raise ValueError("El nombre es obligatorio.")
    if not desarrollador or not desarrollador.strip():
        raise ValueError("El desarrollador es obligatorio.")
    if not plataforma or not plataforma.strip():
        raise ValueError("La plataforma es obligatoria.")
    if not genero or not genero.strip():
        raise ValueError("El género es obligatorio.")
    if not isinstance(anio_lanzamiento, int) or not 1970 <= anio_lanzamiento <= 2100:
        raise ValueError("El año debe ser un número entre 1970 y 2100.")


def listar_videojuegos():
    return ejecutar_consulta(
        "SELECT * FROM vista_resumen_videojuegos ORDER BY nombre"
    )


def buscar_videojuegos(texto):
    patron = f"%{texto.strip()}%"
    return ejecutar_consulta(
        """
        SELECT * FROM vista_resumen_videojuegos
        WHERE nombre LIKE %s OR desarrollador LIKE %s
              OR plataforma LIKE %s OR genero LIKE %s
        ORDER BY nombre
        """,
        (patron, patron, patron, patron),
    )


def obtener_videojuego(id_videojuego):
    return ejecutar_consulta(
        "SELECT * FROM videojuegos WHERE id = %s", (id_videojuego,), uno=True
    )


def agregar_videojuego(
    nombre, descripcion, anio_lanzamiento, desarrollador, plataforma, genero
):
    _validar(nombre, anio_lanzamiento, desarrollador, plataforma, genero)
    _, nuevo_id = ejecutar_comando(
        """
        INSERT INTO videojuegos
            (nombre, descripcion, anio_lanzamiento, desarrollador, plataforma, genero)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            nombre.strip(),
            (descripcion or "").strip() or None,
            anio_lanzamiento,
            desarrollador.strip(),
            plataforma.strip(),
            genero.strip(),
        ),
    )
    return nuevo_id


def actualizar_videojuego(
    id_videojuego,
    nombre,
    descripcion,
    anio_lanzamiento,
    desarrollador,
    plataforma,
    genero,
):
    _validar(nombre, anio_lanzamiento, desarrollador, plataforma, genero)
    filas, _ = ejecutar_comando(
        """
        UPDATE videojuegos
        SET nombre = %s, descripcion = %s, anio_lanzamiento = %s,
            desarrollador = %s, plataforma = %s, genero = %s
        WHERE id = %s
        """,
        (
            nombre.strip(),
            (descripcion or "").strip() or None,
            anio_lanzamiento,
            desarrollador.strip(),
            plataforma.strip(),
            genero.strip(),
            id_videojuego,
        ),
    )
    return filas > 0


def eliminar_videojuego(id_videojuego):
    """Elimina el juego; sus easter eggs y tips se borran en cascada (ON DELETE CASCADE)."""
    filas, _ = ejecutar_comando(
        "DELETE FROM videojuegos WHERE id = %s", (id_videojuego,)
    )
    return filas > 0


def estadisticas():
    return ejecutar_consulta(
        """
        SELECT
            (SELECT COUNT(*) FROM videojuegos) AS videojuegos,
            (SELECT COUNT(*) FROM easter_eggs) AS easter_eggs,
            (SELECT COUNT(*) FROM tips)        AS tips
        """,
        uno=True,
    )
