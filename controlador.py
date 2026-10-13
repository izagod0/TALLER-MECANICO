from vista.panel_formulario import PanelFormulario
from vista.dialogo_piezas import DialogoPiezas
from permisos import modulos_permitidos, tiene_acceso, normalizar_rol
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

# Texto de cada módulo en el menú
ETIQUETAS_MENU = {
    "Usuarios": "Usuarios",
    "Clientes": "Clientes",
    "Vehiculos": "Vehículos",
    "Reparaciones": "Reparaciones",
    "Piezas": "Piezas",
}


class ControladorPrincipal:
    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        self.usuario_actual = None
        self.mostrar_login()

    def mostrar_login(self):
        self.usuario_actual = None
        self.vista.ocultar_info_usuario()
        self.vista.limpiar_contenido()
        self.vista.ocultar_menu()
        self.vista.crear_panel_login(self.iniciar_sesion)

    def iniciar_sesion(self, username, password):
        usuario = self.modelo.verificar_login(username, password)
        if not usuario:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            return

        self.usuario_actual = usuario
        self.vista.mostrar_menu()
        self.vista.mostrar_info_usuario(usuario["username"], usuario["id"], usuario["tipo"])
        self._vincular_eventos()
        self._mostrar_bienvenida()

    def _mostrar_bienvenida(self):
        self.vista.limpiar_contenido()
        marco = self.vista.frame_contenido
        tipo = self.usuario_actual["tipo"]
        modulos = modulos_permitidos(tipo)

        tk.Label(marco, text="¡Sesión iniciada con éxito!", font=("Arial", 20), bg="white").pack(pady=(50, 10))

        if modulos:
            nombres = ", ".join(ETIQUETAS_MENU[m] for m in modulos)
            tk.Label(marco, text=f"Tu rol ({tipo}) tiene acceso a: {nombres}", font=("Arial", 11), bg="white").pack()
        else:
            tk.Label(marco, text=f"Tu rol ({tipo}) no tiene módulos asignados. Contacta al administrador.",
                     font=("Arial", 11), bg="white", fg="#b71c1c").pack()

        # Aviso de inventario para quien puede ver Piezas
        if tiene_acceso(tipo, "Piezas"):
            bajas = self.modelo.contar_stock_bajo()
            if bajas:
                tk.Label(marco, text=f"⚠ Hay {bajas} pieza(s) con stock igual o menor al mínimo.",
                         font=("Arial", 11, "bold"), bg="white", fg="#b71c1c").pack(pady=15)

    def _vincular_eventos(self):
        """Arma el menú solo con los módulos que el rol puede usar."""
        menu = self.vista.menu_file
        menu.delete(0, tk.END)
        for modulo in modulos_permitidos(self.usuario_actual["tipo"]):
            menu.add_command(label=ETIQUETAS_MENU[modulo], command=lambda m=modulo: self.mostrar_modulo(m))
        menu.add_separator()
        menu.add_command(label="Cerrar sesión", command=self.mostrar_login)
        menu.add_command(label="Salir", command=self.vista.quit)

    def mostrar_modulo(self, entidad):
        # Doble seguro: aunque el menú ya filtra, se vuelve a validar el permiso
        if not self.usuario_actual or not tiene_acceso(self.usuario_actual["tipo"], entidad):
            messagebox.showerror("Acceso denegado", "Tu rol no tiene permiso para entrar a este módulo.")
            return

        self.vista.limpiar_contenido()
        cfg = self.modelo.obtener_config(entidad)
        campos = cfg["campos"]
        columnas_tabla = self.modelo.obtener_columnas_tabla(entidad)

        controlador_form = ControladorFormulario(self.modelo, entidad, self.usuario_actual)
        panel = PanelFormulario(self.vista.frame_contenido, entidad, campos, controlador_form, columnas_tabla, cfg)

        # Llenar las listas desplegables (clientes, vehículos, mecánicos, estados...)
        for campo, fuente in cfg["combos"].items():
            panel.entradas[campo].config(values=self.modelo.obtener_opciones(fuente))

        controlador_form.set_panel(panel)
        panel.pack(fill=tk.BOTH, expand=True)


