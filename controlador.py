# controlador.py
from vista.panel_formulario import PanelFormulario
import tkinter as tk
from tkinter import messagebox

class ControladorPrincipal:
    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista
        self._vincular_eventos()

    def _vincular_eventos(self):
        self.vista.menu_file.add_command(label="Usuarios", command=lambda: self.mostrar_modulo("Usuarios"))
        self.vista.menu_file.add_command(label="Clientes", command=lambda: self.mostrar_modulo("Clientes"))
        self.vista.menu_file.add_command(label="Vehículos", command=lambda: self.mostrar_modulo("Vehiculos"))
        self.vista.menu_file.add_command(label="Reparaciones", command=lambda: self.mostrar_modulo("Reparaciones"))
        self.vista.menu_file.add_command(label="Piezas", command=lambda: self.mostrar_modulo("Piezas"))
        self.vista.menu_file.add_separator()
        self.vista.menu_file.add_command(label="Salir", command=self.vista.quit)

    def mostrar_modulo(self, entidad):
        self.vista.limpiar_contenido()
        campos = self.modelo.obtener_campos(entidad)
        
        controlador_form = ControladorFormulario(self.modelo, entidad)
        panel = PanelFormulario(self.vista.frame_contenido, entidad, campos, controlador_form)
        controlador_form.set_panel(panel)
        panel.pack(fill=tk.BOTH, expand=True)

class ControladorFormulario:
    def __init__(self, modelo, entidad):
        self.panel = None
        self.modelo = modelo
        self.entidad = entidad
        self.id_seleccionado = None

    def set_panel(self, panel):
        self.panel = panel

    def cargar_registro_seleccionado(self):
        """Carga los datos de la fila seleccionada de la tabla en las cajas de texto."""
        seleccion = self.panel.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor, selecciona una fila de la tabla primero.")
            return False
        
        valores = self.panel.tabla.item(seleccion[0], "values")
        if not valores:
            return False

        self.id_seleccionado = valores[0]
        campos = self.modelo.obtener_campos(self.entidad)
        columnas_tabla = [c.replace("txt", "").replace("cmb", "") for c in campos]

        offset = 0 if "ID" in [col.upper() for col in columnas_tabla] else 1

        for idx, nombre_campo in enumerate(campos):
            val_idx = idx if offset == 0 else idx + 1
            val = valores[val_idx] if val_idx < len(valores) else ""
            entrada = self.panel.entradas[nombre_campo]
            
            if hasattr(entrada, "set"):  # Combobox
                entrada.config(state="normal")
                entrada.set(val)
            else:
                entrada.config(state=tk.NORMAL)
                entrada.delete(0, tk.END)
                entrada.insert(0, val)

        return True

    def accion(self, estado):
        if not self.panel: return

        if estado == "EDITAR":
            if self.cargar_registro_seleccionado():
                self.panel.actualizar_estado("EDITAR")

        elif estado == "SALVAR":
            datos_guardados = {}
            for nombre_campo, caja_texto in self.panel.entradas.items():
                datos_guardados[nombre_campo] = caja_texto.get()

            if self.id_seleccionado:
                self.modelo.actualizar_datos(self.entidad, self.id_seleccionado, datos_guardados)
                self.id_seleccionado = None
            else:
                self.modelo.guardar_datos(self.entidad, datos_guardados)

            self.panel.actualizar_estado("SALVAR")

        elif estado == "REMOVER":
            seleccion = self.panel.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Atención", "Por favor, selecciona una fila de la tabla primero.")
                return

            valores = self.panel.tabla.item(seleccion[0], "values")
            id_registro = valores[0]

            confirmar = messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de eliminar el registro con ID: {id_registro}?")
            if confirmar:
                self.modelo.eliminar_datos(self.entidad, id_registro)
                self.buscar_en_tiempo_real("")
                self.panel.actualizar_estado("REMOVER")

        elif estado in ["NUEVO", "CANCELAR"]:
            self.id_seleccionado = None
            self.panel.actualizar_estado(estado)
        else:
            self.panel.actualizar_estado(estado)

    def buscar_en_tiempo_real(self, termino):
        if not self.panel: return
        resultados = self.modelo.buscar_datos(self.entidad, termino)
        for row in self.panel.tabla.get_children():
            self.panel.tabla.delete(row)
        for fila in resultados:
            self.panel.tabla.insert("", tk.END, values=fila)