"""Interfaz gráfica de GameVault hecha con Flet.

Ejecutar:  python app.py      (o)      flet run app.py
Antes hay que tener MySQL/MariaDB encendido y haber ejecutado:
    python main.py inicializar
"""
import flet as ft
import pymysql

from services.easter_eggs_service import (
    DIFICULTADES,
    eliminar_easter_egg,
    listar_easter_eggs,
    registrar_easter_egg,
)
from services.tips_service import eliminar_tip, listar_tips, registrar_tip
from services.videojuegos_service import (
    actualizar_videojuego,
    agregar_videojuego,
    buscar_videojuegos,
    eliminar_videojuego,
    estadisticas,
    listar_videojuegos,
    obtener_videojuego,
)

PLATAFORMAS = [
    "PC",
    "PlayStation 5",
    "PlayStation 4",
    "Xbox Series X/S",
    "Xbox One",
    "Nintendo Switch",
    "Nintendo 64",
    "Móvil",
]
GENEROS = [
    "Acción",
    "Aventura",
    "Plataformas",
    "RPG",
    "Puzles",
    "Estrategia",
    "Deportes",
    "Carreras",
    "Terror",
    "Simulación",
]
COLOR_DIFICULTAD = {
    "Fácil": ft.Colors.GREEN_400,
    "Media": ft.Colors.ORANGE_400,
    "Difícil": ft.Colors.RED_400,
}

# Identidad visual: una paleta de "arcade nocturno" con acentos neón suaves.
FONDO = "#080B18"
SUPERFICIE = "#12182B"
SUPERFICIE_CLARA = "#1A2340"
TEXTO_SECUNDARIO = "#AAB6D3"
VIOLETA = "#8B5CF6"
CIAN = "#22D3EE"


class GameVaultApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.filtro = ""
        self._configurar_pagina()
        self._construir_vista_lista()
        self.contenido = ft.Container(expand=True, padding=24)
        self.page.add(self.contenido)
        self.mostrar_lista()

    # ------------------------------------------------------------------
    # Configuración general
    # ------------------------------------------------------------------
    def _configurar_pagina(self):
        page = self.page
        page.title = "GameVault"
        page.padding = 0
        page.bgcolor = FONDO
        page.theme_mode = ft.ThemeMode.DARK
        page.theme = ft.Theme(color_scheme_seed=ft.Colors.DEEP_PURPLE)
        page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.DEEP_PURPLE)
        page.window.width = 1150
        page.window.height = 760
        page.window.min_width = 800
        page.window.min_height = 560
        page.appbar = ft.AppBar(
            leading=ft.Container(
                width=42,
                height=42,
                border_radius=14,
                gradient=ft.LinearGradient(colors=[VIOLETA, CIAN]),
                alignment=ft.Alignment.CENTER,
                content=ft.Icon(ft.Icons.SPORTS_ESPORTS, color=ft.Colors.WHITE),
            ),
            title=ft.Column(
                spacing=0,
                tight=True,
                controls=[
                    ft.Text("GameVault", weight=ft.FontWeight.BOLD, size=18),
                    ft.Text("TU UNIVERSO GAMER", size=10, color=TEXTO_SECUNDARIO),
                ],
            ),
            center_title=False,
            bgcolor="#10162A",
            toolbar_height=72,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Actualizar biblioteca",
                    on_click=lambda e: self.refrescar_lista(),
                ),
                ft.Container(width=8),
            ],
        )

    def _hero(self):
        """Cabecera con textura de color y una llamada a la acción clara."""
        return ft.Container(
            padding=24,
            border_radius=24,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#4C1D95", "#312E81", "#0E7490"],
            ),
            shadow=ft.BoxShadow(
                blur_radius=28,
                spread_radius=1,
                color=ft.Colors.with_opacity(0.28, VIOLETA),
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=6,
                        tight=True,
                        controls=[
                            ft.Text("GAMEVAULT", size=12, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                "Tu colección merece una\ninterfaz de nivel legendario.",
                                size=27,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                "Explora secretos, consejos y aventuras en un solo lugar.",
                                color="#DDE7FF",
                            ),
                        ],
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            ft.Container(
                                width=78,
                                height=78,
                                border_radius=24,
                                bgcolor=ft.Colors.with_opacity(0.18, ft.Colors.WHITE),
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(ft.Icons.AUTO_AWESOME, size=42, color="#FDE68A"),
                            ),
                            ft.FilledButton(
                                "Añadir juego",
                                icon=ft.Icons.ADD,
                                on_click=lambda e: self.abrir_formulario_videojuego(),
                            ),
                        ],
                    ),
                ],
            ),
        )

    def _aviso(self, texto, error=False):
        self.page.show_dialog(
            ft.SnackBar(
                ft.Text(texto),
                bgcolor=ft.Colors.RED_700 if error else ft.Colors.GREEN_700,
            )
        )

    def _cerrar_dialogo(self, e=None):
        self.page.pop_dialog()

    def _confirmar(self, titulo, mensaje, accion):
        """Muestra un diálogo Sí/No y ejecuta `accion` si se confirma."""

        def aceptar(e):
            self.page.pop_dialog()
            accion()

        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text(titulo),
                content=ft.Text(mensaje),
                actions=[
                    ft.TextButton("Cancelar", on_click=self._cerrar_dialogo),
                    ft.FilledButton(
                        "Eliminar",
                        icon=ft.Icons.DELETE,
                        bgcolor=ft.Colors.RED_700,
                        color=ft.Colors.WHITE,
                        on_click=aceptar,
                    ),
                ],
            )
        )

    # ------------------------------------------------------------------
    # Vista 1: lista de videojuegos (se construye una sola vez)
    # ------------------------------------------------------------------
    def _construir_vista_lista(self):
        self.campo_busqueda = ft.TextField(
            hint_text="Buscar por nombre, desarrollador, plataforma o género",
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
            expand=True,
            border_radius=14,
            filled=True,
            bgcolor=SUPERFICIE,
            border_color=SUPERFICIE_CLARA,
            on_change=self._al_buscar,
        )
        self.fila_estadisticas = ft.Row(spacing=14, wrap=True)
        self.zona_tabla = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

        self.vista_lista = ft.Column(
            expand=True,
            spacing=20,
            controls=[
                self._hero(),
                ft.Row(
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Biblioteca", size=25, weight=ft.FontWeight.BOLD),
                                ft.Text("Elige una aventura y descubre sus secretos.", color=TEXTO_SECUNDARIO),
                            ],
                        ),
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=12, vertical=7),
                            border_radius=20,
                            bgcolor=ft.Colors.with_opacity(0.12, CIAN),
                            content=ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.BOLT, size=16, color=CIAN),
                                    ft.Text("Modo explorador", size=12, color="#C9F8FF"),
                                ],
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                self.fila_estadisticas,
                ft.Container(
                    padding=8,
                    border_radius=18,
                    bgcolor="#0D1325",
                    content=ft.Row(
                        controls=[
                            self.campo_busqueda,
                            ft.IconButton(
                                icon=ft.Icons.REFRESH,
                                tooltip="Actualizar",
                                on_click=lambda e: self.refrescar_lista(),
                            ),
                        ],
                    ),
                ),
                self.zona_tabla,
            ],
        )

    def mostrar_lista(self, e=None):
        self.contenido.content = self.vista_lista
        self.refrescar_lista()

    def _al_buscar(self, e):
        self.filtro = self.campo_busqueda.value or ""
        self.refrescar_lista()

    def _tarjeta_estadistica(self, icono, titulo, valor):
        return ft.Container(
            width=220,
            padding=16,
            border_radius=18,
            bgcolor=SUPERFICIE,
            shadow=ft.BoxShadow(
                blur_radius=16,
                color=ft.Colors.with_opacity(0.18, ft.Colors.BLACK),
            ),
            content=ft.Row(
                spacing=12,
                controls=[
                    ft.Container(
                        width=46,
                        height=46,
                        border_radius=14,
                        gradient=ft.LinearGradient(colors=[VIOLETA, CIAN]),
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(icono, size=24, color=ft.Colors.WHITE),
                    ),
                    ft.Column(
                        spacing=0,
                        controls=[
                            ft.Text(str(valor), size=24, weight=ft.FontWeight.BOLD),
                            ft.Text(titulo.upper(), size=11, color=TEXTO_SECUNDARIO),
                        ],
                    ),
                ],
            ),
        )

    def refrescar_lista(self):
        try:
            juegos = (
                buscar_videojuegos(self.filtro) if self.filtro.strip() else listar_videojuegos()
            )
            totales = estadisticas()
        except pymysql.MySQLError as error:
            self._mostrar_error_conexion(error)
            return

        self.fila_estadisticas.controls = [
            self._tarjeta_estadistica(
                ft.Icons.SPORTS_ESPORTS, "Videojuegos", totales["videojuegos"]
            ),
            self._tarjeta_estadistica(
                ft.Icons.EGG_ALT, "Easter eggs", totales["easter_eggs"]
            ),
            self._tarjeta_estadistica(
                ft.Icons.LIGHTBULB, "Tips", totales["tips"]
            ),
        ]

        if not juegos:
            self.zona_tabla.controls = [
                ft.Container(
                    padding=48,
                    border_radius=22,
                    bgcolor=SUPERFICIE,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            ft.Container(
                                width=72,
                                height=72,
                                border_radius=22,
                                bgcolor=ft.Colors.with_opacity(0.12, CIAN),
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(ft.Icons.SEARCH_OFF, size=38, color=CIAN),
                            ),
                            ft.Text("Aquí todavía no hay partida.", size=19, weight=ft.FontWeight.BOLD),
                            ft.Text("Prueba otro filtro o añade tu primer videojuego.", color=TEXTO_SECUNDARIO),
                        ],
                    ),
                )
            ]
        else:
            self.zona_tabla.controls = [
                ft.Container(
                    padding=12,
                    border_radius=22,
                    bgcolor=SUPERFICIE,
                    shadow=ft.BoxShadow(
                        blur_radius=18,
                        color=ft.Colors.with_opacity(0.22, ft.Colors.BLACK),
                    ),
                    content=ft.Row(
                        [self._crear_tabla(juegos)], scroll=ft.ScrollMode.AUTO
                    ),
                )
            ]
        self.page.update()

    def _crear_tabla(self, juegos):
        filas = []
        for juego in juegos:
            id_juego = juego["id"]
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(juego["nombre"], weight=ft.FontWeight.W_600)),
                        ft.DataCell(ft.Text(juego["plataforma"])),
                        ft.DataCell(ft.Text(juego["genero"])),
                        ft.DataCell(ft.Text(str(juego["anio_lanzamiento"]))),
                        ft.DataCell(ft.Text(str(juego["total_easter_eggs"]))),
                        ft.DataCell(ft.Text(str(juego["total_tips"]))),
                        ft.DataCell(
                            ft.Row(
                                spacing=0,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.VISIBILITY,
                                        tooltip="Ver detalle",
                                        on_click=lambda e, i=id_juego: self.mostrar_detalle(i),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        tooltip="Editar",
                                        on_click=lambda e, i=id_juego: self.abrir_formulario_videojuego(
                                            obtener_videojuego(i)
                                        ),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        icon_color=ft.Colors.RED_400,
                                        tooltip="Eliminar",
                                        on_click=lambda e, j=juego: self._pedir_eliminar_videojuego(j),
                                    ),
                                ],
                            )
                        ),
                    ]
                )
            )
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Plataforma")),
                ft.DataColumn(ft.Text("Género")),
                ft.DataColumn(ft.Text("Año")),
                ft.DataColumn(ft.Text("Easter eggs")),
                ft.DataColumn(ft.Text("Tips")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=filas,
            column_spacing=32,
            heading_row_color=ft.Colors.with_opacity(0.12, VIOLETA),
            heading_row_height=50,
            data_row_min_height=58,
            divider_thickness=0.5,
        )

    def _mostrar_error_conexion(self, error):
        self.fila_estadisticas.controls = []
        self.zona_tabla.controls = [
            ft.Container(
                padding=40,
                border_radius=22,
                bgcolor=SUPERFICIE,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.CLOUD_OFF, size=56, color=ft.Colors.RED_400),
                        ft.Text("No se pudo consultar la base de datos", size=20),
                        ft.Text(str(error), selectable=True),
                        ft.Text(
                            "Revisa que MySQL/MariaDB esté encendido, que el archivo .env "
                            "tenga los datos correctos y que hayas ejecutado "
                            "'python main.py inicializar'."
                        ),
                        ft.FilledButton(
                            "Reintentar",
                            icon=ft.Icons.REFRESH,
                            on_click=lambda e: self.refrescar_lista(),
                        ),
                    ],
                ),
            )
        ]
        self.page.update()

    # ------------------------------------------------------------------
    # Formulario de videojuego (crear / editar)
    # ------------------------------------------------------------------
    @staticmethod
    def _opciones(catalogo, valor_actual):
        """Si el valor guardado no está en el catálogo, se agrega para no perderlo."""
        valores = list(catalogo)
        if valor_actual and valor_actual not in valores:
            valores.append(valor_actual)
        return [ft.DropdownOption(key=v, text=v) for v in valores]

    def abrir_formulario_videojuego(self, videojuego=None):
        editando = videojuego is not None
        datos = videojuego or {}

        nombre = ft.TextField(label="Nombre *", value=datos.get("nombre", ""), max_length=120)
        descripcion = ft.TextField(
            label="Descripción",
            value=datos.get("descripcion") or "",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        anio = ft.TextField(
            label="Año de lanzamiento *",
            value=str(datos.get("anio_lanzamiento", "")),
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        desarrollador = ft.TextField(
            label="Desarrollador *", value=datos.get("desarrollador", ""), max_length=100
        )
        plataforma = ft.Dropdown(
            label="Plataforma *",
            value=datos.get("plataforma"),
            options=self._opciones(PLATAFORMAS, datos.get("plataforma")),
        )
        genero = ft.Dropdown(
            label="Género *",
            value=datos.get("genero"),
            options=self._opciones(GENEROS, datos.get("genero")),
        )
        mensaje_error = ft.Text(color=ft.Colors.RED_400, visible=False)

        def guardar(e):
            for campo in (nombre, anio, desarrollador, plataforma, genero):
                campo.error_text = None
            mensaje_error.visible = False

            hay_errores = False
            if not (nombre.value or "").strip():
                nombre.error_text = "Campo obligatorio"
                hay_errores = True
            if not (desarrollador.value or "").strip():
                desarrollador.error_text = "Campo obligatorio"
                hay_errores = True
            if not plataforma.value:
                plataforma.error_text = "Selecciona una plataforma"
                hay_errores = True
            if not genero.value:
                genero.error_text = "Selecciona un género"
                hay_errores = True
            anio_numero = None
            try:
                anio_numero = int((anio.value or "").strip())
                if not 1970 <= anio_numero <= 2100:
                    raise ValueError
            except ValueError:
                anio.error_text = "Ingresa un año entre 1970 y 2100"
                hay_errores = True

            if hay_errores:
                self.page.update()
                return

            try:
                argumentos = (
                    nombre.value,
                    descripcion.value,
                    anio_numero,
                    desarrollador.value,
                    plataforma.value,
                    genero.value,
                )
                if editando:
                    actualizar_videojuego(datos["id"], *argumentos)
                    texto = "Videojuego actualizado."
                else:
                    agregar_videojuego(*argumentos)
                    texto = "Videojuego agregado."
            except pymysql.err.IntegrityError as error:
                if error.args and error.args[0] == 1062:
                    nombre.error_text = "Ya existe un videojuego con ese nombre"
                else:
                    mensaje_error.value = f"Error de integridad: {error}"
                    mensaje_error.visible = True
                self.page.update()
                return
            except (pymysql.MySQLError, ValueError) as error:
                mensaje_error.value = f"No se pudo guardar: {error}"
                mensaje_error.visible = True
                self.page.update()
                return

            self.page.pop_dialog()
            self._aviso(texto)
            self.refrescar_lista()

        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Editar videojuego" if editando else "Nuevo videojuego"),
                content=ft.Column(
                    width=520,
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        nombre,
                        descripcion,
                        ft.Row([anio, desarrollador], spacing=12),
                        ft.Row([plataforma, genero], spacing=12),
                        mensaje_error,
                    ],
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=self._cerrar_dialogo),
                    ft.FilledButton("Guardar", icon=ft.Icons.SAVE, on_click=guardar),
                ],
            )
        )

    def _pedir_eliminar_videojuego(self, juego):
        def eliminar():
            try:
                eliminar_videojuego(juego["id"])
            except pymysql.MySQLError as error:
                self._aviso(f"No se pudo eliminar: {error}", error=True)
                return
            self._aviso(f"«{juego['nombre']}» eliminado.")
            self.refrescar_lista()

        self._confirmar(
            "Eliminar videojuego",
            f"¿Eliminar «{juego['nombre']}»? Sus easter eggs y tips también se borrarán.",
            eliminar,
        )

    # ------------------------------------------------------------------
    # Vista 2: detalle de un videojuego (easter eggs y tips)
    # ------------------------------------------------------------------
    def mostrar_detalle(self, id_videojuego):
        try:
            juego = obtener_videojuego(id_videojuego)
            eggs = listar_easter_eggs(id_videojuego)
            tips = listar_tips(id_videojuego)
        except pymysql.MySQLError as error:
            self._aviso(f"Error de MySQL: {error}", error=True)
            return
        if juego is None:
            self._aviso("El videojuego ya no existe.", error=True)
            self.mostrar_lista()
            return

        def dato(icono, texto):
            return ft.Container(
                padding=ft.Padding.symmetric(horizontal=10, vertical=7),
                border_radius=12,
                bgcolor=ft.Colors.with_opacity(0.1, CIAN),
                content=ft.Row(
                    spacing=6,
                    tight=True,
                    controls=[
                        ft.Icon(icono, size=16, color=CIAN),
                        ft.Text(texto, size=13),
                    ],
                ),
            )

        encabezado = ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            tooltip="Volver a la lista",
                            on_click=self.mostrar_lista,
                        ),
                        ft.Column(
                            spacing=1,
                            controls=[
                                ft.Text(juego["nombre"], size=27, weight=ft.FontWeight.BOLD),
                                ft.Text("FICHA DEL JUEGO", size=10, color=TEXTO_SECUNDARIO),
                            ],
                        ),
                    ]
                ),
                ft.OutlinedButton(
                    "Editar",
                    icon=ft.Icons.EDIT,
                    on_click=lambda e: self.abrir_formulario_videojuego(juego),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        ficha = ft.Container(
            padding=22,
            border_radius=22,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
                colors=["#1B2450", "#111A33"],
            ),
            shadow=ft.BoxShadow(
                blur_radius=20,
                color=ft.Colors.with_opacity(0.22, ft.Colors.BLACK),
            ),
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Row(
                        wrap=True,
                        spacing=24,
                        controls=[
                            dato(ft.Icons.DEVICES, juego["plataforma"]),
                            dato(ft.Icons.CATEGORY, juego["genero"]),
                            dato(ft.Icons.CALENDAR_MONTH, str(juego["anio_lanzamiento"])),
                            dato(ft.Icons.CODE, juego["desarrollador"]),
                        ],
                    ),
                    ft.Container(
                        padding=14,
                        border_radius=14,
                        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
                        content=ft.Text(juego["descripcion"] or "Sin descripción."),
                    ),
                ],
            ),
        )

        panel_eggs = self._panel(
            "Easter eggs",
            ft.Icons.EGG_ALT,
            [self._tarjeta_easter_egg(e, id_videojuego) for e in eggs],
            "Este juego aún no tiene easter eggs.",
            lambda e: self.abrir_formulario_easter_egg(id_videojuego),
        )
        panel_tips = self._panel(
            "Tips",
            ft.Icons.LIGHTBULB,
            [self._tarjeta_tip(t, id_videojuego) for t in tips],
            "Este juego aún no tiene tips.",
            lambda e: self.abrir_formulario_tip(id_videojuego),
        )

        self.contenido.content = ft.Column(
            expand=True,
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                encabezado,
                ficha,
                ft.ResponsiveRow(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(panel_eggs, col={"xs": 12, "md": 6}),
                        ft.Container(panel_tips, col={"xs": 12, "md": 6}),
                    ],
                ),
            ],
        )
        self.page.update()

    def _panel(self, titulo, icono, tarjetas, texto_vacio, al_agregar):
        return ft.Container(
            padding=16,
            border_radius=20,
            bgcolor=SUPERFICIE,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Container(
                                        width=36,
                                        height=36,
                                        border_radius=12,
                                        gradient=ft.LinearGradient(colors=[VIOLETA, CIAN]),
                                        alignment=ft.Alignment.CENTER,
                                        content=ft.Icon(icono, size=19, color=ft.Colors.WHITE),
                                    ),
                                    ft.Text(titulo, size=20, weight=ft.FontWeight.BOLD),
                                ],
                            ),
                            ft.FilledTonalButton("Agregar", icon=ft.Icons.ADD, on_click=al_agregar),
                        ],
                    ),
                    *(tarjetas or [
                        ft.Container(
                            padding=18,
                            border_radius=14,
                            bgcolor="#0D1325",
                            content=ft.Text(texto_vacio, italic=True, color=TEXTO_SECUNDARIO),
                        )
                    ]),
                ],
            ),
        )

    def _tarjeta_easter_egg(self, egg, id_videojuego):
        return ft.Card(
            elevation=0,
            color="#0D1325",
            content=ft.Container(
                padding=14,
                border_radius=16,
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(egg["nombre"], weight=ft.FontWeight.BOLD, expand=True),
                                ft.Container(
                                    padding=ft.Padding.symmetric(vertical=2, horizontal=10),
                                    border_radius=12,
                                    bgcolor=COLOR_DIFICULTAD.get(egg["dificultad"]),
                                    content=ft.Text(
                                        egg["dificultad"], size=12, color=ft.Colors.BLACK
                                    ),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Eliminar",
                                    on_click=lambda e: self._pedir_eliminar_hijo(
                                        "easter egg", egg["nombre"], eliminar_easter_egg,
                                        egg["id"], id_videojuego,
                                    ),
                                ),
                            ],
                        ),
                        ft.Text(egg["descripcion"]),
                    ],
                ),
            )
        )

    def _tarjeta_tip(self, tip, id_videojuego):
        return ft.Card(
            elevation=0,
            color="#0D1325",
            content=ft.Container(
                padding=14,
                border_radius=16,
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(tip["titulo"], weight=ft.FontWeight.BOLD, expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Eliminar",
                                    on_click=lambda e: self._pedir_eliminar_hijo(
                                        "tip", tip["titulo"], eliminar_tip,
                                        tip["id"], id_videojuego,
                                    ),
                                ),
                            ],
                        ),
                        ft.Text(tip["contenido"]),
                    ],
                ),
            )
        )

    def _pedir_eliminar_hijo(self, tipo, nombre, funcion_eliminar, id_registro, id_videojuego):
        def eliminar():
            try:
                funcion_eliminar(id_registro)
            except pymysql.MySQLError as error:
                self._aviso(f"No se pudo eliminar: {error}", error=True)
                return
            self._aviso(f"{tipo.capitalize()} eliminado.")
            self.mostrar_detalle(id_videojuego)

        self._confirmar(f"Eliminar {tipo}", f"¿Eliminar «{nombre}»?", eliminar)

    # ------------------------------------------------------------------
    # Formularios de easter egg y tip
    # ------------------------------------------------------------------
    def abrir_formulario_easter_egg(self, id_videojuego):
        nombre = ft.TextField(label="Nombre *", max_length=120)
        descripcion = ft.TextField(label="Descripción *", multiline=True, min_lines=3, max_lines=5)
        dificultad = ft.Dropdown(
            label="Dificultad *",
            value="Media",
            options=[ft.DropdownOption(key=d, text=d) for d in DIFICULTADES],
        )
        mensaje_error = ft.Text(color=ft.Colors.RED_400, visible=False)

        def guardar(e):
            nombre.error_text = None
            descripcion.error_text = None
            mensaje_error.visible = False
            hay_errores = False
            if not (nombre.value or "").strip():
                nombre.error_text = "Campo obligatorio"
                hay_errores = True
            if not (descripcion.value or "").strip():
                descripcion.error_text = "Campo obligatorio"
                hay_errores = True
            if hay_errores:
                self.page.update()
                return
            try:
                registrar_easter_egg(id_videojuego, nombre.value, descripcion.value, dificultad.value)
            except pymysql.err.IntegrityError as error:
                if error.args and error.args[0] == 1062:
                    nombre.error_text = "Este juego ya tiene un easter egg con ese nombre"
                else:
                    mensaje_error.value = f"Error de integridad: {error}"
                    mensaje_error.visible = True
                self.page.update()
                return
            except (pymysql.MySQLError, ValueError) as error:
                mensaje_error.value = f"No se pudo guardar: {error}"
                mensaje_error.visible = True
                self.page.update()
                return
            self.page.pop_dialog()
            self._aviso("Easter egg agregado.")
            self.mostrar_detalle(id_videojuego)

        self._dialogo_formulario(
            "Nuevo easter egg", [nombre, descripcion, dificultad, mensaje_error], guardar
        )

    def abrir_formulario_tip(self, id_videojuego):
        titulo = ft.TextField(label="Título *", max_length=120)
        contenido = ft.TextField(label="Contenido *", multiline=True, min_lines=3, max_lines=5)
        mensaje_error = ft.Text(color=ft.Colors.RED_400, visible=False)

        def guardar(e):
            titulo.error_text = None
            contenido.error_text = None
            mensaje_error.visible = False
            hay_errores = False
            if not (titulo.value or "").strip():
                titulo.error_text = "Campo obligatorio"
                hay_errores = True
            if not (contenido.value or "").strip():
                contenido.error_text = "Campo obligatorio"
                hay_errores = True
            if hay_errores:
                self.page.update()
                return
            try:
                registrar_tip(id_videojuego, titulo.value, contenido.value)
            except pymysql.err.IntegrityError as error:
                if error.args and error.args[0] == 1062:
                    titulo.error_text = "Este juego ya tiene un tip con ese título"
                else:
                    mensaje_error.value = f"Error de integridad: {error}"
                    mensaje_error.visible = True
                self.page.update()
                return
            except (pymysql.MySQLError, ValueError) as error:
                mensaje_error.value = f"No se pudo guardar: {error}"
                mensaje_error.visible = True
                self.page.update()
                return
            self.page.pop_dialog()
            self._aviso("Tip agregado.")
            self.mostrar_detalle(id_videojuego)

        self._dialogo_formulario("Nuevo tip", [titulo, contenido, mensaje_error], guardar)

    def _dialogo_formulario(self, titulo, controles, al_guardar):
        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text(titulo),
                content=ft.Column(width=460, tight=True, controls=controles),
                actions=[
                    ft.TextButton("Cancelar", on_click=self._cerrar_dialogo),
                    ft.FilledButton("Guardar", icon=ft.Icons.SAVE, on_click=al_guardar),
                ],
            )
        )


def main(page: ft.Page):
    GameVaultApp(page)


if __name__ == "__main__":
    ft.run(main)