class ControladorFormulario:
    def __init__(self, modelo, entidad, usuario=None):
        self.panel = None
        self.modelo = modelo
        self.entidad = entidad
        self.usuario = usuario
        self.cfg = modelo.obtener_config(entidad)
        self.id_seleccionado = None

    def set_panel(self, panel):
        self.panel = panel

    # ---------- Utilidades ----------
    def _etiqueta(self, campo):
        texto = self.cfg["etiquetas"].get(campo, self.modelo.nombre_columna(campo))
        return texto.split(" (")[0]

    def _poner_valor(self, campo, valor):
        """Escribe un valor en un campo sin cambiar su estado (normal/readonly/disabled)."""
        entrada = self.panel.entradas[campo]
        estado_previo = str(entrada.cget("state"))
        entrada.config(state="normal")

        if isinstance(entrada, ttk.Combobox):
            texto = valor
            if campo.startswith("cmb") and valor != "":
                opciones = entrada.cget("values")
                if isinstance(opciones, str):
                    opciones = (opciones,)
                # La BD guarda solo el ID; buscamos la opción completa "ID - Nombre"
                for opcion in opciones:
                    if str(opcion).split(" - ")[0] == str(valor):
                        texto = opcion
                        break
            entrada.set(texto)
        else:
            entrada.delete(0, tk.END)
            entrada.insert(0, valor)

        entrada.config(state=estado_previo)

    def _aplicar_defaults(self):
        for campo in self.cfg["campos"]:
            col = self.modelo.nombre_columna(campo)
            if col in self.cfg["defaults"]:
                valor = self.cfg["defaults"][col]
                if valor == "hoy":
                    valor = date.today().isoformat()
                self._poner_valor(campo, valor)

    def _asignar_mecanico_actual(self):
        """Si quien captura es mecánico, la reparación nueva se le asigna por defecto."""
        campo = "cmbmecanico_id"
        if campo in self.panel.entradas and self.usuario and normalizar_rol(self.usuario["tipo"]) == "mecanico":
            self._poner_valor(campo, str(self.usuario["id"]))

    # ---------- Edición ----------
    def cargar_registro_seleccionado(self):
        seleccion = self.panel.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor, selecciona una fila de la tabla primero.")
            return False

        iid = seleccion[0]
        registro = self.modelo.obtener_registro(self.entidad, iid)
        if registro is None:
            messagebox.showwarning("Atención", "No se encontró el registro seleccionado.")
            return False

        self.id_seleccionado = iid
        if self.cfg["modo_id"] == "auto":
            self.panel.mostrar_id(iid)

        for campo in self.cfg["campos"]:
            col = self.modelo.nombre_columna(campo)
            self._poner_valor(campo, registro.get(col, ""))

        return True

    # ---------- Validación ----------
    def _ajustes(self, datos):
        """Reglas propias del módulo antes de validar/guardar."""
        if self.entidad == "Reparaciones":
            if datos.get("cmbEstado") in ("Terminada", "Entregada") and not datos.get("txtFechaSalida"):
                datos["txtFechaSalida"] = date.today().isoformat()

    def _validar(self, datos):
        por_columna = {self.modelo.nombre_columna(k): v for k, v in datos.items()}
        opcionales = set(self.cfg["opcionales"])

        # Campos obligatorios
        for campo, val in datos.items():
            col = self.modelo.nombre_columna(campo)
            if val == "" and col not in opcionales:
                if campo.startswith("cmb"):
                    messagebox.showwarning("Atención", f"Selecciona una opción en: {self._etiqueta(campo)}.")
                else:
                    messagebox.showwarning("Atención", f"El campo {self._etiqueta(campo)} es obligatorio.")
                return False

        # Fechas AAAA-MM-DD
        fechas = {}
        for col in self.cfg["fechas"]:
            val = por_columna.get(col, "")
            if val:
                try:
                    fechas[col] = datetime.strptime(val, "%Y-%m-%d")
                except ValueError:
                    messagebox.showwarning("Atención", f"{col}: la fecha debe tener el formato AAAA-MM-DD (ej. 2026-05-31).")
                    return False

        if "FechaEntrada" in fechas and "FechaSalida" in fechas and fechas["FechaSalida"] < fechas["FechaEntrada"]:
            messagebox.showwarning("Atención", "La fecha de salida no puede ser anterior a la fecha de entrada.")
            return False

        # Números
        for col, tipo in self.cfg["numericos"].items():
            val = por_columna.get(col, "")
            if val == "":
                continue
            try:
                numero = float(val) if tipo == "decimal" else int(val)
            except ValueError:
                esperado = "un número (ej. 150.50)" if tipo == "decimal" else "un número entero"
                messagebox.showwarning("Atención", f"{col} debe ser {esperado}.")
                return False
            if numero < 0:
                messagebox.showwarning("Atención", f"{col} no puede ser negativo.")
                return False

        return True

    # ---------- Acciones de los botones ----------
    def accion(self, estado):
        if not self.panel:
            return

        if estado == "EDITAR":
            if self.cargar_registro_seleccionado():
                self.panel.actualizar_estado("EDITAR")
                # En Vehículos la matrícula es la llave primaria: no se puede cambiar al editar
                if self.cfg["modo_id"] == "campo":
                    for campo in self.cfg["campos"]:
                        if self.modelo.nombre_columna(campo) == self.cfg["pk"]:
                            self.panel.entradas[campo].config(state="readonly")

        elif estado == "SALVAR":
            datos_guardados = {}
            for nombre_campo, caja_texto in self.panel.entradas.items():
                val = caja_texto.get().strip()
                # Si es un combobox con formato "ID - Nombre", extraemos solo el ID
                if nombre_campo.startswith("cmb") and " - " in val:
                    val = val.split(" - ")[0]
                datos_guardados[nombre_campo] = val

            self._ajustes(datos_guardados)
            if not self._validar(datos_guardados):
                return

            if self.id_seleccionado:
                ok = self.modelo.actualizar_datos(self.entidad, self.id_seleccionado, datos_guardados)
            else:
                ok = self.modelo.guardar_datos(self.entidad, datos_guardados)

            if ok:
                self.id_seleccionado = None
                self.panel.actualizar_estado("SALVAR")

        elif estado == "REMOVER":
            seleccion = self.panel.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Atención", "Por favor, selecciona una fila de la tabla primero.")
                return

            id_registro = seleccion[0]
            etiqueta = "matrícula" if self.cfg["modo_id"] == "campo" else "ID"
            aviso = ""
            if self.entidad == "Reparaciones":
                aviso = "\n\nLas piezas usadas en esta reparación regresarán al inventario."
            confirmar = messagebox.askyesno("Confirmar eliminación",
                                            f"¿Estás seguro de eliminar el registro con {etiqueta}: {id_registro}?{aviso}")
            if confirmar:
                if self.modelo.eliminar_datos(self.entidad, id_registro):
                    self.buscar_en_tiempo_real("")
                    self.panel.actualizar_estado("REMOVER")

        elif estado == "PIEZAS":
            seleccion = self.panel.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Atención", "Selecciona primero una reparación de la tabla.")
                return
            ControladorPiezasReparacion(
                self.modelo, self.panel.winfo_toplevel(), seleccion[0],
                al_cerrar=lambda: self.buscar_en_tiempo_real(self.panel.txtBuscador.get()),
            )

        elif estado in ["NUEVO", "CANCELAR"]:
            self.id_seleccionado = None
            self.panel.actualizar_estado(estado)
            if estado == "NUEVO":
                if self.cfg["modo_id"] == "auto":
                    self.panel.mostrar_id(self.modelo.siguiente_id(self.entidad))
                self._aplicar_defaults()
                self._asignar_mecanico_actual()
        else:
            self.panel.actualizar_estado(estado)

    def buscar_en_tiempo_real(self, termino):
        if not self.panel:
            return
        resultados = self.modelo.buscar_datos(self.entidad, termino)
        for row in self.panel.tabla.get_children():
            self.panel.tabla.delete(row)

        # Filas con stock bajo (Piezas): se pintan de rojo
        idx_valor = idx_limite = None
        resaltar = self.cfg["resaltar"]
        if resaltar:
            columnas = self.modelo.obtener_columnas_tabla(self.entidad)
            if resaltar[0] in columnas and resaltar[1] in columnas:
                idx_valor, idx_limite = columnas.index(resaltar[0]), columnas.index(resaltar[1])

        for fila in resultados:
            fila_txt = tuple("" if v is None else str(v) for v in fila)
            etiquetas = ()
            if idx_valor is not None:
                try:
                    if float(fila_txt[idx_valor]) <= float(fila_txt[idx_limite]):
                        etiquetas = ("bajo",)
                except ValueError:
                    pass
            # La primera columna es la llave primaria (id o Matricula): se usa como identificador de la fila
            self.panel.tabla.insert("", tk.END, iid=fila_txt[0], values=fila_txt, tags=etiquetas)


