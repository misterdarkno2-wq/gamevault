-- =====================================================================
-- GameVault - Script SQL (MySQL 8 / MariaDB 10.5+)
-- Ejecutar completo desde DBeaver: Ctrl + Alt + X (Execute script)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS gamevault
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE gamevault;

-- ---------------------------------------------------------------------
-- Tabla principal: videojuegos
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS videojuegos (
    id                INT          NOT NULL AUTO_INCREMENT,
    nombre            VARCHAR(120) NOT NULL,
    descripcion       TEXT         NULL,
    anio_lanzamiento  SMALLINT     NOT NULL,
    desarrollador     VARCHAR(100) NOT NULL,
    plataforma        VARCHAR(50)  NOT NULL,
    genero            VARCHAR(50)  NOT NULL,
    fecha_registro    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_videojuegos_nombre (nombre),
    KEY idx_videojuegos_genero (genero),
    CONSTRAINT ck_videojuegos_anio CHECK (anio_lanzamiento BETWEEN 1970 AND 2100)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Easter eggs de cada videojuego (relación 1:N)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS easter_eggs (
    id              INT          NOT NULL AUTO_INCREMENT,
    id_videojuego   INT          NOT NULL,
    nombre          VARCHAR(120) NOT NULL,
    descripcion     TEXT         NOT NULL,
    dificultad      ENUM('Fácil', 'Media', 'Difícil') NOT NULL DEFAULT 'Media',
    fecha_registro  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_easter_egg (id_videojuego, nombre),
    CONSTRAINT fk_easter_eggs_videojuego
        FOREIGN KEY (id_videojuego) REFERENCES videojuegos (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- Tips / consejos de cada videojuego (relación 1:N)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tips (
    id              INT          NOT NULL AUTO_INCREMENT,
    id_videojuego   INT          NOT NULL,
    titulo          VARCHAR(120) NOT NULL,
    contenido       TEXT         NOT NULL,
    fecha_registro  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_tip (id_videojuego, titulo),
    CONSTRAINT fk_tips_videojuego
        FOREIGN KEY (id_videojuego) REFERENCES videojuegos (id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Migración para instalaciones creadas antes de añadir la descripción.
-- Compatible con MySQL 8 y MariaDB modernos.
ALTER TABLE videojuegos
    ADD COLUMN IF NOT EXISTS descripcion TEXT NULL AFTER nombre;

-- ---------------------------------------------------------------------
-- Vista: videojuegos con el total de easter eggs y tips
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vista_resumen_videojuegos AS
SELECT
    v.id,
    v.nombre,
    v.descripcion,
    v.anio_lanzamiento,
    v.desarrollador,
    v.plataforma,
    v.genero,
    (SELECT COUNT(*) FROM easter_eggs e WHERE e.id_videojuego = v.id) AS total_easter_eggs,
    (SELECT COUNT(*) FROM tips t WHERE t.id_videojuego = v.id)        AS total_tips
FROM videojuegos v;

-- ---------------------------------------------------------------------
-- Datos de ejemplo (se pueden ejecutar varias veces sin duplicar)
-- ---------------------------------------------------------------------
INSERT IGNORE INTO videojuegos (nombre, descripcion, anio_lanzamiento, desarrollador, plataforma, genero) VALUES
('Super Mario 64', 'Primer Mario en 3D, con mundos abiertos dentro de los cuadros del castillo.', 1996, 'Nintendo', 'Nintendo 64', 'Plataformas'),
('Portal', 'Juego de puzles en primera persona basado en portales que conectan dos puntos del espacio.', 2007, 'Valve', 'PC', 'Puzles'),
('Undertale', 'RPG en el que se puede completar la aventura sin derrotar a ningún monstruo.', 2015, 'Toby Fox', 'PC', 'RPG'),
('The Legend of Zelda: Ocarina of Time', 'Aventura en la que Link viaja entre dos épocas de Hyrule.', 1998, 'Nintendo', 'Nintendo 64', 'Aventura');

INSERT IGNORE INTO easter_eggs (id_videojuego, nombre, descripcion, dificultad)
SELECT id, 'Yoshi en el techo del castillo',
       'Al reunir las 120 estrellas, Yoshi espera en el techo del castillo de Peach.', 'Difícil'
FROM videojuegos WHERE nombre = 'Super Mario 64';

INSERT IGNORE INTO easter_eggs (id_videojuego, nombre, descripcion, dificultad)
SELECT id, 'Mensajes ocultos en las paredes',
       'En zonas ocultas de los niveles hay mensajes escritos en las paredes, entre ellos el famoso "the cake is a lie".', 'Media'
FROM videojuegos WHERE nombre = 'Portal';

INSERT IGNORE INTO easter_eggs (id_videojuego, nombre, descripcion, dificultad)
SELECT id, 'Annoying Dog',
       'Un perro blanco aparece en distintos lugares del juego, a veces robando objetos o interrumpiendo escenas.', 'Fácil'
FROM videojuegos WHERE nombre = 'Undertale';

INSERT IGNORE INTO tips (id_videojuego, titulo, contenido)
SELECT id, 'Salto triple',
       'Encadena tres saltos seguidos mientras corres para llegar más alto y más lejos.'
FROM videojuegos WHERE nombre = 'Super Mario 64';

INSERT IGNORE INTO tips (id_videojuego, titulo, contenido)
SELECT id, 'El impulso se conserva',
       'La velocidad con la que entras a un portal se mantiene al salir por el otro. Úsalo para cruzar grandes distancias.'
FROM videojuegos WHERE nombre = 'Portal';

INSERT IGNORE INTO tips (id_videojuego, titulo, contenido)
SELECT id, 'Perdonar a los monstruos',
       'Puedes terminar los combates usando ACT y MERCY para no derrotar a nadie.'
FROM videojuegos WHERE nombre = 'Undertale';

INSERT IGNORE INTO tips (id_videojuego, titulo, contenido)
SELECT id, 'Apuntado con Z',
       'Mantén el botón Z para fijar la vista en un enemigo y esquivar sus ataques con más facilidad.'
FROM videojuegos WHERE nombre = 'The Legend of Zelda: Ocarina of Time';
