# controlador.py
from vista import PanelFormulario
import tkinter as tk

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

    def set_panel(self, panel):
        self.panel = panel

    def accion(self, estado):
        if self.panel:
            if estado == "SALVAR":
                datos_guardados = {}
                for nombre_campo, caja_texto in self.panel.entradas.items():
                    datos_guardados[nombre_campo] = caja_texto.get()
                
                self.modelo.guardar_datos(self.entidad, datos_guardados)

            self.panel.actualizar_estado(estado)

    def buscar_en_tiempo_real(self, termino):
        """Se activa al escribir en la caja de búsqueda. Pide datos y refresca el Treeview."""
        if not self.panel: return
        
        # 1. Traer resultados de SQL
        resultados = self.modelo.buscar_datos(self.entidad, termino)
        
        # 2. Borrar todos los registros actuales de la tabla visual
        for row in self.panel.tabla.get_children():
            self.panel.tabla.delete(row)
            
        # 3. Insertar los nuevos registros
        for fila in resultados:
            self.panel.tabla.insert("", tk.END, values=fila)