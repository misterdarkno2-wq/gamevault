CREATE DATABASE IF NOT EXISTS gamevault
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE gamevault;

CREATE TABLE IF NOT EXISTS videojuegos (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    descripcion TEXT,
    anio_lanzamiento SMALLINT UNSIGNED NOT NULL,
    desarrollador VARCHAR(120) NOT NULL,
    plataforma VARCHAR(80) NOT NULL,
    genero VARCHAR(80) NOT NULL,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_videojuego_nombre_plataforma UNIQUE (nombre, plataforma)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS easter_eggs (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    videojuego_id INT UNSIGNED NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT NOT NULL,
    dificultad ENUM('Fácil', 'Media', 'Difícil') NOT NULL DEFAULT 'Media',
    CONSTRAINT fk_easter_egg_videojuego
        FOREIGN KEY (videojuego_id) REFERENCES videojuegos(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT uq_easter_egg_videojuego_titulo
        UNIQUE (videojuego_id, titulo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tips (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    videojuego_id INT UNSIGNED NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    contenido TEXT NOT NULL,
    CONSTRAINT fk_tip_videojuego
        FOREIGN KEY (videojuego_id) REFERENCES videojuegos(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT uq_tip_videojuego_titulo
        UNIQUE (videojuego_id, titulo)
) ENGINE=InnoDB;

INSERT IGNORE INTO videojuegos
    (nombre, descripcion, anio_lanzamiento, desarrollador, plataforma, genero)
VALUES
    ('Portal 2', 'Juego de puzles basado en portales y física.', 2011, 'Valve', 'PC', 'Puzles'),
    ('The Legend of Zelda: Breath of the Wild', 'Aventura de mundo abierto en el reino de Hyrule.', 2017, 'Nintendo EPD', 'Nintendo Switch', 'Aventura'),
    ('Stardew Valley', 'Simulador de granja y vida en un pequeño pueblo.', 2016, 'ConcernedApe', 'PC', 'Simulación');

INSERT IGNORE INTO easter_eggs
    (videojuego_id, titulo, descripcion, dificultad)
SELECT id, 'Habitación de Rattmann',
       'Una sala oculta con dibujos y mensajes de Doug Rattmann.', 'Media'
FROM videojuegos
WHERE nombre = 'Portal 2' AND plataforma = 'PC';

INSERT IGNORE INTO easter_eggs
    (videojuego_id, titulo, descripcion, dificultad)
SELECT id, 'Camisa de Nintendo Switch',
       'Link puede encontrar una camiseta con el logotipo de la consola.', 'Fácil'
FROM videojuegos
WHERE nombre = 'The Legend of Zelda: Breath of the Wild'
  AND plataforma = 'Nintendo Switch';

INSERT IGNORE INTO tips (videojuego_id, titulo, contenido)
SELECT id, 'Conserva el impulso',
       'La velocidad al entrar en un portal se conserva al salir del otro.'
FROM videojuegos
WHERE nombre = 'Portal 2' AND plataforma = 'PC';

INSERT IGNORE INTO tips (videojuego_id, titulo, contenido)
SELECT id, 'Revisa la televisión',
       'El pronóstico ayuda a decidir cuándo regar y cuándo conviene explorar la mina.'
FROM videojuegos
WHERE nombre = 'Stardew Valley' AND plataforma = 'PC';

