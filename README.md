# GameVault

Catálogo de videojuegos con sus easter eggs y tips.
Python + Flet (interfaz) · MySQL/MariaDB (base de datos) · DBeaver (administración).

## Puesta en marcha

1. Instalar dependencias (mejor dentro de un entorno virtual):
   `pip install -r requirements.txt`
2. Copiar `.env.example` a `.env` y poner tus datos de MySQL/MariaDB
   (el `.env` no se sube a Git).
3. Crear la base de datos y los datos de ejemplo:
   `python main.py inicializar`
   (o abrir `database/gamevault.sql` en DBeaver y ejecutarlo con Ctrl+Alt+X)
   Este comando también actualiza instalaciones anteriores que no tengan la
   columna `descripcion` y vuelve a crear la vista de resumen.
4. Probar el backend por consola: `python main.py probar`
5. Abrir la aplicación: `python app.py`
   En la primera ejecución Flet puede mostrar un mensaje de preparación;
   espera a que termine antes de cerrar la consola.

## Estructura

```
app.py                     Interfaz Flet (lista, detalle, formularios)
main.py                    Comandos de consola: inicializar | listar | probar
config.py                  Lee el .env
database/connection.py     Conexión PyMySQL y helpers de SQL
database/inicializar_bd.py Ejecuta gamevault.sql
database/gamevault.sql     Script SQL (tablas, vista, datos de ejemplo)
services/                  Lógica CRUD de videojuegos, easter eggs y tips
```

## Modelo de datos

`videojuegos` 1 ──< `easter_eggs`   y   `videojuegos` 1 ──< `tips`
(claves foráneas con ON DELETE CASCADE) + vista `vista_resumen_videojuegos`.