class ControladorPiezasReparacion:
    """Maneja la ventana de piezas usadas en una reparación (descuenta/devuelve stock)."""

    def __init__(self, modelo, parent, id_reparacion, al_cerrar):
        self.modelo = modelo
        self.id_reparacion = id_reparacion
        self.al_cerrar = al_cerrar
        self.dialogo = None

        resumen = modelo.obtener_resumen_reparacion(id_reparacion)
        if resumen is None:
            messagebox.showerror("Error", "No se encontró la reparación.")
            return

        self.dialogo = DialogoPiezas(parent, self, resumen["texto"])
        if resumen["estado"] == "Entregada":
            self.dialogo.bloquear("Reparación entregada: ya no se pueden modificar las piezas.")
        self.refrescar()

    def refrescar(self):
        self.dialogo.cargar_disponibles(self.modelo.obtener_piezas_disponibles())
        self.dialogo.cargar_usadas(self.modelo.obtener_piezas_reparacion(self.id_reparacion))
        mano_obra, total_piezas = self.modelo.obtener_totales_reparacion(self.id_reparacion)
        self.dialogo.mostrar_totales(mano_obra, total_piezas)
        self.dialogo.reiniciar_cantidad()

    def agregar(self):
        elegida = self.dialogo.pieza_elegida()
        if not elegida:
            messagebox.showwarning("Atención", "Selecciona una pieza.", parent=self.dialogo)
            return
        try:
            cantidad = int(self.dialogo.cantidad())
        except ValueError:
            cantidad = 0
        if cantidad <= 0:
            messagebox.showwarning("Atención", "La cantidad debe ser un número entero mayor a 0.", parent=self.dialogo)
            return

        id_pieza = elegida.split(" - ")[0]
        ok, mensaje = self.modelo.agregar_pieza_reparacion(self.id_reparacion, id_pieza, cantidad)
        if ok:
            self.refrescar()
        else:
            messagebox.showwarning("No se pudo agregar", mensaje, parent=self.dialogo)
            self.refrescar()

    def quitar(self):
        id_pieza = self.dialogo.pieza_seleccionada_en_tabla()
        if not id_pieza:
            messagebox.showwarning("Atención", "Selecciona una pieza de la tabla.", parent=self.dialogo)
            return
        if not messagebox.askyesno("Confirmar", "¿Quitar esta pieza de la reparación? Regresará al inventario.",
                                   parent=self.dialogo):
            return
        ok, mensaje = self.modelo.quitar_pieza_reparacion(self.id_reparacion, id_pieza)
        if not ok:
            messagebox.showwarning("No se pudo quitar", mensaje, parent=self.dialogo)
        self.refrescar()

    def cerrar(self):
        self.dialogo.destroy()
        self.al_cerrar()
